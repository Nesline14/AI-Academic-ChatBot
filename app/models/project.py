from datetime import datetime
from extensions import db


class AcademicProject(db.Model):
    """Student capstone, mini, and academic research projects."""
    __tablename__ = 'academic_projects'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    # Category: 'Web Development', 'Machine Learning', 'IoT', 'Mobile App', 'Research', 'Embedded Systems', 'Cloud Computing'
    category = db.Column(db.String(50), default='Web Development')
    
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    guide_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Teacher mentor
    
    deadline = db.Column(db.Date, nullable=True)
    
    # Status: 'Planning', 'In Progress', 'Completed', 'On Hold'
    status = db.Column(db.String(30), default='Planning')
    progress_percentage = db.Column(db.Integer, default=10)
    
    repository_url = db.Column(db.String(255), nullable=True)
    documentation_url = db.Column(db.String(255), nullable=True)
    feedback = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    creator = db.relationship('User', foreign_keys=[creator_id], backref='created_projects')
    guide = db.relationship('User', foreign_keys=[guide_id], backref='guided_projects')
    members = db.relationship('ProjectMember', back_populates='project', cascade='all, delete-orphan', lazy=True)

    @property
    def status_badge_class(self):
        badges = {
            'Planning': 'secondary',
            'In Progress': 'primary',
            'Completed': 'success',
            'On Hold': 'warning text-dark'
        }
        return badges.get(self.status, 'secondary')

    def is_member(self, user_id):
        if self.creator_id == user_id:
            return True
        return any(m.student_id == user_id for m in self.members)

    def __repr__(self):
        return f'<AcademicProject {self.title} Status:{self.status}>'


class ProjectMember(db.Model):
    """Team members collaborating on an academic project."""
    __tablename__ = 'project_members'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('academic_projects.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role_in_project = db.Column(db.String(50), default='Developer')  # e.g., 'Lead', 'Backend', 'UI/UX', 'Researcher'
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

    project = db.relationship('AcademicProject', back_populates='members')
    student = db.relationship('User', back_populates='project_memberships')

    def __repr__(self):
        return f'<ProjectMember Project:{self.project_id} Student:{self.student_id}>'
