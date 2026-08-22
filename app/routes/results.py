from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from app.models.result import Result
from app.models.academic import ClassRoom, Subject
from app.models.user import User
from app.services.result_service import get_student_academic_summary
from app.services.notification_service import send_notification
from app.services.email_service import send_result_published_email
from app.utils.decorators import teacher_required

results_bp = Blueprint('results', __name__, url_prefix='/results')


@results_bp.route('/')
@login_required
def index():
    if current_user.is_student:
        summary = get_student_academic_summary(current_user.id)
        gpa_summary = {
            'cgpa': summary.get('cgpa', 0.0),
            'overall_percentage': summary.get('overall_percentage', 0.0),
            'total_credits': summary.get('total_subjects', 0) * 3,
            'passed_subjects': summary.get('passed_subjects', 0),
            'total_subjects': summary.get('total_subjects', 0)
        }
        semester_groups = summary.get('semesters', {})
        for sem, sdata in semester_groups.items():
            if 'sgpa' not in sdata:
                sdata['sgpa'] = sdata.get('gpa', 0.0)

        return render_template(
            'results/student_view.html',
            summary=summary,
            gpa_summary=gpa_summary,
            semester_groups=semester_groups
        )

    # Teacher / Admin view
    results = Result.query.order_by(Result.created_at.desc()).all()
    classes = ClassRoom.query.order_by(ClassRoom.name).all()
    subjects = Subject.query.order_by(Subject.name).all()

    return render_template('results/index.html', results=results, classes=classes, subjects=subjects)


@results_bp.route('/add', methods=['GET', 'POST'], endpoint='add')
@results_bp.route('/add_result', methods=['GET', 'POST'], endpoint='add_result')
@login_required
@teacher_required
def add():
    classes = ClassRoom.query.order_by(ClassRoom.name).all()
    subjects = Subject.query.order_by(Subject.name).all()
    students = User.query.filter_by(role='student', is_active_account=True).order_by(User.full_name).all()

    if request.method == 'POST':
        student_id = request.form.get('student_id', type=int)
        subject_id = request.form.get('subject_id', type=int)
        class_id = request.form.get('class_id', type=int)
        semester = request.form.get('semester', default=1, type=int)
        
        internal_marks = float(request.form.get('internal_marks', 0.0))
        assignment_marks = float(request.form.get('assignment_marks', 0.0))
        exam_marks = float(request.form.get('exam_marks', 0.0))
        max_marks = float(request.form.get('max_marks', 100.0))
        remarks = request.form.get('remarks', '').strip()

        if not student_id or not subject_id or not class_id:
            flash('Please select student, subject, and class.', 'warning')
            return render_template('results/add.html', classes=classes, subjects=subjects, students=students)

        total_marks = internal_marks + assignment_marks + exam_marks
        grade, gpa_points = Result.calculate_grade_and_gpa(total_marks, max_marks)

        # Check existing result
        existing = Result.query.filter_by(student_id=student_id, subject_id=subject_id, semester=semester).first()
        if existing:
            existing.internal_marks = internal_marks
            existing.assignment_marks = assignment_marks
            existing.exam_marks = exam_marks
            existing.total_marks = total_marks
            existing.max_marks = max_marks
            existing.grade = grade
            existing.gpa_points = gpa_points
            existing.remarks = remarks or None
            existing.teacher_id = current_user.id
            flash('Existing result record successfully updated!', 'info')
        else:
            new_res = Result(
                student_id=student_id,
                subject_id=subject_id,
                class_id=class_id,
                semester=semester,
                internal_marks=internal_marks,
                assignment_marks=assignment_marks,
                exam_marks=exam_marks,
                total_marks=total_marks,
                max_marks=max_marks,
                grade=grade,
                gpa_points=gpa_points,
                remarks=remarks or None,
                teacher_id=current_user.id
            )
            db.session.add(new_res)
            flash('New examination result added successfully!', 'success')

        db.session.commit()

        # Send notification to student
        sub_obj = Subject.query.get(subject_id)
        sub_name = sub_obj.name if sub_obj else 'your subject'
        send_notification(
            user_id=student_id,
            title='New Result Published',
            message=f'Your grade for {sub_name} (Sem {semester}) has been published: Grade {grade} ({total_marks}/{max_marks}).',
            category='result',
            link_url='/results'
        )

        # Dispatch email notification to student
        saved_result = existing if existing else new_res
        student_user = User.query.get(student_id)
        if student_user and saved_result:
            send_result_published_email(student_user, saved_result)

        return redirect(url_for('results.index'))

    return render_template('results/add.html', classes=classes, subjects=subjects, students=students)


@results_bp.route('/delete/<int:result_id>', methods=['POST'])
@login_required
@teacher_required
def delete(result_id):
    res = Result.query.get_or_404(result_id)
    db.session.delete(res)
    db.session.commit()
    flash('Result record deleted successfully.', 'info')
    return redirect(url_for('results.index'))


@results_bp.route('/student/<int:student_id>')
@login_required
def view_student_results(student_id):
    if current_user.is_student and current_user.id != student_id:
        flash('Unauthorized access to student results.', 'danger')
        return redirect(url_for('results.index'))

    student = User.query.get_or_404(student_id)
    summary = get_student_academic_summary(student_id)
    return render_template('results/student_view.html', summary=summary, target_student=student)
