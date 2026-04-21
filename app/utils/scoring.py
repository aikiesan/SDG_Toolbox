from app import db
from app.models.assessment import Assessment, SdgScore

from app.models.sdg import SdgGoal

def calculate_sdg_scores(assessment_id):
    """
    Calculate SDG scores based on question responses using SQLAlchemy.
    Returns a dictionary of SDG scores.
    """
    # Get the assessment
    assessment = db.session.get(Assessment, assessment_id)
    if not assessment:
        return {"error": "Assessment not found"}
    
    # Get all questions with their SDG associations
    questions = Question.query.join(SdgGoal).all()
    if not questions:
        print("Warning: No questions found in the database.")
        return {"error": "No questions found"}
    
    # Get all responses for this assessment
    responses = QuestionResponse.query.filter_by(assessment_id=assessment_id).all()
    if not responses:
        print(f"No responses found for assessment {assessment_id}")
        return {"error": "No responses found"}
    
    # Calculate scores for each SDG
    sdg_scores = {}
    for response in responses:
        question = db.session.get(Question, response.question_id)
        if question and question.sdg_id:
            sdg_id = question.sdg_id
            score = response.response_score or 0
            
            if sdg_id not in sdg_scores:
                sdg_scores[sdg_id] = {
                    "total_score": 0,
                    "response_count": 0
                }
            
            sdg_scores[sdg_id]["total_score"] += score
            sdg_scores[sdg_id]["response_count"] += 1
    
    # Calculate average scores and update the SdgScore records
    results = {}
    for sdg_id, data in sdg_scores.items():
        avg_score = data["total_score"] / data["response_count"] if data["response_count"] > 0 else 0
        
        # Update or create SdgScore record
        sdg_score = SdgScore.query.filter_by(assessment_id=assessment_id, sdg_id=sdg_id).first()
        if not sdg_score:
            sdg_score = SdgScore(assessment_id=assessment_id, sdg_id=sdg_id)
            db.session.add(sdg_score)
        
        sdg_score.score = avg_score
        
        # Add to results
        results[sdg_id] = {
            "score": avg_score,
            "response_count": data["response_count"]
        }
    
    # Calculate overall assessment score
    if sdg_scores:
        total_score = sum(data["score"] for data in results.values())
        overall_score = total_score / len(results)
        assessment.overall_score = overall_score
        results["overall_score"] = overall_score
    else:
        assessment.overall_score = 0
        results["overall_score"] = 0
    
    # Commit changes
    db.session.commit()
    
    return results
