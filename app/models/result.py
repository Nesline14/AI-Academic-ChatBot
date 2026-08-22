from datetime import datetime
from extensions import db


class Result(db.Model):
    """Academic grade and examination results."""
    __tablename__ = 'results'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False, index=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False, index=True)
    semester = db.Column(db.Integer, nullable=False, default=1)
    
    # Marks breakdown
    internal_marks = db.Column(db.Float, default=0.0)      # Max usually 25-30
    assignment_marks = db.Column(db.Float, default=0.0)    # Max usually 20-25
    exam_marks = db.Column(db.Float, default=0.0)          # Max usually 50-60
    total_marks = db.Column(db.Float, nullable=False, default=0.0)
    max_marks = db.Column(db.Float, nullable=False, default=100.0)
    
    grade = db.Column(db.String(5), nullable=False, default='F')  # A+, A, B+, B, C, P, F
    gpa_points = db.Column(db.Float, default=0.0)                 # Scale 0.0 - 10.0
    remarks = db.Column(db.String(255), nullable=True)
    
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    result_date = db.Column(db.Date, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student = db.relationship('User', foreign_keys=[student_id], back_populates='results')
    teacher = db.relationship('User', foreign_keys=[teacher_id])
    subject = db.relationship('Subject', backref='results')
    classroom = db.relationship('ClassRoom', back_populates='results')

    @property
    def percentage(self):
        if self.max_marks > 0:
            return round((self.total_marks / self.max_marks) * 100, 2)
        return 0.0

    @property
    def grade_badge_class(self):
        if self.grade in ['A+', 'A']:
            return 'success'
        elif self.grade in ['B+', 'B']:
            return 'primary'
        elif self.grade in ['C+', 'C']:
            return 'info'
        elif self.grade in ['D', 'P']:
            return 'warning text-dark'
        return 'danger'

    @staticmethod
    def calculate_grade_and_gpa(total, max_m=100.0):
        pct = (total / max_m) * 100.0 if max_m > 0 else 0
        if pct >= 90:
            return 'A+', 10.0
        elif pct >= 80:
            return 'A', 9.0
        elif pct >= 70:
            return 'B+', 8.0
        elif pct >= 60:
            return 'B', 7.0
        elif pct >= 50:
            return 'C', 6.0
        elif pct >= 40:
            return 'P', 5.0
        else:
            return 'F', 0.0

    def __repr__(self):
        return f'<Result Student:{self.student_id} Subject:{self.subject_id} Total:{self.total_marks} Grade:{self.grade}>'
