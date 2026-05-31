"""Tests for the SDG scoring service — the product's core calculation path.

Covers the pure scoring helpers plus an end-to-end run of calculate_sdg_scores
and get_assessment_summary against the seeded test database (17 goals,
31 questions).
"""
import pytest

from app import db
from app.models.assessment import Assessment, SdgScore
from app.models.response import QuestionResponse
from app.models.sdg import SdgQuestion
from app.services import scoring_service


# ---------------------------------------------------------------------------
# map_option_to_score
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("value,expected", [
    ('strongly agree', 5.0),
    ('Agree', 4.0),
    ('neutral', 3.0),
    ('disagree', 2.0),
    ('strongly disagree', 1.0),
    ('yes', 5.0),
    ('no', 0.0),
    ('partially', 3.0),
    ('4', 4.0),          # numeric string passes through
    (2, 2.0),            # numeric value
    ('', 0.0),           # empty
    (None, 0.0),         # none
    ('some checkbox label', 1.0),  # unmatched non-empty -> default 1.0
])
def test_map_option_to_score(value, expected):
    assert scoring_service.map_option_to_score(value) == expected


# ---------------------------------------------------------------------------
# process_question_response
# ---------------------------------------------------------------------------

def test_process_select_response():
    assert scoring_service.process_question_response('select', '4', None, 5) == 4.0
    # capped at max_score
    assert scoring_service.process_question_response('select', '9', None, 5) == 5.0
    # non-numeric -> 0
    assert scoring_service.process_question_response('select', 'nope', None, 5) == 0


def test_process_checklist_response():
    # 1 point per selection by default
    assert scoring_service.process_question_response('checklist', '["a", "b"]', None, 5) == 2
    # empty list -> 0
    assert scoring_service.process_question_response('checklist', '[]', None, 5) == 0
    # invalid JSON -> 0
    assert scoring_service.process_question_response('checklist', 'not-json', None, 5) == 0
    # capped at max_score
    assert scoring_service.process_question_response('checklist', '["a","b","c","d","e","f"]', None, 5) == 5


def test_process_unknown_type_returns_zero():
    assert scoring_service.process_question_response('mystery', 'x') == 0


# ---------------------------------------------------------------------------
# calculate_sdg_scores (integration)
# ---------------------------------------------------------------------------

def _assessment(session, test_project):
    a = Assessment(project_id=test_project.id, user_id=test_project.user_id, status='draft')
    session.add(a)
    session.flush()
    return a


def test_calculate_scores_with_no_responses(session, test_project):
    a = _assessment(session, test_project)
    result = scoring_service.calculate_sdg_scores(a.id)
    assert result['overall_score'] == 0
    # A zeroed SdgScore row is created for every goal.
    assert SdgScore.query.filter_by(assessment_id=a.id).count() == 17
    assert db.session.get(Assessment, a.id).overall_score == 0


def test_calculate_scores_with_responses(session, test_project):
    a = _assessment(session, test_project)
    # Answer the three questions that map to SDG 1 with full marks.
    sdg1_questions = SdgQuestion.query.filter_by(sdg_id=1).all()
    assert sdg1_questions, "expected seeded questions for SDG 1"
    for q in sdg1_questions:
        session.add(QuestionResponse(
            assessment_id=a.id, question_id=q.id,
            response_score=float(q.max_score or 5.0), response_text='5',
        ))
    session.flush()

    result = scoring_service.calculate_sdg_scores(a.id)

    assert result['overall_score'] > 0
    # SDG 1 should have a strong (capped) score; an unanswered SDG should be 0.
    goal1 = SdgScore.query.filter_by(assessment_id=a.id, sdg_id=1).first()
    assert goal1 is not None
    assert goal1.total_score > 0
    assert goal1.question_count == len(sdg1_questions)
    assert db.session.get(Assessment, a.id).overall_score == result['overall_score']


def test_calculate_scores_missing_assessment_returns_empty():
    result = scoring_service.calculate_sdg_scores(999999)
    assert result == {'sdg_scores': {}, 'overall_score': 0}


# ---------------------------------------------------------------------------
# get_assessment_summary (ORM port — previously broken under SQLAlchemy 2.0)
# ---------------------------------------------------------------------------

def test_get_assessment_summary(session, completed_assessment):
    summary = scoring_service.get_assessment_summary(db.session, completed_assessment.id)
    assert 'error' not in summary
    assert summary['assessment']['id'] == completed_assessment.id
    assert summary['overall_score'] == completed_assessment.overall_score
    assert isinstance(summary['scores'], list) and len(summary['scores']) == 5
    assert set(summary['categories'].keys()) == {
        'People', 'Planet', 'Prosperity', 'Peace & Partnership'
    }
    # chart_data mirrors the score list
    assert len(summary['chart_data']) == len(summary['scores'])


def test_get_assessment_summary_missing():
    assert scoring_service.get_assessment_summary(db.session, 999999) == {'error': 'Assessment not found'}
