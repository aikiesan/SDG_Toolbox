from app import db
from datetime import datetime

# Import the correct QuestionResponse model instead of redefining it
from app.models.response import QuestionResponse

# Existing raw SQL helpers below

# Example helper for fetching a question by ID
def get_question_by_id(question_id):
    from app.utils.db import get_db
    conn = get_db()
    data = conn.execute('SELECT * FROM questions WHERE id = ?', (question_id,)).fetchone()
    # conn.close() removed; teardown handles DB connection.
    return data

# Example helper for fetching a response by ID
def get_question_response_by_id(response_id):
    from app.utils.db import get_db
    conn = get_db()
    data = conn.execute('SELECT * FROM question_responses WHERE id = ?', (response_id,)).fetchone()
    # conn.close() removed; teardown handles DB connection.
    return data
