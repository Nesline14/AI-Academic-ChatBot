from datetime import datetime, date
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models.user import User
from app.models.academic import Department, ClassRoom, ClassStudent, ClassSchedule, Subject
from app.models.attendance import Attendance
from app.models.result import Result
from app.models.announcement import Announcement
from app.models.assignment import Assignment, AssignmentSubmission
from app.models.event import CampusEvent, EventRegistration
from app.models.project import AcademicProject
from app.models.club import Club, ClubMember, ClubActivity
from app.services.attendance_service import get_student_attendance_summary
from app.services.result_service import get_student_academic_summary

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
def root():
    return redirect(url_for('dashboard.index'))


@dashboard_bp.route('/dashboard')
@login_required
def index():
    if current_user.is_admin:
        return redirect(url_for('dashboard.admin_dashboard'))
    elif current_user.is_teacher:
        return redirect(url_for('dashboard.teacher_dashboard'))
    elif current_user.is_coordinator:
        return redirect(url_for('dashboard.coordinator_dashboard'))
    else:
        return redirect(url_for('dashboard.student_dashboard'))


@dashboard_bp.route('/dashboard/student')
@login_required
def student_dashboard():
    student_id = current_user.id
    now = datetime.utcnow()
    today = date.today()

    # 1. Attendance summary
    attendance_summary = get_student_attendance_summary(student_id)

    # 2. Academic results summary
    academic_summary = get_student_academic_summary(student_id)

    # 3. Enrolled classes
    enrollments = ClassStudent.query.filter_by(student_id=student_id).all()
    class_ids = [e.class_id for e in enrollments]

    # 4. Upcoming assignments & pending submissions
    if class_ids:
        assignments = Assignment.query.filter(Assignment.class_id.in_(class_ids)).order_by(Assignment.due_date.asc()).all()
    else:
        assignments = Assignment.query.order_by(Assignment.due_date.asc()).all()

    pending_assignments = []
    for a in assignments:
        sub = a.get_submission_for_student(student_id)
        if not sub or sub.status == 'Pending':
            pending_assignments.append(a)

    # 5. Announcements
    announcements = Announcement.query.order_by(Announcement.is_pinned.desc(), Announcement.created_at.desc()).limit(5).all()

    # 6. Upcoming events
    upcoming_events = CampusEvent.query.filter(CampusEvent.event_date >= today).order_by(CampusEvent.event_date.asc()).limit(4).all()

    # 7. Student's projects
    my_projects = AcademicProject.query.filter(
        (AcademicProject.creator_id == student_id) |
        (AcademicProject.members.any(student_id=student_id))
    ).all()

    # 8. Student's clubs
    my_club_memberships = ClubMember.query.filter_by(student_id=student_id).all()
    my_clubs = [m.club for m in my_club_memberships if m.club]

    # 9. Today's schedule
    day_name = datetime.now().strftime('%A')
    today_schedules = []
    if class_ids:
        today_schedules = ClassSchedule.query.filter(
            ClassSchedule.class_id.in_(class_ids),
            ClassSchedule.day_of_week == day_name
        ).order_by(ClassSchedule.start_time.asc()).all()

    return render_template(
        'dashboard/student_dashboard.html',
        attendance=attendance_summary,
        academic=academic_summary,
        pending_assignments=pending_assignments[:4],
        announcements=announcements,
        upcoming_events=upcoming_events,
        my_projects=my_projects,
        my_clubs=my_clubs,
        today_schedules=today_schedules,
        day_name=day_name
    )


