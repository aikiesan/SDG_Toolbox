from app import db
from datetime import datetime

class QuestionResponse(db.Model):
    __tablename__ = 'question_responses'

    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('sdg_questions.id'), nullable=False)
    response_score = db.Column(db.Float)
    response_text = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships (optional but good practice)
    assessment = db.relationship('Assessment')
    question = db.relationship('SdgQuestion')

    def __repr__(self):
        return f'<QuestionResponse id={self.id} assessment={self.assessment_id} q={self.question_id} score={self.response_score}>'
