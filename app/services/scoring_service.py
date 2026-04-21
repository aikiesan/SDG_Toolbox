"""
SDG Scoring Service.
Contains logic for calculating SDG scores based on question responses.
"""

import json
import math

def map_option_to_score(option):
    """Map a string option to a numeric score.
    Handles Likert scales, Yes/No, and also assigns a default score to checkbox values (unmatched strings).
    """
    # Handle None or empty values
    if option is None or option == '':
        return 0.0
    # Handle already numeric values
    try:
        return float(option)
    except (ValueError, TypeError):
        pass
    option = str(option).lower()
    # Likert-type scales
    if option in ('strongly agree', 'excellent', 'very high', 'always'):
        return 5.0
    elif option in ('agree', 'good', 'high', 'often'):
        return 4.0
    elif option in ('neutral', 'moderate', 'medium', 'sometimes'):
        return 3.0
    elif option in ('disagree', 'poor', 'low', 'rarely'):
        return 2.0
    elif option in ('strongly disagree', 'very poor', 'very low', 'never'):
        return 1.0
    # Yes/No type responses
    elif option in ('yes', 'true', '1', 'y'):
        return 5.0
    elif option in ('partially', 'somewhat', 'in progress'):
        return 3.0
    elif option in ('no', 'false', '0', 'n'):
        return 0.0
    # --- Checkbox/Unknown Value Handling ---
    # If the option text doesn't match any known scale, assume it is a checkbox value
    # or other non-empty string and assign a default positive score (e.g., 1.0).
    if option:
        return 1.0
    # Default case (should not be reached)
    return 0.0

# --- IMPORTS ---
import json
import math
from app import db
from app.models.assessment import Assessment, SdgScore
from app.models.response import QuestionResponse
from app.models.sdg import SdgGoal, SdgQuestion  # Assuming SdgQuestion is defined here or import separately
from app.models.sdg_relationship import SdgRelationship  # Make sure this model exists and is imported
from flask import current_app  # For logging
from app.services.assessment_cache_service import invalidate_assessment_cache

