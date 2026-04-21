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

# Old raw SQL methods removed for ORM migration.

        projects = []
        for project_data in projects_data:
            project = Project(
                id=project_data['id'],
                name=project_data['name'],
                description=project_data['description'],
                project_type=project_data['project_type'],
                location=project_data['location'],
                size_sqm=project_data['size_sqm'],
                user_id=project_data['user_id'],
                created_at=project_data['created_at'],
                updated_at=project_data['updated_at'],
                start_date=project_data.get('start_date'),
                end_date=project_data.get('end_date'),
                budget=project_data.get('budget'),
                sector=project_data.get('sector')
            )
            # Add assessment count as an attribute
            project.assessment_count = project_data['assessment_count']
            projects.append(project)
        return projects

    def save(self):
        """Save the project to the database (create or update)."""
        conn = get_db()
        if self.id:
            # Update existing project
            conn.execute('''
                UPDATE projects
                SET name = ?, description = ?, project_type = ?, location = ?, size_sqm = ?, 
                    start_date = ?, end_date = ?, budget = ?, sector = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND user_id = ?
            ''', (self.name, self.description, self.project_type, self.location, self.size_sqm,
                  self.start_date, self.end_date, self.budget, self.sector, self.id, self.user_id))
        else:
            # Create new project
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO projects (name, description, project_type, location, size_sqm, user_id, 
                                    start_date, end_date, budget, sector, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ''', (self.name, self.description, self.project_type, self.location, self.size_sqm, self.user_id,
                  self.start_date, self.end_date, self.budget, self.sector))
            self.id = cursor.lastrowid
        conn.commit()
        return self

    def delete(self):
        """Delete the project and all its assessments."""
        conn = get_db()
        # Delete all related assessment data first
        conn.execute('DELETE FROM sdg_actions WHERE assessment_id IN (SELECT id FROM assessments WHERE project_id = ?)', (self.id,))
        conn.execute('DELETE FROM sdg_scores WHERE assessment_id IN (SELECT id FROM assessments WHERE project_id = ?)', (self.id,))
        conn.execute('DELETE FROM question_responses WHERE assessment_id IN (SELECT id FROM assessments WHERE project_id = ?)', (self.id,))
        conn.execute('DELETE FROM assessments WHERE project_id = ?', (self.id,))
        # Then delete the project
        conn.execute('DELETE FROM projects WHERE id = ?', (self.id,))
        conn.commit()
