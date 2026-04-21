"""
Assessment management routes.

Handles creating, viewing, editing, and analyzing assessments related to
Sustainable Development Goals (SDGs).
"""

from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify, current_app, json
from flask_login import login_required, current_user
from datetime import datetime
import json
import traceback

# Import models
from app.models.assessment import Assessment, SdgScore
from app.models.project import Project
from app.models.sdg import SdgGoal, SdgQuestion
from app import db

# Import utilities
from app.utils.sdg_data import SDG_TARGETS
from app.utils.db import get_db
from app.services import scoring_service

# Create blueprint
assessments_bp = Blueprint('assessments', __name__, url_prefix='/assessments')


# Helper functions
def map_option_to_direct_score(option):
    """
    Map a string option to a numeric direct_score based on the 7-point scale:
    -3 (canceling), -2 (counteracting), -1 (constraining), 0 (consistent),
    +1 (enabling), +2 (reinforcing), +3 (indivisible)
    """
    # Handle None or empty values
    if option is None or option == '':
        return 0.0
    
    # Handle already numeric values
    try:
        return float(option)
    except (ValueError, TypeError):
        pass
    
    # Map string options to direct_scores (7-point scale)
    option = str(option).lower()
    
    # Mapping based on SDG interaction scale
    if option in ('indivisible', 'indispensable', '+3'):
        return 3.0
    elif option in ('reinforcing', 'very positive', '+2'):
        return 2.0
    elif option in ('enabling', 'positive', '+1'):
        return 1.0
    elif option in ('consistent', 'neutral', '0'):
        return 0.0
    elif option in ('constraining', 'slight negative', '-1'):
        return -1.0
    elif option in ('counteracting', 'negative', '-2'):
        return -2.0
    elif option in ('canceling', 'very negative', '-3'):
        return -3.0
    
    # Alternative 5-point Likert scale mapping
    if option in ('strongly agree', 'excellent', 'very high'):
        return 2.0
    elif option in ('agree', 'good', 'high'):
        return 1.0
    elif option in ('neutral', 'moderate', 'medium'):
        return 0.0
    elif option in ('disagree', 'poor', 'low'):
        return -1.0
    elif option in ('strongly disagree', 'very poor', 'very low'):
        return -2.0
    
    # Yes/No type responses
    elif option in ('yes', 'true', '1', 'y'):
        return 1.0
    elif option in ('no', 'false', '0', 'n'):
        return -1.0
    
    # Default case
    return 0.0


# --- Route handlers ---

@assessments_bp.route('/<int:id>')
@login_required
def show(id):
    """Show assessment details."""
    assessment = db.session.get(Assessment, id)
    if not assessment:
        abort(404)
    
    project = db.session.get(Project, assessment.project_id)
    if not project or project.user_id != current_user.id:
        abort(403)
    
    return render_template('assessments/show.html', assessment=assessment, project=project)


