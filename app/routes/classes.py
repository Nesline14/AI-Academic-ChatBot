from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from app.models.academic import ClassRoom, Department, Subject, ClassStudent, ClassSchedule
from app.models.user import User
from app.utils.decorators import teacher_required, admin_required

classes_bp = Blueprint('classes', __name__, url_prefix='/classes')


@classes_bp.route('/')
@login_required
def index():
    if current_user.is_student:
        # Enrolled classes
        enrollments = ClassStudent.query.filter_by(student_id=current_user.id).all()
        classes = [e.classroom for e in enrollments if e.classroom]
    elif current_user.is_teacher:
        classes = ClassRoom.query.filter((ClassRoom.teacher_id == current_user.id) | (ClassRoom.id > 0)).all()
    else:
        classes = ClassRoom.query.order_by(ClassRoom.name).all()

    departments = Department.query.order_by(Department.name).all()
    return render_template('classes/index.html', classes=classes, departments=departments)


@classes_bp.route('/create', methods=['GET', 'POST'])
@login_required
@teacher_required
def create():
    departments = Department.query.order_by(Department.name).all()
    teachers = User.query.filter_by(role='teacher', is_active_account=True).order_by(User.full_name).all()

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        code = request.form.get('code', '').strip().upper()
        department_id = request.form.get('department_id', type=int)
        semester = request.form.get('semester', default=1, type=int)
        section = request.form.get('section', 'A').strip().upper()
        academic_year = request.form.get('academic_year', '2025-2026').strip()
        teacher_id = request.form.get('teacher_id', type=int) or current_user.id

        if not name or not code or not department_id:
            flash('Name, code, and department are required.', 'warning')
            return render_template('classes/create.html', departments=departments, teachers=teachers)

        existing = ClassRoom.query.filter_by(code=code).first()
        if existing:
            flash(f'Class code {code} is already in use.', 'danger')
            return render_template('classes/create.html', departments=departments, teachers=teachers)

        new_class = ClassRoom(
            name=name,
            code=code,
            department_id=department_id,
            semester=semester,
            section=section,
            academic_year=academic_year,
            teacher_id=teacher_id
        )
        db.session.add(new_class)
        db.session.commit()
        flash(f'Class "{name}" created successfully!', 'success')
        return redirect(url_for('classes.detail', class_id=new_class.id))

    return render_template('classes/create.html', departments=departments, teachers=teachers)


@classes_bp.route('/<int:class_id>')
@login_required
def detail(class_id):
    classroom = ClassRoom.query.get_or_404(class_id)
    all_students = User.query.filter_by(role='student', is_active_account=True).order_by(User.full_name).all()
    subjects = Subject.query.filter_by(department_id=classroom.department_id).all()
    teachers = User.query.filter_by(role='teacher', is_active_account=True).order_by(User.full_name).all()
    
    # Organize schedules by day
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    schedule_by_day = {day: [] for day in days}
    for s in classroom.schedules:
        if s.day_of_week in schedule_by_day:
            schedule_by_day[s.day_of_week].append(s)

    # Sort each day by start_time
    for day in days:
        schedule_by_day[day].sort(key=lambda x: x.start_time)

    # Students not yet in this class
    enrolled_ids = {cs.student_id for cs in classroom.students}
    available_students = [s for s in all_students if s.id not in enrolled_ids]

    return render_template(
        'classes/detail.html',
        classroom=classroom,
        schedule_by_day=schedule_by_day,
        days=days,
        available_students=available_students,
        subjects=subjects,
        teachers=teachers
    )


@classes_bp.route('/<int:class_id>/add-student', methods=['POST'])
@login_required
@teacher_required
def add_student(class_id):
    classroom = ClassRoom.query.get_or_404(class_id)
    student_id = request.form.get('student_id', type=int)

    if not student_id:
        flash('Please select a valid student.', 'warning')
        return redirect(url_for('classes.detail', class_id=class_id))

    existing = ClassStudent.query.filter_by(class_id=class_id, student_id=student_id).first()
    if existing:
        flash('Student is already enrolled in this class.', 'info')
    else:
        enrollment = ClassStudent(class_id=class_id, student_id=student_id)
        db.session.add(enrollment)
        db.session.commit()
        flash('Student enrolled into class successfully!', 'success')

    return redirect(url_for('classes.detail', class_id=class_id))


@classes_bp.route('/<int:class_id>/remove-student/<int:student_id>', methods=['POST'])
@login_required
@teacher_required
def remove_student(class_id, student_id):
    enrollment = ClassStudent.query.filter_by(class_id=class_id, student_id=student_id).first_or_404()
    db.session.delete(enrollment)
    db.session.commit()
    flash('Student removed from class.', 'info')
    return redirect(url_for('classes.detail', class_id=class_id))


@classes_bp.route('/<int:class_id>/add-schedule', methods=['POST'])
@login_required
@teacher_required
def add_schedule(class_id):
    classroom = ClassRoom.query.get_or_404(class_id)
    subject_id = request.form.get('subject_id', type=int)
    teacher_id = request.form.get('teacher_id', type=int) or current_user.id
    day_of_week = request.form.get('day_of_week')
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')
    room_number = request.form.get('room_number', 'LH-101').strip()

    if not subject_id or not day_of_week or not start_time or not end_time:
        flash('All schedule fields are required.', 'warning')
        return redirect(url_for('classes.detail', class_id=class_id))

    new_schedule = ClassSchedule(
        class_id=class_id,
        subject_id=subject_id,
        teacher_id=teacher_id,
        day_of_week=day_of_week,
        start_time=start_time,
        end_time=end_time,
        room_number=room_number
    )
    db.session.add(new_schedule)
    db.session.commit()
    flash(f'Timetable schedule for {day_of_week} ({start_time}-{end_time}) added!', 'success')
    return redirect(url_for('classes.detail', class_id=class_id))
