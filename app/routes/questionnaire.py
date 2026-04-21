from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app import db as orm_db
from app.models.assessment import Assessment
from app.models.project import Project
from app.models.response import QuestionResponse
from app.models.sdg import SdgQuestion
from app.services import scoring_service
from datetime import datetime
import json
from sqlalchemy import select

questionnaire_bp = Blueprint('questionnaire', __name__, url_prefix='/questionnaire')

@questionnaire_bp.route('/')
@login_required
def index():
    return render_template('questionnaire/index.html', title='Questionnaire')

@questionnaire_bp.route('/<int:assessment_id>/save', methods=['POST'])
@login_required
def save_questionnaire_response(assessment_id):
    """Save a questionnaire response for an assessment."""
    current_app.logger.critical(f"--- HIT questionnaire.save_questionnaire_response for assessment {assessment_id} ---")
    user_id = current_user.id

    # ORM Version for Ownership Check
    assessment = orm_db.session.execute(
        select(Assessment).join(Project).where(
            Assessment.id == assessment_id,
            Project.user_id == user_id
        )
    ).scalar_one_or_none()

    if not assessment:
        current_app.logger.warning(f"Save response failed: Assessment {assessment_id} not found or access denied for user {user_id}")
        return jsonify({'error': 'Assessment not found or access denied'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    question_id = data.get('question_id')
    response_text = data.get('response_text')  # Match the key from test payload
    response_option = data.get('response_option')

    if not question_id:
        return jsonify({'error': 'Question ID is required'}), 400

    # ORM Version for fetching SdgQuestion
    question = orm_db.session.get(SdgQuestion, question_id)
    score = None

    if question:
        # Use the actual value received for response_text for scoring
        processed_score = scoring_service.process_question_response(
            question.type,
            response_text,  # Use the retrieved response_text
            question.options,
            question.max_score
        )
        score = processed_score

    # ORM Version for existing response check and update/insert
    existing_response = orm_db.session.execute(
        select(QuestionResponse).filter_by(assessment_id=assessment_id, question_id=question_id)
    ).scalar_one_or_none()

    try:
        # The value to store in the database is response_text (which might be a string, or a JSON string if it was complex)
        # If response_text itself is a list/dict from JSON, it should be stringified for db.Text
        # However, the test sends a simple string 'Test response text'.
        response_text_for_db = json.dumps(response_text) if isinstance(response_text, (list, dict)) else response_text

        if existing_response:
            existing_response.response_text = response_text_for_db  # Use the correct value
            existing_response.response_score = score
            existing_response.updated_at = datetime.utcnow()
        else:
            new_response = QuestionResponse(
                assessment_id=assessment_id,
                question_id=question_id,
                response_text=response_text_for_db,  # Use the correct value
                response_score=score
            )
            orm_db.session.add(new_response)

        assessment.updated_at = datetime.utcnow()
        orm_db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Response saved successfully',
            'score': score
        }), 200

    except Exception as e:
        orm_db.session.rollback()
        current_app.logger.error(f"Error saving response for assessment {assessment_id}, q {question_id}: {str(e)}")
        return jsonify({'error': 'Failed to save response'}), 500