@assessments_bp.route('/projects/<int:project_id>/new', methods=['GET', 'POST'])
@login_required
def new(project_id):
    """Create a new assessment for a project and redirect to the first step."""
    try:
        user_id = getattr(current_user, 'id', None) or session.get('user_id')

        project = db.session.get(Project, project_id)
        if not project or project.user_id != user_id:
            flash('Project not found or you do not have permission to access it', 'danger')
            return redirect(url_for('projects.index'))

        # Create the assessment
        assessment = Assessment(
            project_id=project_id,
            user_id=user_id,
            status='draft',
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.session.add(assessment)
        db.session.commit()

        flash('New assessment started. Complete the questionnaire to evaluate your project.', 'success')

        return redirect(url_for('assessments.questionnaire_step',
                              project_id=project_id,
                              assessment_id=assessment.id,
                              step=1))

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating new assessment: {str(e)}")
        flash('Error starting new assessment. Please try again.', 'danger')
        return redirect(url_for('projects.index'))


@assessments_bp.route('/projects/<int:project_id>/questionnaire/<int:assessment_id>/step/<int:step>', methods=['GET', 'POST'])
@login_required
def questionnaire_step(project_id, assessment_id, step):
    """
    Multi-step SDG questionnaire for assessments.
    Step 1: SDGs 1,2,3,6 | Step 2: SDGs 4,5,8,10 | Step 3: SDGs 7,9,11,12
    Step 4: SDGs 13,14,15 | Step 5: SDGs 16,17
    """
    try:
        user_id = getattr(current_user, 'id', None) or session.get('user_id')
        
        # Step SDG mapping
        step_sdgs = {
            1: [1, 2, 3, 6],
            2: [4, 5, 8, 10],
            3: [7, 9, 11, 12],
            4: [13, 14, 15],
            5: [16, 17]
        }
        
        # Verify project and assessment
        project = db.session.get(Project, project_id)
        assessment = db.session.get(Assessment, assessment_id)
        
        if not project or not assessment or assessment.project_id != project.id:
            flash('Project or assessment not found, or permission denied.', 'danger')
            return redirect(url_for('projects.index'))
        
        # Get SDGs for current step
        sdgs = SdgGoal.query.filter(SdgGoal.number.in_(step_sdgs.get(step, []))).order_by(SdgGoal.number).all()
        
        # Get existing direct_scores
        direct_scores_data = SdgScore.query.filter_by(assessment_id=assessment_id).all()
        direct_scores = {direct_score.sdg_id: direct_score for direct_score in direct_scores_data}
        
        if request.method == 'POST':
            try:
                # Process and save submitted direct_scores
                for sdg in sdgs:
                    direct_score_value = request.form.get(f'direct_score_{sdg.id}')
                    notes = request.form.get(f'notes_{sdg.id}')
                    
                    if direct_score_value:
                        existing = SdgScore.query.filter_by(assessment_id=assessment_id, sdg_id=sdg.id).first()
                        
                        if existing:
                            existing.direct_score = direct_score_value
                            existing.notes = notes
                        else:
                            new_direct_score = SdgScore(
                                assessment_id=assessment_id,
                                sdg_id=sdg.id,
                                direct_score=direct_score_value,
                                notes=notes
                            )
                            db.session.add(new_direct_score)
                
                # Update assessment timestamp
                assessment.updated_at = datetime.now()
                db.session.commit()
                
                flash(f'Step {step} saved successfully!', 'success')
                
                # Redirect to next step or finalize
                if step < 5:
                    return redirect(url_for('assessments.questionnaire_step',
                                           project_id=project_id,
                                           assessment_id=assessment_id,
                                           step=step+1))
                else:
                    return redirect(url_for('assessments.finalize', id=assessment_id))
                    
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"Error saving questionnaire step: {str(e)}")
                flash(f"An error occurred while saving: {str(e)}", 'danger')
        
        # GET method - render the form
        return render_template(
            'questionnaire/assessment.html',
            project=project,
            assessment=assessment,
            assessment_id=assessment_id,
            sdgs=sdgs,
            direct_scores=direct_scores,
            step=step,
            sdg_targets=SDG_TARGETS
        )
    except Exception as e:
        current_app.logger.error(f"Error in questionnaire step: {str(e)}")
        flash(f"An error occurred: {str(e)}", 'danger')
        return redirect(url_for('projects.index'))


@assessments_bp.route('/<int:id>/finalize', methods=['GET', 'POST'])
@login_required
def finalize(id):
    """Finalize an assessment and calculate overall direct_scores."""
    try:
        user_id = getattr(current_user, 'id', None) or session.get('user_id')
        
        assessment = db.session.get(Assessment, id)
        if not assessment:
            flash('Assessment not found', 'danger')
            return redirect(url_for('projects.index'))
        
        project_id = assessment.project_id
        project = db.session.get(Project, project_id)
        
        if not project or project.user_id != user_id:
            flash('You do not have permission to finalize this assessment', 'danger')
            return redirect(url_for('projects.index'))
        
        # Accept GET for redirect compatibility
        if request.method == 'GET':
            return redirect(url_for('assessments.results',
                                   project_id=project_id,
                                   assessment_id=id))
        
        # POST method - calculate direct_scores and update status
        direct_scores = SdgScore.query.filter_by(assessment_id=id).all()
        valid_direct_scores = [float(direct_score.direct_score) for direct_score in direct_scores if direct_score.direct_score is not None]
        
        overall_direct_score = sum(valid_direct_scores) / len(valid_direct_scores) if valid_direct_scores else 0
        
        assessment.status = 'completed'
        assessment.completed_at = datetime.now()
        assessment.overall_direct_score = overall_direct_score
        assessment.updated_at = datetime.now()
        
        db.session.commit()
        
        flash('Assessment has been finalized successfully!', 'success')
        
        # Redirect to the results page
        return redirect(url_for('assessments.results',
                               project_id=project_id,
                               assessment_id=id))
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error finalizing assessment: {str(e)}")
        flash(f"An error occurred: {str(e)}", 'danger')
        return redirect(url_for('projects.index'))


