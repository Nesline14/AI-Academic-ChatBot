from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from app.models.assignment import Assignment, AssignmentSubmission
from app.models.academic import ClassRoom, Subject, ClassStudent
from app.models.user import User
from app.services.notification_service import send_notification, send_bulk_notification
from app.services.email_service import (
    send_bulk_assignment_created_email,
    send_assignment_graded_email,
    send_assignment_due_reminder_email,
    check_and_send_due_assignment_reminders
)
from app.utils.helpers import save_uploaded_file
from app.utils.decorators import teacher_required

assignments_bp = Blueprint('assignments', __name__, url_prefix='/assignments')


@assignments_bp.route('/')
@login_required
def index():
    if current_user.is_student:
        enrollments = ClassStudent.query.filter_by(student_id=current_user.id).all()
        class_ids = [e.class_id for e in enrollments]
        if class_ids:
            assignments = Assignment.query.filter(Assignment.class_id.in_(class_ids)).order_by(Assignment.due_date.asc()).all()
        else:
            assignments = Assignment.query.order_by(Assignment.due_date.asc()).all()
    elif current_user.is_teacher:
        assignments = Assignment.query.filter_by(teacher_id=current_user.id).order_by(Assignment.due_date.desc()).all()
    else:
        assignments = Assignment.query.order_by(Assignment.due_date.desc()).all()

    return render_template('assignments/index.html', assignments=assignments)


@assignments_bp.route('/create', methods=['GET', 'POST'])
@login_required
@teacher_required
def create():
    classes = ClassRoom.query.order_by(ClassRoom.name).all()
    subjects = Subject.query.order_by(Subject.name).all()

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        class_id = request.form.get('class_id', type=int)
        subject_id = request.form.get('subject_id', type=int)
        max_marks = float(request.form.get('max_marks', 100.0))
        due_date_str = request.form.get('due_date')

        if not title or not description or not class_id or not subject_id or not due_date_str:
            flash('Please fill in all required assignment details.', 'warning')
            return render_template('assignments/create.html', classes=classes, subjects=subjects)

        try:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d')

        file_path = None
        if 'attachment' in request.files:
            att = request.files['attachment']
            if att and att.filename != '':
                file_path = save_uploaded_file(att, subfolder='assignments')

        new_assignment = Assignment(
            title=title,
            description=description,
            class_id=class_id,
            subject_id=subject_id,
            teacher_id=current_user.id,
            max_marks=max_marks,
            due_date=due_date,
            file_path=file_path
        )
        db.session.add(new_assignment)
        db.session.commit()

        # Send notifications to enrolled students
        classroom = ClassRoom.query.get(class_id)
        if classroom:
            enrolled_students = [cs.student for cs in classroom.students if cs.student and cs.student.is_active_account]
            student_ids = [s.id for s in enrolled_students]
            if student_ids:
                send_bulk_notification(
                    user_ids=student_ids,
                    title=f'New Assignment: {title}',
                    message=f'Due by {due_date.strftime("%b %d, %Y %I:%M %p")}. Max marks: {max_marks}.',
                    category='assignment',
                    link_url=f'/assignments/{new_assignment.id}'
                )
                # Dispatch email notifications
                send_bulk_assignment_created_email(
                    users=enrolled_students,
                    assignment=new_assignment
                )

        flash('Assignment published successfully!', 'success')
        return redirect(url_for('assignments.detail', assignment_id=new_assignment.id))

    return render_template('assignments/create.html', classes=classes, subjects=subjects)


@assignments_bp.route('/<int:assignment_id>')
@login_required
def detail(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    user_submission = None
    if current_user.is_student:
        user_submission = assignment.get_submission_for_student(current_user.id)
    return render_template('assignments/detail.html', assignment=assignment, user_submission=user_submission)


@assignments_bp.route('/<int:assignment_id>/submit', methods=['POST'])
@login_required
def submit(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    submission_text = request.form.get('submission_text', '').strip()
    
    file_path = None
    if 'submission_file' in request.files:
        file_obj = request.files['submission_file']
        if file_obj and file_obj.filename != '':
            file_path = save_uploaded_file(file_obj, subfolder='submissions')

    is_late = datetime.utcnow() > assignment.due_date
    status = 'Late' if is_late else 'Submitted'

    existing = AssignmentSubmission.query.filter_by(
        assignment_id=assignment_id,
        student_id=current_user.id
    ).first()

    if existing:
        existing.submission_text = submission_text
        if file_path:
            existing.file_path = file_path
        existing.submitted_at = datetime.utcnow()
        existing.status = status
        flash('Assignment submission updated successfully!', 'success')
    else:
        new_sub = AssignmentSubmission(
            assignment_id=assignment_id,
            student_id=current_user.id,
            submission_text=submission_text,
            file_path=file_path,
            status=status
        )
        db.session.add(new_sub)
        flash('Assignment submitted successfully!', 'success')

    db.session.commit()
    return redirect(url_for('assignments.detail', assignment_id=assignment_id))


@assignments_bp.route('/<int:assignment_id>/submissions', endpoint='view_submissions')
@assignments_bp.route('/<int:assignment_id>/submissions_list', endpoint='submissions_list')
@login_required
@teacher_required
def view_submissions(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    return render_template('assignments/submissions.html', assignment=assignment)


@assignments_bp.route('/submission/<int:submission_id>/grade', methods=['POST'])
@login_required
@teacher_required
def grade_submission(submission_id):
    submission = AssignmentSubmission.query.get_or_404(submission_id)
    marks = request.form.get('marks_obtained', type=float)
    feedback = request.form.get('feedback', '').strip()

    if marks is not None:
        submission.marks_obtained = marks
        submission.feedback = feedback or None
        submission.status = 'Graded'
        db.session.commit()

        # Send notification to student
        send_notification(
            user_id=submission.student_id,
            title='Assignment Graded',
            message=f'Your submission for "{submission.assignment.title}" received {marks}/{submission.assignment.max_marks} marks.',
            category='assignment',
            link_url=f'/assignments/{submission.assignment_id}'
        )

        # Dispatch email notification to student
        if submission.student:
            send_assignment_graded_email(
                user=submission.student,
                submission=submission
            )

        flash(f'Submission graded successfully ({marks} marks)!', 'success')

    return redirect(url_for('assignments.view_submissions', assignment_id=submission.assignment_id))


@assignments_bp.route('/send-due-reminders', methods=['POST'])
@login_required
@teacher_required
def send_due_reminders():
    """Trigger dispatch of assignment deadline reminder emails."""
    hours = request.form.get('hours', default=48, type=int)
    count = check_and_send_due_assignment_reminders(hours_ahead=hours)
    flash(f'Sent {count} upcoming deadline reminder email(s) for assignments due in the next {hours} hours.', 'info')
    return redirect(url_for('assignments.index'))
