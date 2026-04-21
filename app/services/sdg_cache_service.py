"""
SDG Cache Service
Provides caching for static SDG data (goals, questions, relationships).
"""

from app import cache
from app.models.sdg import SdgGoal, SdgQuestion, SdgRelationship
from app import db


# Cache timeout: 1 hour (3600 seconds) for SDG data
SDG_CACHE_TIMEOUT = 3600


@cache.memoize(timeout=SDG_CACHE_TIMEOUT)
def get_all_sdg_goals():
    """
    Get all SDG goals with caching.
    Cache timeout: 1 hour (SDG goals rarely change)

    Returns:
        list: List of SdgGoal objects
    """
    return SdgGoal.query.order_by(SdgGoal.number).all()


@cache.memoize(timeout=SDG_CACHE_TIMEOUT)
def get_sdg_goal_by_id(sdg_id):
    """
    Get a specific SDG goal by ID with caching.

    Args:
        sdg_id (int): SDG goal ID

    Returns:
        SdgGoal: The SDG goal object or None
    """
    return db.session.get(SdgGoal, sdg_id)


@cache.memoize(timeout=SDG_CACHE_TIMEOUT)
def get_sdg_questions_by_goal(sdg_id):
    """
    Get all questions for a specific SDG goal with caching.

    Args:
        sdg_id (int): SDG goal ID

    Returns:
        list: List of SdgQuestion objects
    """
    return SdgQuestion.query.filter_by(sdg_id=sdg_id).order_by(SdgQuestion.display_order).all()


@cache.memoize(timeout=SDG_CACHE_TIMEOUT)
def get_all_sdg_questions():
    """
    Get all SDG questions with caching.

    Returns:
        list: List of all SdgQuestion objects
    """
    return SdgQuestion.query.order_by(SdgQuestion.display_order).all()


@cache.memoize(timeout=SDG_CACHE_TIMEOUT)
def get_all_sdg_relationships():
    """
    Get all SDG relationships with caching.

    Returns:
        list: List of all SdgRelationship objects
    """
    return SdgRelationship.query.all()


@cache.memoize(timeout=SDG_CACHE_TIMEOUT)
def get_sdg_relationships_by_source(source_sdg_id):
    """
    Get relationships where a specific SDG is the source.

    Args:
        source_sdg_id (int): Source SDG ID

    Returns:
        list: List of SdgRelationship objects
    """
    return SdgRelationship.query.filter_by(source_sdg_id=source_sdg_id).order_by(
        SdgRelationship.strength.desc()
    ).all()


def invalidate_sdg_cache():
    """
    Clear all SDG-related caches.
    Call this when SDG data is updated (e.g., admin modifies goals/questions).
    """
    cache.delete_memoized(get_all_sdg_goals)
    cache.delete_memoized(get_sdg_goal_by_id)
    cache.delete_memoized(get_sdg_questions_by_goal)
    cache.delete_memoized(get_all_sdg_questions)
    cache.delete_memoized(get_all_sdg_relationships)
    cache.delete_memoized(get_sdg_relationships_by_source)


def warm_sdg_cache():
    """
    Pre-populate SDG caches with data.
    Useful to call after application startup or cache invalidation.
    """
    # Warm up common caches
    get_all_sdg_goals()
    get_all_sdg_questions()
    get_all_sdg_relationships()

    # Warm up individual goal caches
    goals = get_all_sdg_goals()
    for goal in goals:
        get_sdg_goal_by_id(goal.id)
        get_sdg_questions_by_goal(goal.id)
        get_sdg_relationships_by_source(goal.id)
