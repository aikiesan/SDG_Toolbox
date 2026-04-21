"""
Assessment model.
Represents SDG assessments for architectural projects.
"""

from app import db
from datetime import datetime

class Assessment(db.Model):
    draft_data = db.Column(db.Text)  # Stores draft JSON data for assessments
    __tablename__ = 'assessments'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(32), default='draft')
    overall_score = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    step1_completed = db.Column(db.Boolean, default=False)
    step2_completed = db.Column(db.Boolean, default=False)
    step3_completed = db.Column(db.Boolean, default=False)
    step4_completed = db.Column(db.Boolean, default=False)
    step5_completed = db.Column(db.Boolean, default=False)
    
    # New columns for expert assessment support
    raw_expert_data = db.Column(db.JSON)  # Stores the raw JSON data from expert assessment form
    assessment_type = db.Column(db.String(50), default='standard')  # 'standard' or 'expert'

    # Shareable link support
    share_token = db.Column(db.String(64), unique=True, nullable=True)
    share_expires = db.Column(db.DateTime, nullable=True)

    project = db.relationship('Project', back_populates='assessments')
    sdg_scores = db.relationship('SdgScore', back_populates='assessment', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Assessment {self.id} for Project {self.project_id}>'

class SdgScore(db.Model):
    __tablename__ = 'sdg_scores'

    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id'), nullable=False)
    sdg_id = db.Column(db.Integer, db.ForeignKey('sdg_goals.id'), nullable=False)
    direct_score = db.Column(db.Float)  # Score from direct assessment
    bonus_score = db.Column(db.Float)   # Score from related SDGs
    total_score = db.Column(db.Float)   # Changed from final_score: Direct + Bonus (capped)
    raw_score = db.Column(db.Float)     # Sum of raw points from questions
    max_possible = db.Column(db.Float)  # Max possible raw points for the SDG
    percentage_score = db.Column(db.Float) # Raw / MaxPossible * 100
    question_count = db.Column(db.Integer) # Number of questions answered for this SDG
    response_text = db.Column(db.Text)  # Store original text response if applicable
    notes = db.Column(db.Text)          # Store notes entered directly for the score
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    assessment = db.relationship('Assessment', back_populates='sdg_scores')
    sdg_goal = db.relationship('SdgGoal', back_populates='sdg_scores')

    def __repr__(self):
        return f'<SdgScore id={self.id} assessment={self.assessment_id} sdg={self.sdg_id} total={self.total_score}>'