@assessments_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Delete an assessment."""
    assessment = db.session.get(Assessment, id)
    if not assessment:
        abort(404)
    
    project = db.session.get(Project, assessment.project_id)
    if not project or project.user_id != current_user.id:
        abort(403)
    
    # Delete SDG scores and the assessment
    SdgScore.query.filter_by(assessment_id=id).delete()
    db.session.delete(assessment)
    db.session.commit()
    
    flash('Assessment deleted successfully.', 'success')
    return redirect(url_for('projects.show', id=project.id))


@assessments_bp.route('/<int:id>/finalize-api', methods=['POST'])
@login_required
def finalize_assessment(id):
    """
    Finalize an assessment (set status to 'finalized').
    API endpoint for AJAX calls.
    """
    try:
        user_id = getattr(current_user, 'id', None) or session.get('user_id')
        
        assessment = db.session.get(Assessment, id)
        if not assessment:
            return jsonify({'success': False, 'message': 'Assessment not found'}), 404
        
        project = db.session.get(Project, assessment.project_id)
        if not project or project.user_id != user_id:
            return jsonify({'success': False, 'message': 'Permission denied'}), 403
        
        assessment.status = 'finalized'
        assessment.updated_at = datetime.now()
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Assessment finalized successfully'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in finalize API: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@assessments_bp.route('/projects/<int:project_id>/assessments/<int:assessment_id>/results')
@login_required
def results(project_id, assessment_id):
    """Display detailed assessment results with SDG details."""
    try:
        user_id = getattr(current_user, 'id', None) or session.get('user_id')

        assessment = db.session.get(Assessment, assessment_id)
        if not assessment:
            flash('Assessment not found', 'danger')
            return redirect(url_for('projects.index'))

        project = db.session.get(Project, assessment.project_id)
        if not project or project.user_id != user_id:
            flash('You do not have permission to view this assessment', 'danger')
            return redirect(url_for('projects.index'))

        # Fetch scores along with goal details using the ORM relationship
        sdg_scores_orm = SdgScore.query.filter_by(assessment_id=assessment_id)\
                                    .join(SdgGoal)\
                                    .order_by(SdgGoal.number)\
                                    .all()

        # Convert ORM objects to dictionaries suitable for JSON serialization
        sdg_scores_data = []
        for score_obj in sdg_scores_orm:
            goal_obj = score_obj.sdg_goal
            score_dict = {
                'id': score_obj.id,
                'assessment_id': score_obj.assessment_id,
                'sdg_id': score_obj.sdg_id,
                'direct_score': float(score_obj.direct_score) if score_obj.direct_score is not None else 0.0,
                'bonus_score': float(score_obj.bonus_score) if score_obj.bonus_score is not None else 0.0,
                'total_score': float(score_obj.total_score) if score_obj.total_score is not None else 0.0,
                'raw_score': float(score_obj.raw_score) if score_obj.raw_score is not None else 0.0,
                'max_possible': float(score_obj.max_possible) if score_obj.max_possible is not None else 0.0,
                'percentage_score': float(score_obj.percentage_score) if score_obj.percentage_score is not None else 0.0,
                'question_count': int(score_obj.question_count) if score_obj.question_count is not None else 0,
                'response_text': score_obj.response_text or '',
                'notes': score_obj.notes or '',
                'number': goal_obj.number if goal_obj and hasattr(goal_obj, 'number') else None,
                'name': goal_obj.name if goal_obj and hasattr(goal_obj, 'name') else '',
                'color_code': goal_obj.color_code if goal_obj and hasattr(goal_obj, 'color_code') else '',
                'description': goal_obj.description if goal_obj and hasattr(goal_obj, 'description') else ''
            }
            sdg_scores_data.append(score_dict)

        overall_score = getattr(assessment, 'overall_score', None)
        if overall_score is None:
            overall_score = 0.0

        return render_template(
            'questionnaire/results.html',
            assessment=assessment,
            project=project,
            sdg_scores=sdg_scores_data,
            overall_score_display=overall_score
        )
    except Exception as e:
        current_app.logger.error(f"Error in results view: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        flash(f"An error occurred while loading the assessment results: {str(e)}", 'danger')
        return redirect(url_for('projects.show', id=project_id))


@assessments_bp.route('/assessments/<int:assessment_id>/recalculate')
@login_required
def recalculate_direct_scores(assessment_id):
    """Recalculate assessment scores based on all SDG responses using the scoring service."""
    try:
        user_id = getattr(current_user, 'id', None) or session.get('user_id')

        assessment = db.session.get(Assessment, assessment_id)
        if not assessment:
            flash('Assessment not found', 'danger')
            return redirect(url_for('projects.index'))

        project = db.session.get(Project, assessment.project_id)
        if not project or project.user_id != user_id:
            flash('You do not have permission to recalculate this assessment', 'danger')
            return redirect(url_for('projects.index'))

        # --- Call the full scoring service ---
        try:
            current_app.logger.critical("--- CALLING RECALCULATE (ORM version) ---")
            calculated_scores = scoring_service.calculate_sdg_scores(assessment_id)
            current_app.logger.info(f"Scores recalculated (ORM) for assessment {assessment_id}: {calculated_scores}")
            flash('Assessment scores have been recalculated!', 'success')
        except Exception as score_calc_e:
            # db.session.rollback() # Rollback might not be needed if service uses separate conn and commits
            current_app.logger.error(f"Error during score recalculation: {str(score_calc_e)}")
            flash(f"An error occurred during score recalculation: {str(score_calc_e)}", 'danger')
            # Redirect back to project page even if recalculation fails
            return redirect(url_for('projects.show', id=project.id))

        # Redirect back to the project page where the button was clicked
        return redirect(url_for('projects.show', id=project.id))

    except Exception as e:
        # db.session.rollback() # Rollback general errors
        current_app.logger.error(f"Error in recalculate route: {str(e)}")
        flash(f"An error occurred: {str(e)}", 'danger')
        return redirect(url_for('projects.index'))


@assessments_bp.route('/projects/<int:project_id>/questionnaire/<int:assessment_id>/save-draft', methods=['POST'])
@login_required
def save_draft(project_id, assessment_id):
    """Save draft assessment data (receives JSON). Now handles CSRF correctly via header."""
    try:
        # CSRF protection is likely handled globally for POST/AJAX if Flask-WTF is enabled.
        # If not, you might need specific checks here.

        data = request.json  # Expect JSON data
        if not data:
            return jsonify({'success': False, 'message': 'No data received'}), 400

        user_id = getattr(current_user, 'id', None) or session.get('user_id')

        assessment = db.session.get(Assessment, assessment_id)
        # Ensure user owns the assessment
        if not assessment or assessment.user_id != user_id:
            return jsonify({'success': False, 'message': 'Assessment not found or permission denied'}), 404

        # Optionally validate the structure of 'data' here

        assessment.draft_data = json.dumps(data)  # Store as JSON string
        assessment.updated_at = datetime.now()
        db.session.commit()

        return jsonify({'success': True, 'message': 'Draft saved successfully'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error saving draft for assessment {assessment_id}: {str(e)}")
        return jsonify({'success': False, 'message': f'Internal server error: {str(e)}'}), 500


@assessments_bp.route('/projects/<int:project_id>/questionnaire/<int:assessment_id>/load-draft', methods=['GET'])
@login_required
def load_draft(project_id, assessment_id):
    """Load draft assessment data."""
    try:
        user_id = getattr(current_user, 'id', None) or session.get('user_id')

        assessment = db.session.get(Assessment, assessment_id)
        # Ensure user owns the assessment
        if not assessment or assessment.user_id != user_id:
            return jsonify({'success': False, 'message': 'Assessment not found or permission denied'}), 404

        if not assessment.draft_data:  # Check if draft_data exists and is not empty
            return jsonify({'success': False, 'message': 'No draft data found'}), 404

        # Try parsing the JSON data
        try:
            draft_json_data = json.loads(assessment.draft_data)
        except json.JSONDecodeError:
            current_app.logger.error(f"Error decoding draft data for assessment {assessment_id}")
            return jsonify({'success': False, 'message': 'Error loading draft data format'}), 500

        return jsonify({
            'success': True,
            'data': draft_json_data  # Return the parsed JSON object
        })
    except Exception as e:
        current_app.logger.error(f"Error loading draft: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@assessments_bp.route('/projects/<int:project_id>/assessments/<int:assessment_id>/submit', methods=['POST'])
@login_required
def submit_assessment(project_id, assessment_id):
    """Submit a completed assessment, save initial responses, and trigger score calculation."""
    current_app.logger.critical(f"--- ENTERING SUBMIT_ASSESSMENT (AJAX): Project {project_id}, Assessment {assessment_id} ---")
    try:
        user_id = getattr(current_user, 'id', None) or session.get('user_id')
        current_app.logger.info(f"Submit request for project {project_id}, assessment {assessment_id} by user {user_id}")

        # --- Basic Project/Assessment Verification ---
        project = db.session.get(Project, project_id)
        if not project:
            current_app.logger.warning(f"Submit failed: Project {project_id} not found or access denied for user {user_id}")
            # Return JSON error for AJAX
            return jsonify({'success': False, 'message': 'Project not found or permission denied'}), 404

        assessment = db.session.get(Assessment, assessment_id)
        if not assessment or assessment.project_id != project_id:
            current_app.logger.warning(f"Submit failed: Assessment {assessment_id} not found or permission denied for user {user_id}")
            # Return JSON error for AJAX
            return jsonify({'success': False, 'message': 'Assessment not found or does not belong to this project'}), 404

        # --- Process JSON data from AJAX request ---
        current_app.logger.critical("--- ABOUT TO PROCESS JSON DATA ---")
        form_data = request.json # <--- CHANGE HERE: Use request.json
        if not form_data:
             current_app.logger.error("No JSON data received in submit request.")
             return jsonify({'success': False, 'message': 'No data received'}), 400

        current_app.logger.info(f"JSON data received: {form_data}")
        from app.models.response import QuestionResponse
        from datetime import datetime
        from app.services import scoring_service

        # --- Step 1: Clear existing responses ---
        try:
            num_deleted = QuestionResponse.query.filter_by(assessment_id=assessment_id).delete()
            db.session.commit()
            current_app.logger.info(f"Deleted {num_deleted} existing responses for assessment {assessment_id}.")
        except Exception as del_e:
            db.session.rollback()
            current_app.logger.error(f"Error deleting existing responses for assessment {assessment_id}: {str(del_e)}")
            return jsonify({'success': False, 'message': 'Error preparing assessment for new submission.'}), 500

        # --- Step 2: Save new responses from JSON data ---
        responses_to_add = []
        current_app.logger.critical("--- ENTERING JSON DATA LOOP ---")
        for key, value in form_data.items():
            current_app.logger.info(f"Looping: Processing key '{key}' with value '{value}'")
            if key.startswith('q') and key[1:].isdigit():
                current_app.logger.info(f"Key '{key}' matched condition 'qN'.")
                try:
                    question_id = int(key[1:])

                    # Determine response_text based on type (string for radio, list for checkbox)
                    response_text_value = value # Value could be string or list
                    raw_score = 0 # Initialize score

                    # Handle single value (radio) vs list (checkbox)
                    if isinstance(value, list):
                         # For checkboxes, calculate score based on number selected or specific values
                         # Example: Simple count-based score (adjust logic as needed)
                         raw_score = len(value)
                         # Store the list as JSON string or handle appropriately
                         response_text_for_db = json.dumps(value)
                         current_app.logger.info(f"Checkbox q_id {question_id}: values={value}, score={raw_score}")
                    elif isinstance(value, str):
                         # For radio buttons, map the single value
                         raw_score = scoring_service.map_option_to_score(value)
                         response_text_for_db = value
                         current_app.logger.info(f"Radio q_id {question_id}: value='{value}', score={raw_score}")
                    else:
                         current_app.logger.warning(f"Unexpected value type for {key}: {type(value)}. Skipping.")
                         continue

                    new_response = QuestionResponse(
                        assessment_id=assessment_id,
                        question_id=question_id,
                        response_score=raw_score,
                        response_text=response_text_for_db # Use the potentially JSON-stringified value
                    )
                    responses_to_add.append(new_response)
                    current_app.logger.info(f"Added response for q{question_id} to list.")

                except Exception as e:
                    current_app.logger.error(f"Error processing JSON field {key}='{value}': {str(e)}")
            else:
                 current_app.logger.info(f"Key '{key}' did NOT match condition 'qN' or is not relevant form data (e.g., project_id).")

        current_app.logger.critical("--- EXITED JSON DATA LOOP ---")

        if not responses_to_add:
             current_app.logger.warning(f"No QuestionResponse objects created from JSON data for assessment {assessment_id}.")
             # Decide if this is an error - maybe allow submitting empty?
             # return jsonify({'success': False, 'message': 'No valid responses found in submission'}), 400
        else:
            current_app.logger.info(f"Prepared {len(responses_to_add)} QuestionResponse objects to add.")
            try:
                db.session.add_all(responses_to_add)
                db.session.flush()
                db.session.commit()
                current_app.logger.info(f"Successfully committed {len(responses_to_add)} responses for assessment {assessment_id}.")
            except Exception as commit_e:
                db.session.rollback()
                current_app.logger.error(f"Database commit error saving responses for assessment {assessment_id}: {str(commit_e)}")
                return jsonify({'success': False, 'message': 'Error saving assessment responses.'}), 500

        # --- Step 3: Trigger Detailed Score Calculation ---
        current_app.logger.critical("--- CALLING SCORING SERVICE ---")
        try:
            calculated_scores = scoring_service.calculate_sdg_scores(assessment_id)
            current_app.logger.info(f"Scores calculated (ORM) for assessment {assessment_id}: {calculated_scores}")
        except Exception as score_calc_e:
            # Note: Responses are saved, but scores failed. Status remains draft? Or completed with error flag?
            # For now, let's still mark as completed but log the error.
            db.session.rollback() # Rollback potential partial score saves within the service
            current_app.logger.error(f"CRITICAL Error during score calculation: {str(score_calc_e)}")
            # Don't update status if scoring failed critically
            return jsonify({'success': False, 'message': f'Responses saved, but score calculation failed: {str(score_calc_e)}'}), 500

        # --- Step 4: Update Assessment Status ---
        current_app.logger.critical("--- UPDATING ASSESSMENT STATUS ---")
        assessment.status = 'completed'
        assessment.completed_at = datetime.now()
        assessment.updated_at = datetime.now()
        # Optional: Clear draft data if it exists
        assessment.draft_data = None
        db.session.commit()

        current_app.logger.info('Assessment submitted and scores calculated successfully!')
        # Return success for AJAX
        return jsonify({'success': True, 'message': 'Assessment submitted successfully!'})

    except Exception as e:
        db.session.rollback()
        current_app.logger.critical(f"--- UNHANDLED EXCEPTION in submit_assessment (AJAX) ---")
        current_app.logger.error(f"Error in submit_assessment: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({'success': False, 'message': f'An internal error occurred: {str(e)}'}), 500


@assessments_bp.route('/admin/populate-database', methods=['GET', 'POST'])
def admin_populate_database():
    """
    TEMPORARY ADMIN ROUTE: Populate SDG questions and goals.
    Call this route to fix the production database.
    DELETE THIS ROUTE AFTER USE FOR SECURITY!
    """
    try:
        # Check current state
        goal_count = SdgGoal.query.count()
        question_count = SdgQuestion.query.count()
        
        results = {
            'initial_goals': goal_count,
            'initial_questions': question_count,
            'actions_taken': []
        }
        
        # Populate SDG Goals if needed
        if goal_count == 0:
            current_app.logger.info("Populating SDG Goals...")
            
            sdg_goals = [
                {"number": 1, "name": "No Poverty", "description": "End poverty in all its forms everywhere"},
                {"number": 2, "name": "Zero Hunger", "description": "End hunger, achieve food security and improved nutrition and promote sustainable agriculture"},
                {"number": 3, "name": "Good Health and Well-being", "description": "Ensure healthy lives and promote well-being for all at all ages"},
                {"number": 4, "name": "Quality Education", "description": "Ensure inclusive and equitable quality education and promote lifelong learning opportunities for all"},
                {"number": 5, "name": "Gender Equality", "description": "Achieve gender equality and empower all women and girls"},
                {"number": 6, "name": "Clean Water and Sanitation", "description": "Ensure availability and sustainable management of water and sanitation for all"},
                {"number": 7, "name": "Affordable and Clean Energy", "description": "Ensure access to affordable, reliable, sustainable and modern energy for all"},
                {"number": 8, "name": "Decent Work and Economic Growth", "description": "Promote sustained, inclusive and sustainable economic growth, full and productive employment and decent work for all"},
                {"number": 9, "name": "Industry, Innovation and Infrastructure", "description": "Build resilient infrastructure, promote inclusive and sustainable industrialization and foster innovation"},
                {"number": 10, "name": "Reduced Inequalities", "description": "Reduce inequality within and among countries"},
                {"number": 11, "name": "Sustainable Cities and Communities", "description": "Make cities and human settlements inclusive, safe, resilient and sustainable"},
                {"number": 12, "name": "Responsible Consumption and Production", "description": "Ensure sustainable consumption and production patterns"},
                {"number": 13, "name": "Climate Action", "description": "Take urgent action to combat climate change and its impacts"},
                {"number": 14, "name": "Life Below Water", "description": "Conserve and sustainably use the oceans, seas and marine resources for sustainable development"},
                {"number": 15, "name": "Life on Land", "description": "Protect, restore and promote sustainable use of terrestrial ecosystems, sustainably manage forests, combat desertification, and halt and reverse land degradation and halt biodiversity loss"},
                {"number": 16, "name": "Peace, Justice and Strong Institutions", "description": "Promote peaceful and inclusive societies for sustainable development, provide access to justice for all and build effective, accountable and inclusive institutions at all levels"},
                {"number": 17, "name": "Partnerships for the Goals", "description": "Strengthen the means of implementation and revitalize the global partnership for sustainable development"}
            ]
            
            for goal_data in sdg_goals:
                goal = SdgGoal(
                    number=goal_data["number"],
                    name=goal_data["name"],
                    description=goal_data["description"],
                    color_code=f"#sdg{goal_data['number']}"
                )
                db.session.add(goal)
            
            db.session.commit()
            results['actions_taken'].append(f"Added {len(sdg_goals)} SDG Goals")
        else:
            results['actions_taken'].append("SDG Goals already exist")
        
        # Populate SDG Questions if needed
        if question_count == 0:
            current_app.logger.info("Populating SDG Questions...")
            
            sdg_goals = SdgGoal.query.all()
            question_id = 1
            
            for goal in sdg_goals:
                # Create 2 questions per SDG (adjust as needed)
                for i in range(2):
                    question_type = 'radio' if i % 2 == 0 else 'checkbox'
                    question_text = f"How does your project contribute to {goal.name}? (Question {i+1})"
                    
                    question = SdgQuestion(
                        id=question_id,
                        text=question_text,
                        type=question_type,
                        sdg_id=goal.id,
                        max_score=5.0,
                        display_order=question_id,
                        options='["Not at all", "Slightly", "Moderately", "Significantly", "Extremely"]' if question_type == 'radio' else '["Option A", "Option B", "Option C", "Option D"]'
                    )
                    db.session.add(question)
                    question_id += 1
            
            db.session.commit()
            results['actions_taken'].append(f"Added {question_id - 1} SDG Questions")
        else:
            results['actions_taken'].append("SDG Questions already exist")
        
        # Final counts
        results['final_goals'] = SdgGoal.query.count()
        results['final_questions'] = SdgQuestion.query.count()
        results['success'] = True
        
        current_app.logger.info(f"Database population completed: {results}")
        
        return jsonify(results), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error populating database: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Database population failed'
        }), 500


# --- Database Management Functions ---

def validate_questions_database():
    """Verify all expected questions exist in the database."""
    try:
        conn = get_db()
        existing_ids = [q['id'] for q in conn.execute('SELECT id FROM sdg_questions').fetchall()]
        expected_ids = list(range(1, 32))  # Questions 1-31
        missing_ids = [id for id in expected_ids if id not in existing_ids]
        
        if missing_ids:
            current_app.logger.warning(f"Missing question IDs in database: {missing_ids}")
            return False
        
        current_app.logger.info("All expected question IDs exist in the database")
        return True
    except Exception as e:
        current_app.logger.error(f"Error validating questions database: {str(e)}")
        return False


def populate_questions():
    """Populate the sdg_questions table with all required questions."""
    final_success = False
    try:
        conn = get_db()

        # --- CONFIRM THESE MATCH YOUR TABLE ---
        COL_ID = 'id'
        COL_TEXT = 'text'
        COL_TYPE = 'type'
        COL_SDG_ID = 'sdg_id'
        COL_MAX_SCORE = 'max_score'
        # Add other columns if they need default values during insert
        # COL_OPTIONS = 'options'
        # COL_DISPLAY_ORDER = 'display_order'
        # -------------------------------------

        existing_ids = [q[COL_ID] for q in conn.execute(f'SELECT {COL_ID} FROM sdg_questions').fetchall()]
        questions_to_add = []
        current_app.logger.info(f"Existing question IDs in DB: {existing_ids}")

        for i in range(1, 32):  # Questions 1-31
            if i not in existing_ids:
                target_sdg_id = ((i - 1) % 17) + 1
                q_type = 'checkbox' if i % 2 == 0 else 'radio' # Adjust logic as needed
                q_text = f'PLACEHOLDER TEXT: Question {i} (SDG {target_sdg_id})' # *** REPLACE WITH ACTUAL TEXT ***
                q_max_score = 5.0

                questions_to_add.append({
                    COL_ID: i,
                    COL_TEXT: q_text,
                    COL_TYPE: q_type,
                    COL_SDG_ID: target_sdg_id,
                    COL_MAX_SCORE: q_max_score
                    # Add defaults for other columns if they cannot be NULL
                    # COL_OPTIONS: None,
                    # COL_DISPLAY_ORDER: i,
                })

        if not questions_to_add:
             current_app.logger.info("No missing questions (1-31) found to add. Table already populated.")
             final_success = True
        else:
            current_app.logger.info(f"Found {len(questions_to_add)} missing questions to add.")
            insert_sql = f'''
                INSERT INTO sdg_questions ({COL_ID}, {COL_TEXT}, {COL_TYPE}, {COL_SDG_ID}, {COL_MAX_SCORE})
                VALUES (?, ?, ?, ?, ?)
            '''
            current_app.logger.info(f"Executing INSERT SQL: {insert_sql}")
            added_count = 0
            for q_data in questions_to_add:
                 try:
                     conn.execute(insert_sql, (
                         q_data[COL_ID],
                         q_data[COL_TEXT],
                         q_data[COL_TYPE],
                         q_data[COL_SDG_ID],
                         q_data[COL_MAX_SCORE]
                     ))
                     added_count += 1
                 except Exception as insert_e:
                      current_app.logger.error(f"Failed to insert question {q_data[COL_ID]}: {insert_e}")
            conn.commit()
            current_app.logger.info(f"Added {added_count} questions to the database.")
            final_success = added_count == len(questions_to_add)
    except Exception as e:
        current_app.logger.error(f"Error populating questions: {str(e)}")
        if conn:
            conn.rollback()
        final_success = False
    finally:
        if final_success:
            print("populate_questions: Succeeded.")
        else:
            print("populate_questions: Failed.")
    return final_success


@assessments_bp.route('/projects/<int:project_id>/assessments/<int:assessment_id>/share', methods=['POST'])
@login_required
def share_assessment(project_id, assessment_id):
    """Generate shareable link for assessment results."""
    import secrets
    from datetime import timedelta

    project = db.session.get(Project, project_id)
    if not project or project.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    assessment = db.session.get(Assessment, assessment_id)
    if not assessment or assessment.project_id != project_id:
        return jsonify({'success': False, 'message': 'Assessment not found'}), 404

    # Generate unique share token
    share_token = secrets.token_urlsafe(32)

    # Store token in assessment
    assessment.share_token = share_token
    assessment.share_expires = datetime.utcnow() + timedelta(days=30)  # 30-day expiry
    db.session.commit()

    # Generate shareable URL
    share_url = url_for('assessments.view_shared', token=share_token, _external=True)

    return jsonify({
        'success': True,
        'share_url': share_url,
        'expires_at': assessment.share_expires.isoformat()
    })


@assessments_bp.route('/shared/<token>')
def view_shared(token):
    """View shared assessment results (public, no login required)."""
    assessment = Assessment.query.filter_by(share_token=token).first()

    if not assessment:
        flash('Invalid or expired share link.', 'error')
        return redirect(url_for('main.index'))

    # Check expiry
    if assessment.share_expires and assessment.share_expires < datetime.utcnow():
        flash('This share link has expired.', 'error')
        return redirect(url_for('main.index'))

    # Render results page in read-only mode
    return render_template(
        'questionnaire/results_shared.html',
        assessment=assessment,
        project=assessment.project,
        read_only=True
    )


def populate_sdg_relationships():
    """Populate the sdg_relationships table with relationships between SDGs."""
    try:
        conn = get_db()
        
        # Check if relationships already exist
        existing = conn.execute('SELECT COUNT(*) as count FROM sdg_relationships').fetchone()
        if existing and existing['count'] > 0:
            current_app.logger.info(f"SDG relationships table already has {existing['count']} entries")
            return True
        
        # Define relationships (source_sdg_id, target_sdg_id, relationship_strength)
        relationships = [
            # SDG 1 (No Poverty) relationships
            (1, 2, 0.8),  # Strong relationship with SDG 2 (Zero Hunger)
            (1, 3, 0.7),  # Strong relationship with SDG 3 (Good Health)
            (1, 4, 0.9),  # Very strong relationship with SDG 4 (Education)
            
            # SDG 2 (Zero Hunger) relationships
            (2, 1, 0.8),  # Strong relationship with SDG 1 (No Poverty)
            (2, 3, 0.9),  # Very strong relationship with SDG 3 (Good Health)
            (2, 15, 0.7),  # Strong relationship with SDG 15 (Life on Land)
        ]
        
        # Insert relationships
        for rel in relationships:
            conn.execute('''
                INSERT INTO sdg_relationships (source_sdg_id, target_sdg_id, relationship_strength)
                VALUES (?, ?, ?)
            ''', rel)
            
        conn.commit()
        current_app.logger.info(f"Added {len(relationships)} SDG relationships to the database")
        return True
    except Exception as e:
        current_app.logger.error(f"Error populating SDG relationships: {str(e)}")
        return False
