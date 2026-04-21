from app import db

class SdgRelationship(db.Model):
    __tablename__ = 'sdg_relationships'
    id = db.Column(db.Integer, primary_key=True)
    source_sdg_id = db.Column(db.Integer, db.ForeignKey('sdg_goals.id'))
    target_sdg_id = db.Column(db.Integer, db.ForeignKey('sdg_goals.id'))

    # --- Added strength column ---
    strength = db.Column(db.Float, nullable=False, default=0.0)  # Add the strength column

    # back‐refs use string names
    source_goal = db.relationship(
        'SdgGoal',
        foreign_keys=[source_sdg_id],
        back_populates='source_rels'
    )
    target_goal = db.relationship(
        'SdgGoal',
        foreign_keys=[target_sdg_id],
        back_populates='target_rels'
    )
