"""
Project model.
Represents architectural projects in the application.
"""

from app import db
from datetime import datetime
from sqlalchemy.orm import validates

class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    project_type = db.Column(db.String(100))
    location = db.Column(db.String(255))
    size_sqm = db.Column(db.Float)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    budget = db.Column(db.Float)
    sector = db.Column(db.String(100))
    status = db.Column(db.String(50), nullable=True, default='planning')

    user = db.relationship('User', back_populates='projects')
    assessments = db.relationship('Assessment', back_populates='project', cascade='all, delete-orphan')

    @property
    def assessment_count(self):
        """Return the number of assessments for this project."""
        return len(self.assessments)

    @validates('size_sqm')
    def validate_size_sqm(self, key, value):
        if value is not None:
            if not isinstance(value, (int, float)):
                raise ValueError("Size must be a number.")
            if value <= 0:
                raise ValueError("Size must be a positive number.")
            if value > 1000000:
                raise ValueError("Size must be less than 1,000,000 sq meters.")
        return value
    
    @validates('budget')
    def validate_budget(self, key, value):
        if value is not None:
            if not isinstance(value, (int, float)):
                raise ValueError("Budget must be a number.")
            if value <= 0:
                raise ValueError("Budget must be a positive number.")
        return value
    
    @validates('end_date')
    def validate_end_date(self, key, value):
        if value is not None and self.start_date is not None:
            if value < self.start_date:
                raise ValueError("End date must be after start date.")
        return value
    
    @validates('name')
    def validate_name(self, key, value):
        if not value:
            raise ValueError("Project name is required.")
        if len(value) > 100:
            raise ValueError("Project name must be less than 100 characters.")
        return value
    
    @validates('description')
    def validate_description(self, key, value):
        if value and len(value) > 500:
            raise ValueError("Description must be less than 500 characters.")
        return value
    
    @validates('location')
    def validate_location(self, key, value):
        if value and len(value) > 255:
            raise ValueError("Location must be less than 255 characters.")
        return value
    
    @validates('sector')
    def validate_sector(self, key, value):
        valid_sectors = [
            'Residential', 'Commercial', 'Education', 'Healthcare', 
            'Transportation', 'Technology', 'Energy', 'Industrial',
            'Agriculture', 'Entertainment', 'Hospitality', 'Public', 'Other'
        ]
        if value and value not in [s.lower() for s in valid_sectors]:
            return value.title() if value.title() in valid_sectors else value
        return value

    def __repr__(self):
        return f'<Project {self.name}>'

    def save(self):
        """Persist the project (create or update) via the ORM session."""
        db.session.add(self)
        db.session.commit()
        return self

    def delete(self):
        """Delete the project; related assessments cascade via the relationship."""
        db.session.delete(self)
        db.session.commit()
