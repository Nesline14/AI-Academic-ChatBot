from datetime import datetime, date
from flask import current_app
from extensions import db
from app.models.chatbot import ChatMessage
from app.models.academic import ClassStudent, ClassSchedule
from app.models.announcement import Announcement
from app.models.assignment import Assignment, AssignmentSubmission
from app.models.event import CampusEvent
from app.models.club import Club
from app.services.attendance_service import get_student_attendance_summary
from app.services.result_service import get_student_academic_summary


def process_student_query(user, message_text):
    """
    Process natural language queries from students and return database-aware answers.
    Supports modular extension for AI API keys if configured.
    """
    raw_query = (message_text or '').strip().lower()
    user_name = user.full_name.split()[0] if user and user.full_name else 'Student'
    
    intent = 'general'
    response_html = ''

    # 1. Attendance queries
    if any(k in raw_query for k in ['attendance', 'present', 'absent', 'percentage', 'attended']):
        intent = 'attendance'
        if user and user.is_student:
            summary = get_student_attendance_summary(user.id)
            total = summary['total_classes']
            pct = summary['overall_percentage']
            attended = summary['attended']
            missed = summary['missed']
            
            warning_text = ""
            if summary['is_below_threshold']:
                warning_text = f"<div class='alert alert-warning py-1 px-2 my-2 small'><i class='bi bi-exclamation-triangle-fill me-1'></i> <strong>Warning:</strong> Your attendance is below the mandatory <strong>75%</strong> threshold!</div>"
            
            sub_items = ""
            for sub in summary['subjects'][:4]:
                color = "text-danger" if sub['is_below_threshold'] else "text-success"
                sub_items += f"<li><strong>{sub['name']}</strong>: <span class='{color} fw-bold'>{sub['percentage']}%</span> ({sub['attended']}/{sub['total']} classes)</li>"
            
            response_html = f"""
                <p>Hello <strong>{user_name}</strong>! Here is your current attendance summary:</p>
                <div class='card bg-light border-0 p-2 mb-2'>
                    <div class='d-flex justify-content-between align-items-center'>
                        <span>Overall Attendance:</span>
                        <span class='badge bg-{"danger" if summary["is_below_threshold"] else "success"} fs-6'>{pct}%</span>
                    </div>
                    <div class='small text-muted mt-1'>
                        Classes Attended: <strong>{attended}</strong> | Missed: <strong>{missed}</strong> | Total: <strong>{total}</strong>
                    </div>
                </div>
                {warning_text}
                <p class='mb-1 small fw-semibold'>Subject Breakdown:</p>
                <ul class='small ps-3 mb-2'>{sub_items or '<li>No subject records recorded yet.</li>'}</ul>
                <a href='/attendance' class='btn btn-sm btn-outline-primary'>View Full Attendance Record &rarr;</a>
            """
        else:
            response_html = "<p>Attendance metrics can be managed in the <a href='/attendance'>Attendance Portal</a>.</p>"

    # 2. Assignments queries
    elif any(k in raw_query for k in ['assignment', 'homework', 'submission', 'due', 'deadline', 'task']):
        intent = 'assignments'
        if user and user.is_student:
            # Find student's enrolled classes
            enrollments = ClassStudent.query.filter_by(student_id=user.id).all()
            class_ids = [e.class_id for e in enrollments]
            
            if class_ids:
                assignments = Assignment.query.filter(Assignment.class_id.in_(class_ids)).order_by(Assignment.due_date.asc()).all()
            else:
                assignments = Assignment.query.order_by(Assignment.due_date.asc()).all()
                
            now = datetime.utcnow()
            pending_list = []
            
            for a in assignments:
                sub = a.get_submission_for_student(user.id)
                if not sub or sub.status == 'Pending':
                    pending_list.append(a)
            
            if pending_list:
                items = ""
                for a in pending_list[:4]:
                    due_str = a.due_date.strftime('%b %d, %Y at %I:%M %p')
                    is_late = now > a.due_date
                    badge = "<span class='badge bg-danger ms-1'>Overdue</span>" if is_late else f"<span class='badge bg-warning text-dark ms-1'>{due_str}</span>"
                    items += f"<li class='mb-2'><strong>{a.title}</strong> ({a.subject.name if a.subject else 'General'})<br><small class='text-muted'>Due: {badge}</small></li>"
                
                response_html = f"""
                    <p>You have <strong>{len(pending_list)} pending assignment(s)</strong>:</p>
                    <ul class='small ps-3 mb-2'>{items}</ul>
                    <a href='/assignments' class='btn btn-sm btn-primary'>Go to Assignments & Submit &rarr;</a>
                """
            else:
                response_html = """
                    <p>🎉 <strong>Great job, {user_name}!</strong> You have no pending assignments right now.</p>
                    <a href='/assignments' class='btn btn-sm btn-outline-primary'>View All Coursework</a>
                """
        else:
            response_html = "<p>You can create and grade assignments under the <a href='/assignments'>Assignments Section</a>.</p>"

    # 3. Results and Performance queries
    elif any(k in raw_query for k in ['result', 'grade', 'marks', 'gpa', 'cgpa', 'score', 'performance', 'exam']):
        intent = 'results'
        if user and user.is_student:
            summary = get_student_academic_summary(user.id)
            if summary['total_subjects'] > 0:
                recent_items = ""
                for r in summary['recent_results'][:3]:
                    recent_items += f"<li><strong>{r.subject.name if r.subject else 'Subject'}</strong>: <span class='badge bg-{r.grade_badge_class}'>{r.grade}</span> ({r.total_marks}/{r.max_marks} marks)</li>"
                
                response_html = f"""
                    <p>Here is your Academic Performance snapshot:</p>
                    <div class='card bg-light border-0 p-2 mb-2'>
                        <div class='row text-center'>
                            <div class='col-6 border-end'>
                                <div class='fs-5 fw-bold text-primary'>{summary['cgpa']} / 10.0</div>
                                <div class='small text-muted'>Cumulative CGPA</div>
                            </div>
                            <div class='col-6'>
                                <div class='fs-5 fw-bold text-success'>{summary['overall_percentage']}%</div>
                                <div class='small text-muted'>Overall Score</div>
                            </div>
                        </div>
                    </div>
                    <p class='mb-1 small fw-semibold'>Recent Subject Grades:</p>
                    <ul class='small ps-3 mb-2'>{recent_items}</ul>
                    <a href='/results' class='btn btn-sm btn-outline-success'>View Full Grade Sheet &rarr;</a>
                """
            else:
                response_html = """
                    <p>No examination results published for your profile yet.</p>
                    <a href='/results' class='btn btn-sm btn-outline-primary'>Check Results Page</a>
                """
        else:
            response_html = "<p>View and publish examination grades in the <a href='/results'>Results Portal</a>.</p>"

    # 4. Announcements queries
    elif any(k in raw_query for k in ['announcement', 'notice', 'news', 'update', 'urgent', 'circular']):
        intent = 'announcements'
        announcements = Announcement.query.order_by(Announcement.created_at.desc()).limit(3).all()
        if announcements:
            items = ""
            for a in announcements:
                date_str = a.created_at.strftime('%b %d')
                items += f"<li class='mb-1'><strong>[{a.category}] {a.title}</strong> <small class='text-muted'>({date_str})</small></li>"
            response_html = f"""
                <p>Here are the latest campus notices:</p>
                <ul class='small ps-3 mb-2'>{items}</ul>
                <a href='/announcements' class='btn btn-sm btn-outline-primary'>Read All Announcements &rarr;</a>
            """
        else:
            response_html = "<p>No active announcements found right now.</p>"

    # 5. Events queries
    elif any(k in raw_query for k in ['event', 'workshop', 'seminar', 'cultural', 'fest', 'sports', 'happen', 'activity']):
        intent = 'events'
        upcoming = CampusEvent.query.filter(CampusEvent.event_date >= date.today()).order_by(CampusEvent.event_date.asc()).limit(3).all()
        if upcoming:
            items = ""
            for ev in upcoming:
                d_str = ev.event_date.strftime('%b %d, %Y')
                items += f"<li class='mb-2'><strong>{ev.title}</strong> ({ev.category})<br><small class='text-muted'><i class='bi bi-calendar3'></i> {d_str} at {ev.start_time} | <i class='bi bi-geo-alt'></i> {ev.location}</small></li>"
            response_html = f"""
                <p>Upcoming Campus Events:</p>
                <ul class='small ps-3 mb-2'>{items}</ul>
                <a href='/events' class='btn btn-sm btn-outline-info'>Browse & Register for Events &rarr;</a>
            """
        else:
            response_html = "<p>No upcoming events currently scheduled. Check back soon or visit <a href='/events'>Events</a>.</p>"

    # 6. Classes / Timetable queries
    elif any(k in raw_query for k in ['class', 'timetable', 'schedule', 'room', 'period', 'lecture', 'subject']):
        intent = 'classes'
        if user and user.is_student:
            enrollments = ClassStudent.query.filter_by(student_id=user.id).all()
            if enrollments:
                class_names = ", ".join([e.classroom.name for e in enrollments if e.classroom])
                response_html = f"""
                    <p>You are currently enrolled in: <strong>{class_names}</strong>.</p>
                    <p class='small text-muted'>You can check your weekly timetable, classroom numbers, and faculty details on your class page.</p>
                    <a href='/classes' class='btn btn-sm btn-outline-primary'>View My Classes & Timetable &rarr;</a>
                """
            else:
                response_html = "<p>You are not currently enrolled in any class section. Please contact your department admin or visit <a href='/classes'>Classes</a>.</p>"
        else:
            response_html = "<p>Manage courses, subjects, and schedules in the <a href='/classes'>Classes Management Portal</a>.</p>"

    # 7. Clubs queries
    elif any(k in raw_query for k in ['club', 'society', 'chapter', 'robotics', 'coding club', 'music', 'sports club']):
        intent = 'clubs'
        clubs = Club.query.limit(4).all()
        if clubs:
            club_list = ", ".join([c.name for c in clubs])
            response_html = f"""
                <p>CampusConnect features active student clubs such as: <strong>{club_list}</strong>.</p>
                <p class='small text-muted'>Join clubs to participate in hackathons, cultural fests, workshops, and leadership activities.</p>
                <a href='/clubs' class='btn btn-sm btn-outline-warning'>Explore & Join Clubs &rarr;</a>
            """
        else:
            response_html = "<p>Explore club activities and chapters in the <a href='/clubs'>Clubs Directory</a>.</p>"

    # 8. Projects queries
    elif any(k in raw_query for k in ['project', 'capstone', 'mentor', 'guide', 'repo', 'github']):
        intent = 'projects'
        response_html = f"""
            <p>You can collaborate on academic capstone and mini projects, assign mentors, and track progress.</p>
            <a href='/projects' class='btn btn-sm btn-outline-primary'>Go to Academic Projects &rarr;</a>
        """

    # 9. Greeting / Help fallback
    elif any(k in raw_query for k in ['hi', 'hello', 'hey', 'help', 'who are you', 'what can you do', 'start']):
        intent = 'greeting'
        response_html = f"""
            <p>👋 Hello <strong>{user_name}</strong>! I am <strong>CampusBot</strong>, your AI-powered campus assistant.</p>
            <p class='small mb-2'>Here are things you can ask me:</p>
            <div class='d-flex flex-wrap gap-1'>
                <button type='button' class='btn btn-sm btn-light border prompt-pill' onclick='window.campusBotSend("What is my attendance?")'>📊 My Attendance</button>
                <button type='button' class='btn btn-sm btn-light border prompt-pill' onclick='window.campusBotSend("Show my upcoming assignments")'>📝 Assignments</button>
                <button type='button' class='btn btn-sm btn-light border prompt-pill' onclick='window.campusBotSend("Show my latest results")'>🎓 My Results</button>
                <button type='button' class='btn btn-sm btn-light border prompt-pill' onclick='window.campusBotSend("What events are happening this week?")'>🎪 Campus Events</button>
                <button type='button' class='btn btn-sm btn-light border prompt-pill' onclick='window.campusBotSend("What announcements are new?")'>📢 Announcements</button>
                <button type='button' class='btn btn-sm btn-light border prompt-pill' onclick='window.campusBotSend("What clubs can I join?")'>🤝 Student Clubs</button>
            </div>
        """
    else:
        # Smart fallback with options
        intent = 'fallback'
        response_html = f"""
            <p>I didn't quite catch that. Here are some quick actions you can ask me about:</p>
            <ul class='small mb-2 ps-3'>
                <li>"What is my attendance percentage?"</li>
                <li>"Show my pending assignments"</li>
                <li>"Show my exam results and GPA"</li>
                <li>"What events are happening this week?"</li>
                <li>"What announcements are new?"</li>
                <li>"Show my classes and schedule"</li>
            </ul>
        """

    # Save interaction to ChatMessage log in DB if user is logged in
    if user and user.is_authenticated:
        try:
            chat_entry = ChatMessage(
                user_id=user.id,
                message=message_text,
                response=response_html,
                intent=intent
            )
            db.session.add(chat_entry)
            db.session.commit()
        except Exception:
            db.session.rollback()

    return {
        'response': response_html,
        'intent': intent,
        'timestamp': datetime.utcnow().strftime('%I:%M %p')
    }
