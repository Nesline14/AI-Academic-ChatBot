from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db


class User(UserMixin, db.Model):
    """User model supporting Admin, Teacher, Student, and Club Coordinator roles."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    
    # Roles: 'admin', 'teacher', 'student', 'coordinator'
    role = db.Column(db.String(20), nullable=False, default='student', index=True)
    
    # Academic and Identification Info
    identifier = db.Column(db.String(50), unique=True, nullable=True)  # Student ID (Roll No) or Employee ID
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    semester = db.Column(db.Integer, nullable=True, default=1)
    phone = db.Column(db.String(20), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    avatar = db.Column(db.String(255), nullable=True, default='default-avatar.png')
    is_active_account = db.Column(db.Boolean, default=True)
    
    # Email Notification Preferences
    email_notifications_enabled = db.Column(db.Boolean, default=True)
    email_announcements = db.Column(db.Boolean, default=True)
    email_assignments = db.Column(db.Boolean, default=True)
    email_results = db.Column(db.Boolean, default=True)
    email_attendance = db.Column(db.Boolean, default=True)
    email_events = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    department = db.relationship('Department', backref='members', lazy=True)
    
    # Student specific
    enrollments = db.relationship('ClassStudent', back_populates='student', cascade='all, delete-orphan', lazy=True)
    attendances = db.relationship('Attendance', back_populates='student', foreign_keys='Attendance.student_id', cascade='all, delete-orphan', lazy=True)
    results = db.relationship('Result', back_populates='student', foreign_keys='Result.student_id', cascade='all, delete-orphan', lazy=True)
    submissions = db.relationship('AssignmentSubmission', back_populates='student', cascade='all, delete-orphan', lazy=True)
    event_registrations = db.relationship('EventRegistration', back_populates='user', cascade='all, delete-orphan', lazy=True)
    club_memberships = db.relationship('ClubMember', back_populates='student', cascade='all, delete-orphan', lazy=True)
    project_memberships = db.relationship('ProjectMember', back_populates='student', cascade='all, delete-orphan', lazy=True)
    notifications = db.relationship('Notification', back_populates='user', cascade='all, delete-orphan', lazy='dynamic')
    chat_logs = db.relationship('ChatMessage', back_populates='user', cascade='all, delete-orphan', lazy='dynamic')

    def set_password(self, password):
        """Hash and set user password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify user password against hash."""
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_teacher(self):
        return self.role == 'teacher'

    @property
    def is_student(self):
        return self.role == 'student'

    @property
    def is_coordinator(self):
        return self.role == 'coordinator'

    @property
    def role_badge_color(self):
        badges = {
            'admin': 'danger',
            'teacher': 'primary',
            'student': 'success',
            'coordinator': 'warning text-dark'
        }
        return badges.get(self.role, 'secondary')

    @property
    def role_display(self):
        names = {
            'admin': 'Administrator',
            'teacher': 'Faculty / Teacher',
            'student': 'Student',
            'coordinator': 'Club Coordinator'
        }
        return names.get(self.role, self.role.capitalize())

    def wants_email(self, category=None):
        """Check if user has opted into email notifications for a specific category."""
        if not self.email_notifications_enabled or not self.is_active_account:
            return False
        if not category:
            return True
        category = str(category).lower().strip()
        if category in ('announcement', 'announcements'):
            return bool(self.email_announcements)
        elif category in ('assignment', 'assignments', 'due_date', 'grade'):
            return bool(self.email_assignments)
        elif category in ('result', 'results', 'grades'):
            return bool(self.email_results)
        elif category in ('attendance', 'attendance_warning'):
            return bool(self.email_attendance)
        elif category in ('event', 'events'):
            return bool(self.email_events)
        return True

    def __repr__(self):
        return f'<User {self.email} ({self.role})>'
