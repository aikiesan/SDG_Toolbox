"""
SDG Goal model.
Represents Sustainable Development Goals and their relationships.
"""

from app.utils.db import get_db

from app import db
from datetime import datetime

class SdgGoal(db.Model):
    __tablename__ = 'sdg_goals'
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer)
    name = db.Column(db.String(255))
    description = db.Column(db.Text)
    color_code = db.Column(db.String(16))
    icon = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    questions = db.relationship('SdgQuestion', back_populates='sdg', lazy=True)
    source_rels = db.relationship(
        'SdgRelationship',
        foreign_keys='SdgRelationship.source_sdg_id',
        back_populates='source_goal'
    )
    target_rels = db.relationship(
        'SdgRelationship',
        foreign_keys='SdgRelationship.target_sdg_id',
        back_populates='target_goal'
    )

class SdgQuestion(db.Model):
    __tablename__ = 'sdg_questions'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(64))
    sdg_id = db.Column(db.Integer, db.ForeignKey('sdg_goals.id'), nullable=False)
    options = db.Column(db.Text)
    display_order = db.Column(db.Integer)
    max_score = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    sdg = db.relationship('SdgGoal', back_populates='questions')

# Remove any duplicate SdgQuestion class definitions below this point.
# Define relationships after all models are defined (late binding)
SdgGoal.sdg_scores = db.relationship('SdgScore', back_populates='sdg_goal', cascade='all, delete-orphan')
