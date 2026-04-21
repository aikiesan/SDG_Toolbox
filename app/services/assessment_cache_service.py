"""
Assessment Cache Service
Provides caching for assessment results and related data.
"""

from app import cache, db
from app.models.assessment import Assessment, SdgScore
from app.models.project import Project


# Cache timeout: 10 minutes for assessment results
ASSESSMENT_CACHE_TIMEOUT = 600


@cache.memoize(timeout=ASSESSMENT_CACHE_TIMEOUT)
def get_assessment_results(assessment_id):
    """
    Get complete assessment results with all SDG scores (cached).

    Args:
        assessment_id (int): Assessment ID

    Returns:
        dict: Assessment results with scores, or None if not found
    """
    assessment = db.session.get(Assessment, assessment_id)
    if not assessment:
        return None

    # Get SDG scores with eager loading
    sdg_scores = db.session.query(SdgScore).filter_by(
        assessment_id=assessment_id
    ).join(SdgScore.sdg_goal).all()

    # Format scores for display
    formatted_scores = []
    for score in sdg_scores:
        formatted_scores.append({
            'sdg_id': score.sdg_id,
            'sdg_number': score.sdg_goal.number,
            'sdg_name': score.sdg_goal.name,
            'sdg_color': score.sdg_goal.color_code,
            'direct_score': round(score.direct_score, 2) if score.direct_score else 0,
            'bonus_score': round(score.bonus_score, 2) if score.bonus_score else 0,
            'total_score': round(score.total_score, 2) if score.total_score else 0,
            'percentage_score': round(score.percentage_score, 2) if score.percentage_score else 0,
            'question_count': score.question_count or 0
        })

    # Sort by SDG number
    formatted_scores.sort(key=lambda x: x['sdg_number'])

    return {
        'assessment_id': assessment.id,
        'project_id': assessment.project_id,
        'overall_score': round(assessment.overall_score, 2) if assessment.overall_score else 0,
        'status': assessment.status,
        'completed_at': assessment.completed_at,
        'sdg_scores': formatted_scores
    }


@cache.memoize(timeout=ASSESSMENT_CACHE_TIMEOUT)
def get_assessment_summary(assessment_id):
    """
    Get assessment summary statistics (cached).

    Args:
        assessment_id (int): Assessment ID

    Returns:
        dict: Summary statistics
    """
    assessment = db.session.get(Assessment, assessment_id)
    if not assessment:
        return None

    sdg_scores = db.session.query(SdgScore).filter_by(assessment_id=assessment_id).all()

    # Calculate statistics
    total_scores = [s.total_score for s in sdg_scores if s.total_score]
    direct_scores = [s.direct_score for s in sdg_scores if s.direct_score]
    bonus_scores = [s.bonus_score for s in sdg_scores if s.bonus_score]

    return {
        'assessment_id': assessment_id,
        'overall_score': round(assessment.overall_score, 2) if assessment.overall_score else 0,
        'avg_direct_score': round(sum(direct_scores) / len(direct_scores), 2) if direct_scores else 0,
        'avg_bonus_score': round(sum(bonus_scores) / len(bonus_scores), 2) if bonus_scores else 0,
        'max_score': round(max(total_scores), 2) if total_scores else 0,
        'min_score': round(min(total_scores), 2) if total_scores else 0,
        'sdg_count': len(sdg_scores)
    }


@cache.memoize(timeout=900)  # 15 minutes
def get_project_assessments_summary(project_id):
    """
    Get summary of all assessments for a project (cached).

    Args:
        project_id (int): Project ID

    Returns:
        dict: Project assessments summary
    """
    assessments = db.session.query(Assessment).filter_by(
        project_id=project_id
    ).order_by(Assessment.created_at.desc()).all()

    completed_assessments = [a for a in assessments if a.status == 'completed']
    overall_scores = [a.overall_score for a in completed_assessments if a.overall_score]

    return {
        'project_id': project_id,
        'total_assessments': len(assessments),
        'completed_assessments': len(completed_assessments),
        'draft_assessments': len([a for a in assessments if a.status == 'draft']),
        'avg_overall_score': round(sum(overall_scores) / len(overall_scores), 2) if overall_scores else 0,
        'latest_score': overall_scores[0] if overall_scores else None
    }


def invalidate_assessment_cache(assessment_id):
    """
    Clear cache for a specific assessment.
    Call this when assessment data is updated or recalculated.

    Args:
        assessment_id (int): Assessment ID
    """
    cache.delete_memoized(get_assessment_results, assessment_id)
    cache.delete_memoized(get_assessment_summary, assessment_id)

    # Also invalidate project summary if we know the project
    assessment = db.session.get(Assessment, assessment_id)
    if assessment:
        cache.delete_memoized(get_project_assessments_summary, assessment.project_id)


def invalidate_project_assessments_cache(project_id):
    """
    Clear cache for all assessments in a project.
    Call this when project assessments are modified.

    Args:
        project_id (int): Project ID
    """
    cache.delete_memoized(get_project_assessments_summary, project_id)

    # Invalidate individual assessment caches
    assessments = db.session.query(Assessment).filter_by(project_id=project_id).all()
    for assessment in assessments:
        cache.delete_memoized(get_assessment_results, assessment.id)
        cache.delete_memoized(get_assessment_summary, assessment.id)


def clear_all_assessment_caches():
    """
    Clear all assessment-related caches.
    Use sparingly - only when needed (e.g., data migration).
    """
    # This will clear ALL cached data, not just assessments
    cache.clear()