def calculate_sdg_scores(assessment_id):
    """
    Calculate SDG scores based on question responses using SQLAlchemy ORM.
    Updates Assessment and SdgScore records directly.

    Args:
        assessment_id: ID of the assessment to calculate scores for

    Returns:
        Dictionary containing calculated scores {'sdg_scores': {...}, 'overall_score': ...}
    """
    print(f"--- ORM: ENTERING calculate_sdg_scores for assessment_id: {assessment_id} ---")

    assessment = db.session.get(Assessment, assessment_id)
    if not assessment:
        print(f"ERROR: Assessment {assessment_id} not found via ORM.")
        return {'sdg_scores': {}, 'overall_score': 0}

    try:
        from app.models.sdg import SdgQuestion
        question_count_db = db.session.query(SdgQuestion).count()
        if question_count_db == 0:
            print("CRITICAL ERROR: sdg_questions table is empty or inaccessible (ORM query)!")
            assessment.overall_score = 0
            db.session.commit()
            return {'sdg_scores': {}, 'overall_score': 0}
        print(f"ORM: Found {question_count_db} rows in sdg_questions table.")
    except Exception as q_check_e:
        print(f"CRITICAL ERROR checking sdg_questions table via ORM: {q_check_e}")
        return {'sdg_scores': {}, 'overall_score': 0}

    print(f"ORM: Querying QuestionResponse for assessment_id = {assessment_id}")
    try:
        responses = QuestionResponse.query.filter_by(assessment_id=assessment_id).all()
    except Exception as query_e:
        print(f"CRITICAL ERROR executing ORM query for responses: {query_e}")
        assessment.overall_score = 0
        db.session.commit()
        return {'sdg_scores': {}, 'overall_score': 0}

    # Pre-fetch all SDG goals and existing scores in single queries (avoid N+1)
    all_sdg_goals = SdgGoal.query.all()
    all_sdg_ids = [g.id for g in all_sdg_goals]

    # Batch fetch existing scores for this assessment
    existing_scores = {
        score.sdg_id: score
        for score in SdgScore.query.filter_by(assessment_id=assessment_id).all()
    }

    if not responses:
        print(f"ORM: Query returned 0 responses for assessment_id {assessment_id}.")
        assessment.overall_score = 0
        for sdg_id in all_sdg_ids:
            sdg_score_obj = existing_scores.get(sdg_id)
            if not sdg_score_obj:
                sdg_score_obj = SdgScore(assessment_id=assessment_id, sdg_id=sdg_id)
                db.session.add(sdg_score_obj)
            sdg_score_obj.direct_score = 0.0
            sdg_score_obj.bonus_score = 0.0
            sdg_score_obj.total_score = 0.0
            sdg_score_obj.raw_score = 0.0
            sdg_score_obj.max_possible = 0.0
            sdg_score_obj.percentage_score = 0.0
            sdg_score_obj.question_count = 0
        db.session.commit()
        return {'sdg_scores': {}, 'overall_score': 0}

    print(f"ORM: Query successfully found {len(responses)} responses.")
    print("First few responses fetched by ORM:")
    for i, r in enumerate(responses[:5]):
        print(f"  Row {i}: assessment={r.assessment_id}, q_id={r.question_id}, score={r.response_score}, text='{r.response_text}'")

    print("--- ORM: Starting Raw Score Calculation Loop ---")
    # Reuse all_sdg_ids and existing_scores from above to avoid redundant queries
    sdg_raw_scores = {sdg_id: 0.0 for sdg_id in all_sdg_ids}
    sdg_max_possible_raw = {sdg_id: 0.0 for sdg_id in all_sdg_ids}
    sdg_question_counts = {sdg_id: 0 for sdg_id in all_sdg_ids}
    counted_questions_for_max = set()

    try:
        questions_details = {q.id: {'sdg_id': q.sdg_id, 'max_score': float(q.max_score or 5.0)} for q in SdgQuestion.query.all()}
    except Exception as q_details_e:
        print(f"ERROR fetching question details via ORM: {q_details_e}")
        return {'sdg_scores': {}, 'overall_score': 0}

    for response in responses:
        question_id = response.question_id
        response_score = float(response.response_score or 0.0)
        q_detail = questions_details.get(question_id)
        if not q_detail:
            print(f"  Warning: Details not found for Question ID {question_id}. Skipping response.")
            continue
        sdg_id = q_detail['sdg_id']
        print(f"  ORM Processing response: Q_ID={question_id}, SDG_ID={sdg_id}, Score={response_score}")
        if sdg_id not in sdg_raw_scores:
            print(f"  Warning: SDG ID {sdg_id} from question details not in goal list. Skipping.")
            continue
        sdg_raw_scores[sdg_id] += response_score
        sdg_question_counts[sdg_id] += 1
        if question_id not in counted_questions_for_max:
            q_max_score = q_detail.get('max_score', 5.0)
            sdg_max_possible_raw[sdg_id] += q_max_score
            counted_questions_for_max.add(question_id)
            print(f"    -> Added max score {q_max_score} for Q{question_id} to SDG {sdg_id}. New Max Total: {sdg_max_possible_raw[sdg_id]}")
        print(f"    -> SDG {sdg_id}: New Raw Score = {sdg_raw_scores[sdg_id]}, Count = {sdg_question_counts[sdg_id]}")

    print("--- ORM: Finished Raw Score Calculation Loop ---")
    print("--- ORM: Calculating Normalized Scores ---")
    sdg_direct_scores = {}
    for sdg_id in all_sdg_ids:
        raw_score = sdg_raw_scores.get(sdg_id, 0)
        max_possible = sdg_max_possible_raw.get(sdg_id, 0)
        q_count = sdg_question_counts.get(sdg_id, 0)
        print(f"SDG {sdg_id}: Raw={raw_score}, MaxPossible={max_possible}, QuestionCount={q_count}")
        if max_possible > 0:
            # Initial normalization + boost
            normalized_score = min(10, (raw_score / max_possible) * 10 * 1.25)

            # --- FLOOR ADJUSTED TO 3.0 ---
            if raw_score > 0 and normalized_score < 3.0:
                normalized_score = 3.0
                print(f"  Applied minimum score floor of 3.0 for SDG {sdg_id}")

            # --- SCALING ADJUSTED TO START FROM 3.0 ---
            if 3.0 <= normalized_score < 7.0:
                original_score = normalized_score
                normalized_score = 3.0 + (normalized_score - 3.0) * 1.2
                print(f"  Applied progressive scaling to SDG {sdg_id}: {original_score:.2f} -> {normalized_score:.2f}")
        else:
            normalized_score = 0
        sdg_direct_scores[sdg_id] = normalized_score
        print(f"  -> NormalizedDirect={normalized_score:.2f}")

    # --- ORM: Calculating Bonus Scores ---
    current_app.logger.info("--- ORM: Calculating Bonus Scores ---")
    sdg_bonus_scores = {sdg_id: 0.0 for sdg_id in all_sdg_ids} # Initialize all bonus scores to 0

    try:
        # Fetch all relationships at once
        all_relationships = SdgRelationship.query.all()
        if not all_relationships:
            current_app.logger.warning("ORM WARNING: No SDG relationships found in the database. Bonus scores will remain 0.")
        else:
            current_app.logger.info(f"ORM: Found {len(all_relationships)} SDG relationships.")

            # Iterate through each relationship to potentially apply bonus
            for rel in all_relationships:
                source_sdg_id = rel.source_sdg_id
                target_sdg_id = rel.target_sdg_id
                strength = float(rel.strength or 0.0)

                # Ensure target SDG ID is valid before proceeding
                if target_sdg_id not in sdg_bonus_scores:
                    current_app.logger.warning(f"  Skipping relationship: Target SDG {target_sdg_id} not in score dictionary.")
                    continue

                # Get the DIRECT score of the SOURCE SDG
                source_direct_score = sdg_direct_scores.get(source_sdg_id, 0.0)

                # --- Define Your Bonus Logic Here ---
                bonus_increment = 0.0
                # Example: Apply bonus ONLY from 'Good' or 'Excellent' source scores (>= 6.0)
                # AND ONLY for positive relationships (strength > 0)
                if source_direct_score >= 6.0 and strength > 0:
                    # Formula: Bonus scaled by how much source exceeds threshold and relationship strength
                    threshold = 6.0
                    factor = 0.15 # Tunable factor - how much bonus to give (0.15 = 15%)
                    bonus_increment = (source_direct_score - threshold) * strength * factor
                    sdg_bonus_scores[target_sdg_id] += bonus_increment
                    current_app.logger.debug(f"  Applying bonus to SDG {target_sdg_id}: +{bonus_increment:.2f} (From SDG {source_sdg_id}, Score: {source_direct_score:.1f}, Strength: {strength:.2f})")

            # --- Apply Bonus Cap ---
            MAX_BONUS_POINTS = 2.0 # Max bonus an SDG can receive
            for sdg_id in sdg_bonus_scores:
                original_bonus = sdg_bonus_scores[sdg_id]
                # Cap bonus between 0 and MAX_BONUS_POINTS
                capped_bonus = min(max(original_bonus, 0.0), MAX_BONUS_POINTS)
                sdg_bonus_scores[sdg_id] = capped_bonus
                if original_bonus != capped_bonus and original_bonus > 0: # Log only if changed and was positive
                    current_app.logger.info(f"  Capped Bonus for SDG {sdg_id}: {original_bonus:.2f} -> {capped_bonus:.2f}")

    except Exception as bonus_calc_e:
        current_app.logger.error(f"ERROR during bonus score calculation: {bonus_calc_e}", exc_info=True)
        # Fallback to 0 bonus if calculation fails
        sdg_bonus_scores = {sdg_id: 0.0 for sdg_id in all_sdg_ids}
    # --- ORM: Calculating Total Scores ---


    current_app.logger.info("--- ORM: Calculating Total Scores ---")
    sdg_total_scores = {}
    for sdg_id in all_sdg_ids:
        direct = sdg_direct_scores.get(sdg_id, 0.0)
        bonus = sdg_bonus_scores.get(sdg_id, 0.0) # Use the calculated & capped bonus
        total = direct + bonus
        # Cap total score between 0 and 10
        sdg_total_scores[sdg_id] = min(max(total, 0.0), 10.0)
        current_app.logger.debug(f"SDG {sdg_id}: Direct={direct:.2f}, Bonus={bonus:.2f}, Raw Total={total:.2f}, Final Total Score = {sdg_total_scores[sdg_id]:.2f}")

    current_app.logger.info("--- ORM: Saving Calculated Scores to sdg_scores table ---")
    # (The saving loop should correctly pick up the new bonus_score_val and total_score_val)
    for sdg_id in all_sdg_ids:
        # Use pre-fetched existing scores to avoid N+1 query
        sdg_score_obj = existing_scores.get(sdg_id)
        if not sdg_score_obj:
            sdg_score_obj = SdgScore(assessment_id=assessment_id, sdg_id=sdg_id)
            db.session.add(sdg_score_obj)
            existing_scores[sdg_id] = sdg_score_obj  # Add to cache

        # Assign calculated values
        direct_score_val = sdg_direct_scores.get(sdg_id, 0.0)
        bonus_score_val = sdg_bonus_scores.get(sdg_id, 0.0)
        total_score_val = sdg_total_scores.get(sdg_id, 0.0)
        raw_score_val = sdg_raw_scores.get(sdg_id, 0.0) # Assuming sdg_raw_scores exists from direct calc
        max_possible_val = sdg_max_possible_raw.get(sdg_id, 0.0) # Assuming exists from direct calc
        percentage_val = (raw_score_val / max_possible_val) * 100 if max_possible_val else 0.0
        question_count_val = sdg_question_counts.get(sdg_id, 0) # Assuming exists from direct calc

        # Update the SdgScore object
        sdg_score_obj.direct_score = direct_score_val
        sdg_score_obj.bonus_score = bonus_score_val # Assign calculated bonus
        sdg_score_obj.total_score = total_score_val # Assign calculated total
        sdg_score_obj.raw_score = raw_score_val
        sdg_score_obj.max_possible = max_possible_val
        sdg_score_obj.percentage_score = percentage_val
        sdg_score_obj.question_count = question_count_val

        current_app.logger.debug(f"  ORM Preparing to Save SDG {sdg_id}: Direct={sdg_score_obj.direct_score:.2f}, Bonus={sdg_score_obj.bonus_score:.2f}, Total={sdg_score_obj.total_score:.2f}, Count={sdg_score_obj.question_count}")

    print("--- ORM: Calculating and Saving Overall Score ---")
    valid_total_scores = [score for score in sdg_total_scores.values() if score is not None]
    overall_score = sum(valid_total_scores) / len(valid_total_scores) if valid_total_scores else 0
    overall_score = round(overall_score, 2)
    print(f"ORM Calculated Overall Score: {overall_score}")
    assessment.overall_score = overall_score
    assessment.updated_at = db.func.now()
    try:
        db.session.commit()
        print("--- ORM: Committed sdg_scores updates and assessment overall_score ---")

        # Invalidate cache for this assessment after successful update
        try:
            invalidate_assessment_cache(assessment_id)
            print(f"--- ORM: Invalidated cache for assessment {assessment_id} ---")
        except Exception as cache_e:
            # Don't fail if cache invalidation fails
            print(f"Warning: Cache invalidation failed: {cache_e}")

    except Exception as final_commit_e:
        db.session.rollback()
        print(f"ERROR during final commit in scoring service: {final_commit_e}")
        return {'sdg_scores': {}, 'overall_score': 0}
    print(f"--- ORM: EXITING calculate_sdg_scores for assessment_id: {assessment_id} ---")
    return {'sdg_scores': sdg_total_scores, 'overall_score': overall_score}



    if not questions:
        print("Warning: No questions found in the database.")
        # Set overall score to 0 in assessment table if no questions exist
        conn.execute('UPDATE assessments SET overall_score = 0, updated_at = CURRENT_TIMESTAMP WHERE id = ?', (assessment_id,))
        return {'sdg_scores': {}, 'overall_score': 0}

    questions_dict = {q['id']: dict(q) for q in questions}

    # Get all question responses for this assessment
    responses = conn.execute('''
        SELECT * FROM question_responses
        WHERE assessment_id = ?
    ''', (assessment_id,)).fetchall()
    if not responses:
        print(f"Warning: No responses found for assessment_id {assessment_id}.")
        # Proceed to calculate 0 scores for all SDGs

    # Create a lookup dictionary of responses by question ID
    response_lookup = {r['question_id']: r for r in responses}

    # --- Step 1: Calculate Raw Scores and Max Possible Raw Scores per SDG ---
    all_sdg_ids = [q['id'] for q in conn.execute('SELECT id FROM sdg_goals').fetchall()]
    sdg_raw_scores = {}
    sdg_max_possible_raw = {}
    sdg_question_counts = {sdg_id: 0 for sdg_id in all_sdg_ids}

    for sdg_id in all_sdg_ids:  # Initialize all SDGs
        sdg_raw_scores[sdg_id] = 0
        sdg_max_possible_raw[sdg_id] = 0

    for qid, question_info in questions_dict.items():
        sdg_id = question_info['sdg_id']
        if sdg_id not in all_sdg_ids: continue  # Skip if somehow question maps to non-existent SDG

        # Add max possible score for this question (typically 5)
        q_max_score = float(question_info.get('max_score', 5))
        sdg_max_possible_raw[sdg_id] += q_max_score
        sdg_question_counts[sdg_id] += 1  # Count questions per SDG

        # Add actual score achieved for this question from responses
        response = response_lookup.get(qid)
        if response:
            sdg_raw_scores[sdg_id] += response['response_score']

    # --- Step 2: Calculate Normalized Direct Scores (0-10 scale) ---
    sdg_direct_scores = {}
    for sdg_id in all_sdg_ids:
        raw_score = sdg_raw_scores.get(sdg_id, 0)
        max_possible = sdg_max_possible_raw.get(sdg_id, 0)

        if max_possible > 0:
            # Enhanced normalization formula with a more significant boost
            # This applies a 25% boost to scores to counteract the feeling of scores being lowered
            normalized_score = min(10, (raw_score / max_possible) * 10 * 1.25)
            
            # Apply a floor of 4.0 for any SDG that has at least one response
            if raw_score > 0 and normalized_score < 4.0:
                normalized_score = 4.0
                print(f"  Applied minimum score floor of 4.0 for SDG {sdg_id}")
            
            # Apply progressive scaling to mid-range scores to make them feel more rewarding
            # This creates a more generous curve in the middle range (4-7)
            if 4.0 <= normalized_score < 7.0:
                original_score = normalized_score
                normalized_score = 4.0 + (normalized_score - 4.0) * 1.2
                print(f"  Applied progressive scaling to SDG {sdg_id}: {original_score:.2f} -> {normalized_score:.2f}")
        else:
            normalized_score = 0  # Assign 0 if no questions/max score defined for this SDG

        sdg_direct_scores[sdg_id] = normalized_score
        print(f"SDG ID {sdg_id}: Raw={raw_score}, MaxPossible={max_possible}, NormalizedDirect={normalized_score:.2f}")  # Debug print

    # --- Step 3: Calculate Bonus Scores (Cross-SDG Point Transfer) ---
    relationships = conn.execute('SELECT * FROM sdg_relationships').fetchall()
    sdg_relationships = {}
    
    # Debug: Check if relationships data exists
    if not relationships:
        print("WARNING: No SDG relationships found in the database. Cross-SDG Point Transfer will not work.")
    else:
        print(f"Found {len(relationships)} SDG relationships in the database.")
    
    for rel in relationships:
        source_id = rel['source_sdg_id']
        if source_id not in sdg_relationships: sdg_relationships[source_id] = []
        sdg_relationships[source_id].append({
            'target_id': rel['target_sdg_id'],
            'strength': rel['relationship_strength']
        })

    sdg_bonus_scores = {sdg_id: 0 for sdg_id in all_sdg_ids}
    for source_id, direct_score in sdg_direct_scores.items():
        # Lower the threshold for bonus point generation from 7 to 6
        # This allows more SDGs to generate bonus points
        if direct_score >= 6:
            bonus_value = 0
            if direct_score >= 9: bonus_value = 1.5    # Increased from 1.0
            elif direct_score >= 8: bonus_value = 1.0  # Increased from 0.7
            elif direct_score >= 7: bonus_value = 0.7  # Increased from 0.5
            else: bonus_value = 0.5                    # New tier for scores >=6
            
            print(f"SDG {source_id} has direct score {direct_score:.2f} >= 6, generating bonus value: {bonus_value}")

            if source_id in sdg_relationships:
                sorted_relations = sorted(sdg_relationships[source_id], key=lambda x: x['strength'], reverse=True)
                print(f"  Found {len(sorted_relations)} relationships for SDG {source_id}")
                
                # Increase from top 3 to top 4 relationships
                for relation in sorted_relations[:4]:
                    target_id = relation['target_id']
                    strength = relation['strength']
                    if target_id in sdg_bonus_scores:  # Check if target SDG exists
                        bonus = bonus_value * strength
                        sdg_bonus_scores[target_id] += bonus
                        print(f"  Applying bonus from SDG {source_id} to SDG {target_id}: +{bonus:.2f} (Strength: {strength}, Base: {bonus_value})")
            else:
                print(f"  No relationships found for SDG {source_id}")

    # Apply balance constraint: Max 3 bonus points receivable per SDG (increased from 2)
    for sdg_id in sdg_bonus_scores:
        original_bonus = sdg_bonus_scores[sdg_id]
        sdg_bonus_scores[sdg_id] = min(original_bonus, 3)
        if original_bonus > 0:
            print(f"SDG {sdg_id} bonus points: {original_bonus:.2f}, after cap: {sdg_bonus_scores[sdg_id]:.2f}")

    # --- Step 4: Calculate Total Scores (Direct + Bonus, capped at 10) ---
    sdg_total_scores = {}
    for sdg_id in all_sdg_ids:
        direct = sdg_direct_scores.get(sdg_id, 0)
        bonus = sdg_bonus_scores.get(sdg_id, 0)
        total = direct + bonus
        sdg_total_scores[sdg_id] = min(total, 10)  # Cap total score at 10

    # --- Step 5: Store Detailed Scores in Database ---
    for sdg_id in all_sdg_ids:
        direct_score_val = sdg_direct_scores.get(sdg_id, 0)
        bonus_score_val = sdg_bonus_scores.get(sdg_id, 0)
        raw_score_val = sdg_raw_scores.get(sdg_id, 0)
        max_possible_val = sdg_max_possible_raw.get(sdg_id, 0)
        total_score_val = min(direct_score_val + bonus_score_val, 10)
        percentage_val = (raw_score_val / max_possible_val) * 100 if max_possible_val > 0 else 0
        question_count_val = sdg_question_counts.get(sdg_id, 0)

        print(f"DEBUG Scoring Service: Preparing to save for SDG {sdg_id}: Direct={direct_score_val:.2f}, Bonus={bonus_score_val:.2f}, Total={total_score_val:.2f}, Raw={raw_score_val}, Max={max_possible_val}, Percentage={percentage_val:.2f}, Count={question_count_val}")

        existing = conn.execute('SELECT id FROM sdg_scores WHERE assessment_id = ? AND sdg_id = ?', (assessment_id, sdg_id)).fetchone()

        if existing:
            conn.execute('''
                UPDATE sdg_scores SET
                    direct_score = ?, bonus_score = ?, total_score = ?,
                    raw_score = ?, max_possible = ?, percentage_score = ?, question_count = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (direct_score_val, bonus_score_val, total_score_val,
                  raw_score_val, max_possible_val, percentage_val, question_count_val,
                  existing['id']))
        else:
            conn.execute('''
                INSERT INTO sdg_scores (
                    assessment_id, sdg_id, direct_score, bonus_score, total_score,
                    raw_score, max_possible, percentage_score, question_count,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ''', (assessment_id, sdg_id, direct_score_val, bonus_score_val, total_score_val,
                  raw_score_val, max_possible_val, percentage_val, question_count_val))

    # --- Step 6: Calculate and Update Overall Assessment Score ---
    valid_total_scores = [score for score in sdg_total_scores.values() if score is not None]
    overall_score = sum(valid_total_scores) / len(valid_total_scores) if valid_total_scores else 0
    overall_score = round(overall_score, 2)
    print(f"Calculated Overall Score: {overall_score}")  # Debug print

    conn.execute('''
        UPDATE assessments SET overall_score = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?
    ''', (overall_score, assessment_id))

    # Note: No commit here, commit happens in the calling function

    return {
        'sdg_scores': sdg_total_scores,
        'overall_score': overall_score
    }

def process_question_response(question_type, value, options=None, max_score=5):
    """
    Process a question response and calculate its score.
    
    Args:
        question_type: Type of question (select, checklist, etc.)
        value: Response value
        options: Question options (for checklists)
        max_score: Maximum score for this question
        
    Returns:
        Calculated score value
    """
    if question_type == 'select':
        # For select/radio questions, value is the score (1-5)
        try:
            return min(float(value), max_score)
        except (ValueError, TypeError):
            return 0
    
    elif question_type == 'checklist':
        # For checklist questions, calculate based on selected options
        try:
            selected_keys = json.loads(value) if isinstance(value, str) else value
            
            if not selected_keys or not isinstance(selected_keys, list):
                return 0
            
            # If options have defined values, use them
            if options:
                try:
                    options_data = json.loads(options) if isinstance(options, str) else options
                    option_value_map = {opt.get('key', opt['text']): float(opt.get('value', 1)) 
                                       for opt in options_data}
                    
                    current_score = sum(option_value_map.get(key, 0) for key in selected_keys)
                except (json.JSONDecodeError, KeyError, TypeError):
                    # Fallback: 1 point per selection
                    current_score = len(selected_keys)
            else:
                # No options defined, use 1 point per selection
                current_score = len(selected_keys)
            
            # Special handling for certain questions (example)
            # if question_id in [29, 30, 31]:  # SDGs 15, 16, 17
            #     if len(selected_keys) > 0:
            #         min_score = len(selected_keys) * 0.75
            #         current_score = max(current_score, min_score)
            
            return min(current_score, max_score)
        
        except (json.JSONDecodeError, TypeError):
            return 0
    
    # For other question types or errors
    return 0

def get_assessment_summary(conn, assessment_id):
    """
    Generate a summary of assessment results for display.
    
    Args:
        conn: Database connection
        assessment_id: ID of the assessment to summarize
        
    Returns:
        Dictionary containing summary information
    """
    # Get assessment details
    assessment = conn.execute('''
        SELECT a.*, p.name as project_name, p.description as project_description
        FROM assessments a
        JOIN projects p ON a.project_id = p.id
        WHERE a.id = ?
    ''', (assessment_id,)).fetchone()
    
    if not assessment:
        return {'error': 'Assessment not found'}
    
    # Get SDG scores
    scores = conn.execute('''
        SELECT s.*, g.number, g.name, g.description, g.color_code
        FROM sdg_scores s
        JOIN sdg_goals g ON s.sdg_id = g.id
        WHERE s.assessment_id = ?
        ORDER BY g.number
    ''', (assessment_id,)).fetchall()
    
    # Convert to dictionaries for JSON serialization
    scores_list = [dict(score) for score in scores]
    
    # Group by SDG categories
    categories = {
        'People': [s for s in scores_list if s['number'] in [1, 2, 3, 4, 5]],
        'Planet': [s for s in scores_list if s['number'] in [6, 12, 13, 14, 15]],
        'Prosperity': [s for s in scores_list if s['number'] in [7, 8, 9, 10, 11]],
        'Peace & Partnership': [s for s in scores_list if s['number'] in [16, 17]]
    }
    
    # Calculate category averages
    category_scores = {}
    for category, category_scores_list in categories.items():
        if category_scores_list:
            category_scores[category] = sum(s['total_score'] for s in category_scores_list) / len(category_scores_list)
        else:
            category_scores[category] = 0
    
    # Identify top and bottom performing SDGs
    sorted_scores = sorted(scores_list, key=lambda s: s['total_score'], reverse=True)
    top_sdgs = sorted_scores[:3] if len(sorted_scores) >= 3 else sorted_scores
    bottom_sdgs = sorted_scores[-3:] if len(sorted_scores) >= 3 else sorted_scores
    
    # Prepare chart data
    chart_data = [
        {
            'sdg': score['number'],
            'name': score['name'],
            'direct': score['direct_score'],
            'bonus': score['bonus_score'],
            'total': score['total_score'],
            'color': score['color_code']
        }
        for score in scores_list
    ]
    
    return {
        'assessment': dict(assessment),
        'scores': scores_list,
        'categories': categories,
        'category_scores': category_scores,
        'top_sdgs': top_sdgs,
        'bottom_sdgs': bottom_sdgs,
        'chart_data': chart_data,
        'overall_score': assessment['overall_score']
    }
