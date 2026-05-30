from app import db
from datetime import datetime

# Import the correct QuestionResponse model instead of redefining it
from app.models.response import QuestionResponse
from app.models.sdg import SdgQuestion


def get_question_by_id(question_id):
    """Fetch an SDG question by its primary key (ORM)."""
    return db.session.get(SdgQuestion, question_id)


def get_question_response_by_id(response_id):
    """Fetch a question response by its primary key (ORM)."""
    return db.session.get(QuestionResponse, response_id)
