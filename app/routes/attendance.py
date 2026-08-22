from datetime import datetime, date
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from app.models.academic import ClassRoom, Subject, ClassStudent
from app.models.attendance import Attendance
from app.models.user import User
from app.services.attendance_service import get_student_attendance_summary
from app.services.notification_service import send_notification
from app.services.email_service import send_attendance_alert_email
from app.utils.decorators import teacher_required, role_required

attendance_bp = Blueprint('attendance', __name__, url_prefix='/attendance')


@attendance_bp.route('/')
@login_required
def index():
    if current_user.is_student:
        summary = get_student_attendance_summary(current_user.id)
        return render_template('attendance/student_view.html', summary=summary, attendance_data=summary)
    
    # Teacher / Admin view
    if current_user.is_teacher:
        classes = ClassRoom.query.filter((ClassRoom.teacher_id == current_user.id) | (ClassRoom.id > 0)).all()
    else:
        classes = ClassRoom.query.order_by(ClassRoom.name).all()
        
    subjects = Subject.query.order_by(Subject.name).all()
    recent_records = Attendance.query.order_by(Attendance.date.desc(), Attendance.created_at.desc()).limit(15).all()

    return render_template('attendance/index.html', classes=classes, subjects=subjects, recent_records=recent_records)


@attendance_bp.route('/mark', methods=['GET', 'POST'])
@login_required
@teacher_required
def mark():
    class_id = request.args.get('class_id', type=int) or request.form.get('class_id', type=int)
    subject_id = request.args.get('subject_id', type=int) or request.form.get('subject_id', type=int)
    att_date_str = request.args.get('date') or request.form.get('date')

    if att_date_str:
        try:
            att_date = datetime.strptime(att_date_str, '%Y-%m-%d').date()
        except ValueError:
            att_date = date.today()
    else:
        att_date = date.today()

    classes = ClassRoom.query.order_by(ClassRoom.name).all()
    subjects = Subject.query.order_by(Subject.name).all()

    selected_class = ClassRoom.query.get(class_id) if class_id else None
    selected_subject = Subject.query.get(subject_id) if subject_id else None
    
    students = []
    if selected_class:
        students = [cs.student for cs in selected_class.students if cs.student and cs.student.is_active_account]

    if request.method == 'POST' and 'submit_attendance' in request.form:
        if not selected_class or not selected_subject:
            flash('Please select both a class and a subject.', 'warning')
            return redirect(url_for('attendance.mark'))

        count_marked = 0
        for student in students:
            status = request.form.get(f'status_{student.id}', 'Present')
            remarks = request.form.get(f'remarks_{student.id}', '').strip()

            # Check if record already exists for this date, student, subject
            existing = Attendance.query.filter_by(
                student_id=student.id,
                class_id=selected_class.id,
                subject_id=selected_subject.id,
                date=att_date
            ).first()

            if existing:
                existing.status = status
                existing.remarks = remarks
                existing.marked_by_id = current_user.id
            else:
                new_att = Attendance(
                    student_id=student.id,
                    class_id=selected_class.id,
                    subject_id=selected_subject.id,
                    date=att_date,
                    status=status,
                    remarks=remarks or None,
                    marked_by_id=current_user.id
                )
                db.session.add(new_att)
                
                # If absent, send a friendly warning notification and email
                if status == 'Absent':
                    send_notification(
                        user_id=student.id,
                        title='Attendance Notice',
                        message=f'You were marked absent in {selected_subject.name} on {att_date.strftime("%b %d, %Y")}.',
                        category='attendance',
                        link_url='/attendance'
                    )
                    send_attendance_alert_email(
                        user=student,
                        attendance_record=new_att
                    )

            count_marked += 1

        db.session.commit()
        flash(f'Successfully recorded attendance for {count_marked} students in {selected_class.name}!', 'success')
        return redirect(url_for('attendance.index'))

    return render_template(
        'attendance/mark.html',
        classes=classes,
        subjects=subjects,
        selected_class=selected_class,
        selected_subject=selected_subject,
        students=students,
        att_date=att_date
    )


@attendance_bp.route('/student/<int:student_id>')
@login_required
def view_student_attendance(student_id):
    # Only allow self or faculty/admin
    if current_user.is_student and current_user.id != student_id:
        flash('Unauthorized to view this student attendance record.', 'danger')
        return redirect(url_for('attendance.index'))

    student = User.query.get_or_404(student_id)
    summary = get_student_attendance_summary(student_id)
    return render_template('attendance/student_view.html', summary=summary, target_student=student)
