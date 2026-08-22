from datetime import datetime
from extensions import db


class Assignment(db.Model):
    """Academic coursework, assignments, and homework tasks."""
    __tablename__ = 'assignments'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    max_marks = db.Column(db.Float, default=100.0)
    due_date = db.Column(db.DateTime, nullable=False)
    file_path = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    classroom = db.relationship('ClassRoom', back_populates='assignments')
    subject = db.relationship('Subject', backref='assignments')
    teacher = db.relationship('User', backref='assignments_created')
    submissions = db.relationship('AssignmentSubmission', back_populates='assignment', cascade='all, delete-orphan', lazy=True)

    @property
    def is_overdue(self):
        return datetime.utcnow() > self.due_date

    def get_submission_for_student(self, student_id):
        return next((s for s in self.submissions if s.student_id == student_id), None)

    def __repr__(self):
        return f'<Assignment {self.title} Due:{self.due_date}>'


class AssignmentSubmission(db.Model):
    """Student homework submission records."""
    __tablename__ = 'assignment_submissions'

    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    submission_text = db.Column(db.Text, nullable=True)
    file_path = db.Column(db.String(255), nullable=True)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    marks_obtained = db.Column(db.Float, nullable=True)
    feedback = db.Column(db.Text, nullable=True)
    
    # Status: 'Pending', 'Submitted', 'Late', 'Graded'
    status = db.Column(db.String(20), default='Submitted')

    # Relationships
    assignment = db.relationship('Assignment', back_populates='submissions')
    student = db.relationship('User', back_populates='submissions')

    @property
    def status_badge_class(self):
        badges = {
            'Pending': 'warning text-dark',
            'Submitted': 'info',
            'Late': 'secondary',
            'Graded': 'success'
        }
        return badges.get(self.status, 'secondary')

    def __repr__(self):
        return f'<AssignmentSubmission Assignment:{self.assignment_id} Student:{self.student_id} Status:{self.status}>'
