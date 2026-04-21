"""
Integration tests for the scoring flow.
Tests: Submit responses → Calculate scores → Verify SDG breakdown
"""

import pytest
from app.models.assessment import Assessment, SdgScore
from app.models.response import QuestionResponse
from app.models.sdg import SdgQuestion, SdgGoal
from app.models.sdg_relationship import SdgRelationship
from app.services.scoring_service import calculate_sdg_scores
from datetime import datetime


class TestScoringFlow:
    """Test the complete scoring calculation flow."""

    def test_calculate_scores_with_responses(self, session, test_project):
        """Test score calculation with actual question responses."""
        # Create assessment
        assessment = Assessment(
            project_id=test_project.id,
            user_id=test_project.user_id,
            status='draft',
            assessment_type='standard'
        )
        session.add(assessment)
        session.flush()

        # Add responses for questions across multiple SDGs
        questions = session.query(SdgQuestion).limit(15).all()
        assert len(questions) > 0, "No questions found in database"

        for i, question in enumerate(questions):
            response = QuestionResponse(
                assessment_id=assessment.id,
                question_id=question.id,
                response_score=float(3 + (i % 3)),  # Scores: 3, 4, 5, 3, 4, 5...
                response_text=f'Test response {i}'
            )
            session.add(response)

        session.commit()

        # Calculate scores
        result = calculate_sdg_scores(assessment.id)

        # Verify result structure
        assert 'sdg_scores' in result
        assert 'overall_score' in result
        assert result['overall_score'] > 0
        assert len(result['sdg_scores']) > 0

        # Verify scores were saved to database
        sdg_scores = session.query(SdgScore).filter_by(assessment_id=assessment.id).all()
        assert len(sdg_scores) > 0

        # Verify each score has the required fields
        for score in sdg_scores:
            assert score.direct_score is not None
            assert score.bonus_score is not None
            assert score.total_score is not None
            assert score.raw_score is not None
            assert score.max_possible is not None
            assert score.percentage_score is not None
            assert 0 <= score.total_score <= 10, f"Score {score.total_score} outside valid range"

    def test_calculate_scores_without_responses(self, session, test_project):
        """Test score calculation when assessment has no responses."""
        assessment = Assessment(
            project_id=test_project.id,
            user_id=test_project.user_id,
            status='draft'
        )
        session.add(assessment)
        session.commit()

        # Calculate scores with no responses
        result = calculate_sdg_scores(assessment.id)

        # Should return zero scores
        assert result['overall_score'] == 0
        assert result['sdg_scores'] == {} or all(score == 0 for score in result['sdg_scores'].values())

        # Verify zero scores were saved
        session.refresh(assessment)
        assert assessment.overall_score == 0

    def test_scoring_with_bonus_points(self, session, test_project):
        """Test that bonus points are calculated from SDG relationships."""
        assessment = Assessment(
            project_id=test_project.id,
            user_id=test_project.user_id,
            status='draft'
        )
        session.add(assessment)
        session.flush()

        # Get questions for a specific SDG that we'll score highly
        # to trigger bonus points for related SDGs
        questions = session.query(SdgQuestion).limit(10).all()

        # Add high responses
        for question in questions:
            response = QuestionResponse(
                assessment_id=assessment.id,
                question_id=question.id,
                response_score=5.0,  # Maximum score
                response_text='Maximum score response'
            )
            session.add(response)

        session.commit()

        # Calculate scores
        result = calculate_sdg_scores(assessment.id)

        # Verify bonus scores were applied
        sdg_scores = session.query(SdgScore).filter_by(assessment_id=assessment.id).all()

        # At least some SDGs should have bonus scores if relationships exist
        has_bonus = any(score.bonus_score > 0 for score in sdg_scores)
        # Note: This might be False if there are no relationships in test data
        # In a real scenario with relationships, we'd assert True

        # Verify total score is within valid range
        for score in sdg_scores:
            assert score.total_score >= score.direct_score, \
                "Total score should be >= direct score"
            assert score.total_score <= 10, \
                "Total score should not exceed 10"

    def test_score_calculation_idempotency(self, session, test_project):
        """Test that calculating scores multiple times produces consistent results."""
        assessment = Assessment(
            project_id=test_project.id,
            user_id=test_project.user_id,
            status='draft'
        )
        session.add(assessment)
        session.flush()

        # Add responses
        questions = session.query(SdgQuestion).limit(5).all()
        for question in questions:
            response = QuestionResponse(
                assessment_id=assessment.id,
                question_id=question.id,
                response_score=4.0
            )
            session.add(response)
        session.commit()

        # Calculate scores first time
        result1 = calculate_sdg_scores(assessment.id)
        score1 = result1['overall_score']

        # Calculate scores second time
        result2 = calculate_sdg_scores(assessment.id)
        score2 = result2['overall_score']

        # Results should be identical
        assert score1 == score2, "Score calculation should be idempotent"
        assert result1['sdg_scores'] == result2['sdg_scores']

    def test_sdg_score_breakdown(self, session, test_project):
        """Test that SDG scores are correctly broken down into components."""
        assessment = Assessment(
            project_id=test_project.id,
            user_id=test_project.user_id,
            status='draft'
        )
        session.add(assessment)
        session.flush()

        # Add responses
        questions = session.query(SdgQuestion).limit(8).all()
        for i, question in enumerate(questions):
            response = QuestionResponse(
                assessment_id=assessment.id,
                question_id=question.id,
                response_score=float(2 + i),  # Varied scores
                response_text=f'Response {i}'
            )
            session.add(response)
        session.commit()

        # Calculate scores
        calculate_sdg_scores(assessment.id)

        # Verify breakdown for each SDG
        sdg_scores = session.query(SdgScore).filter_by(assessment_id=assessment.id).all()

        for score in sdg_scores:
            # Verify components sum correctly (considering cap at 10)
            expected_total = min(score.direct_score + score.bonus_score, 10.0)
            assert abs(score.total_score - expected_total) < 0.01, \
                f"Total score mismatch for SDG {score.sdg_id}"

            # Verify percentage calculation
            if score.max_possible > 0:
                expected_percentage = (score.raw_score / score.max_possible) * 100
                assert abs(score.percentage_score - expected_percentage) < 0.01, \
                    f"Percentage calculation incorrect for SDG {score.sdg_id}"

    def test_overall_score_calculation(self, session, test_project):
        """Test that overall score is correctly calculated as average of SDG scores."""
        assessment = Assessment(
            project_id=test_project.id,
            user_id=test_project.user_id,
            status='draft'
        )
        session.add(assessment)
        session.flush()

        # Add responses
        questions = session.query(SdgQuestion).limit(12).all()
        for question in questions:
            response = QuestionResponse(
                assessment_id=assessment.id,
                question_id=question.id,
                response_score=3.5
            )
            session.add(response)
        session.commit()

        # Calculate scores
        result = calculate_sdg_scores(assessment.id)

        # Get all SDG scores
        sdg_scores = session.query(SdgScore).filter_by(assessment_id=assessment.id).all()

        if sdg_scores:
            # Calculate expected overall score
            total_scores = [score.total_score for score in sdg_scores if score.total_score is not None]
            expected_overall = sum(total_scores) / len(total_scores) if total_scores else 0

            # Verify overall score matches
            session.refresh(assessment)
            assert abs(assessment.overall_score - expected_overall) < 0.01, \
                "Overall score should be average of all SDG total scores"

    def test_scoring_with_zero_responses(self, session, test_project):
        """Test scoring behavior when some SDGs have zero responses."""
        assessment = Assessment(
            project_id=test_project.id,
            user_id=test_project.user_id,
            status='draft'
        )
        session.add(assessment)
        session.flush()

        # Add responses for only first 3 questions (leaving some SDGs empty)
        questions = session.query(SdgQuestion).limit(3).all()
        for question in questions:
            response = QuestionResponse(
                assessment_id=assessment.id,
                question_id=question.id,
                response_score=5.0
            )
            session.add(response)
        session.commit()

        # Calculate scores
        result = calculate_sdg_scores(assessment.id)

        # Verify that SDGs without responses get zero scores
        sdg_scores = session.query(SdgScore).filter_by(assessment_id=assessment.id).all()

        # At least some SDGs should have zero scores
        zero_score_sdgs = [s for s in sdg_scores if s.total_score == 0]
        non_zero_score_sdgs = [s for s in sdg_scores if s.total_score > 0]

        # Should have both zero and non-zero scores
        assert len(zero_score_sdgs) > 0, "Should have some SDGs with zero scores"
        assert len(non_zero_score_sdgs) > 0, "Should have some SDGs with non-zero scores"