@dashboard_bp.route('/dashboard/teacher')
@login_required
def teacher_dashboard():
    teacher_id = current_user.id
    today = date.today()
    day_name = datetime.now().strftime('%A')

    # Classes taught or mentored
    classes_mentored = ClassRoom.query.filter_by(teacher_id=teacher_id).all()
    
    # Assignments created
    my_assignments = Assignment.query.filter_by(teacher_id=teacher_id).order_by(Assignment.due_date.desc()).all()
    
    # Pending submissions to grade
    pending_submissions = AssignmentSubmission.query.join(Assignment).filter(
        Assignment.teacher_id == teacher_id,
        AssignmentSubmission.status == 'Submitted'
    ).order_by(AssignmentSubmission.submitted_at.desc()).limit(6).all()

    # Guided projects
    guided_projects = AcademicProject.query.filter_by(guide_id=teacher_id).all()

    # Today's teaching schedule
    today_schedules = ClassSchedule.query.filter_by(
        teacher_id=teacher_id,
        day_of_week=day_name
    ).order_by(ClassSchedule.start_time.asc()).all()

    # Announcements
    announcements = Announcement.query.order_by(Announcement.created_at.desc()).limit(4).all()

    return render_template(
        'dashboard/teacher_dashboard.html',
        classes=classes_mentored,
        assigned_classes=classes_mentored,
        assignments=my_assignments[:5],
        pending_submissions=pending_submissions,
        guided_projects=guided_projects,
        today_schedules=today_schedules,
        day_name=day_name,
        announcements=announcements
    )


@dashboard_bp.route('/dashboard/admin')
@login_required
def admin_dashboard():
    # Overall statistics
    total_students = User.query.filter_by(role='student').count()
    total_teachers = User.query.filter_by(role='teacher').count()
    total_coordinators = User.query.filter_by(role='coordinator').count()
    total_classes = ClassRoom.query.count()
    total_departments = Department.query.count()
    total_subjects = Subject.query.count()
    total_events = CampusEvent.query.count()
    total_clubs = Club.query.count()
    total_projects = AcademicProject.query.count()

    stats = {
        'students_count': total_students,
        'teachers_count': total_teachers,
        'coordinators_count': total_coordinators,
        'classes_count': total_classes,
        'departments_count': total_departments,
        'subjects_count': total_subjects,
        'events_count': total_events,
        'clubs_count': total_clubs,
        'projects_count': total_projects
    }

    recent_users = User.query.order_by(User.created_at.desc()).limit(8).all()
    announcements = Announcement.query.order_by(Announcement.created_at.desc()).limit(5).all()
    recent_events = CampusEvent.query.order_by(CampusEvent.event_date.asc()).limit(4).all()

    return render_template(
        'dashboard/admin_dashboard.html',
        stats=stats,
        total_students=total_students,
        total_teachers=total_teachers,
        total_coordinators=total_coordinators,
        total_classes=total_classes,
        total_departments=total_departments,
        total_subjects=total_subjects,
        total_events=total_events,
        total_clubs=total_clubs,
        total_projects=total_projects,
        recent_users=recent_users,
        announcements=announcements,
        recent_announcements=announcements,
        recent_events=recent_events
    )


@dashboard_bp.route('/dashboard/coordinator')
@login_required
def coordinator_dashboard():
    coordinator_id = current_user.id
    today = date.today()

    # Clubs led/coordinated
    if current_user.is_admin:
        my_clubs = Club.query.all()
    else:
        my_clubs = Club.query.filter_by(coordinator_id=coordinator_id).all()

    club_ids = [c.id for c in my_clubs]

    # Activities organized
    activities = ClubActivity.query.filter(ClubActivity.club_id.in_(club_ids)).order_by(ClubActivity.activity_date.desc()).limit(6).all() if club_ids else []

    # Upcoming campus events
    upcoming_events = CampusEvent.query.filter(CampusEvent.event_date >= today).order_by(CampusEvent.event_date.asc()).limit(4).all()

    # Announcements
    announcements = Announcement.query.order_by(Announcement.created_at.desc()).limit(4).all()

    return render_template(
        'dashboard/coordinator_dashboard.html',
        my_clubs=my_clubs,
        managed_clubs=my_clubs,
        activities=activities,
        recent_activities=activities,
        upcoming_events=upcoming_events,
        announcements=announcements
    )
