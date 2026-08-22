from datetime import datetime
from extensions import db


class Department(db.Model):
    """Academic Department (e.g. Computer Science, Mechanical Eng)."""
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    courses = db.relationship('Course', backref='department', cascade='all, delete-orphan', lazy=True)
    classes = db.relationship('ClassRoom', backref='department', cascade='all, delete-orphan', lazy=True)
    subjects = db.relationship('Subject', backref='department', cascade='all, delete-orphan', lazy=True)

    def __repr__(self):
        return f'<Department {self.code} - {self.name}>'


class Course(db.Model):
    """Academic Degree / Course Program (e.g., B.Tech Computer Science)."""
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    total_semesters = db.Column(db.Integer, default=8)
    credits = db.Column(db.Integer, default=160)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Course {self.code} - {self.name}>'


class Subject(db.Model):
    """Subject / Course Module (e.g., Data Structures, Database Systems)."""
    __tablename__ = 'subjects'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    semester = db.Column(db.Integer, default=1)
    credits = db.Column(db.Integer, default=4)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Subject {self.code} - {self.name}>'


class ClassRoom(db.Model):
    """Cohort / Academic Class Section (e.g., CS 3rd Year - Sec A)."""
    __tablename__ = 'classes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # e.g., "CSE-3A"
    code = db.Column(db.String(30), unique=True, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    semester = db.Column(db.Integer, default=1)
    section = db.Column(db.String(10), default='A')
    academic_year = db.Column(db.String(20), default='2025-2026')
    
    # Class Advisor / Lead Teacher
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    teacher = db.relationship('User', foreign_keys=[teacher_id], backref='mentored_classes')
    students = db.relationship('ClassStudent', back_populates='classroom', cascade='all, delete-orphan', lazy=True)
    schedules = db.relationship('ClassSchedule', back_populates='classroom', cascade='all, delete-orphan', lazy=True)
    attendances = db.relationship('Attendance', back_populates='classroom', cascade='all, delete-orphan', lazy=True)
    results = db.relationship('Result', back_populates='classroom', cascade='all, delete-orphan', lazy=True)
    assignments = db.relationship('Assignment', back_populates='classroom', cascade='all, delete-orphan', lazy=True)

    @property
    def student_count(self):
        return len(self.students)

    def __repr__(self):
        return f'<ClassRoom {self.code} ({self.name})>'


class ClassStudent(db.Model):
    """Association linking enrolled students to their active class."""
    __tablename__ = 'class_students'

    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
    roll_number = db.Column(db.String(30), nullable=True)

    classroom = db.relationship('ClassRoom', back_populates='students')
    student = db.relationship('User', back_populates='enrollments')

    def __repr__(self):
        return f'<ClassStudent StudentID:{self.student_id} in Class:{self.class_id}>'


class ClassSchedule(db.Model):
    """Weekly timetable entries for classes."""
    __tablename__ = 'class_schedules'

    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    day_of_week = db.Column(db.String(15), nullable=False)  # Monday, Tuesday, etc.
    start_time = db.Column(db.String(10), nullable=False)   # e.g., '09:00'
    end_time = db.Column(db.String(10), nullable=False)     # e.g., '10:00'
    room_number = db.Column(db.String(30), default='LH-101')

    classroom = db.relationship('ClassRoom', back_populates='schedules')
    subject = db.relationship('Subject', backref='schedules')
    teacher = db.relationship('User', backref='schedules')

    def __repr__(self):
        return f'<ClassSchedule {self.day_of_week} {self.start_time}-{self.end_time} Subj:{self.subject_id}>'
