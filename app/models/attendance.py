from datetime import datetime, date
from extensions import db


class Attendance(db.Model):
    """Daily/Session student attendance records."""
    __tablename__ = 'attendance'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False, index=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, default=date.today, index=True)
    
    # Status: 'Present', 'Absent', 'Late'
    status = db.Column(db.String(20), nullable=False, default='Present')
    marked_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    remarks = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    student = db.relationship('User', foreign_keys=[student_id], back_populates='attendances')
    marked_by = db.relationship('User', foreign_keys=[marked_by_id])
    classroom = db.relationship('ClassRoom', back_populates='attendances')
    subject = db.relationship('Subject', backref='attendances')

    @property
    def status_badge_class(self):
        badges = {
            'Present': 'success',
            'Absent': 'danger',
            'Late': 'warning text-dark'
        }
        return badges.get(self.status, 'secondary')

    def __repr__(self):
        return f'<Attendance Student:{self.student_id} Subject:{self.subject_id} Date:{self.date} Status:{self.status}>'
