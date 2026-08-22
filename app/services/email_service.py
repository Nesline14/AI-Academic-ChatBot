import smtplib
import ssl
import re
import threading
import logging
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr, parseaddr
from flask import current_app, render_template

logger = logging.getLogger('campusconnect.email')


def html_to_plain_text(html_content):
    """Convert HTML string to basic plain text alternative."""
    text = re.sub(r'<style.*?>.*?</style>', '', html_content, flags=re.DOTALL)
    text = re.sub(r'<script.*?>.*?</script>', '', html_content, flags=re.DOTALL)
    text = re.sub(r'<br\s*/?>', '\n', text)
    text = re.sub(r'</p>', '\n\n', text)
    text = re.sub(r'</div>', '\n', text)
    text = re.sub(r'</li>', '\n', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\n\s*\n', '\n\n', text)
    return text.strip()


def _send_smtp_message(app, to_email, subject, html_body, text_body=None):
    """Internal worker function to send an email via configured SMTP server."""
    with app.app_context():
        mail_enabled = app.config.get('MAIL_ENABLED', True)
        mail_server = app.config.get('MAIL_SERVER', 'localhost')
        mail_port = int(app.config.get('MAIL_PORT', 587))
        mail_use_tls = app.config.get('MAIL_USE_TLS', True)
        mail_use_ssl = app.config.get('MAIL_USE_SSL', False)
        mail_username = app.config.get('MAIL_USERNAME', '')
        mail_password = app.config.get('MAIL_PASSWORD', '')
        default_sender = app.config.get('MAIL_DEFAULT_SENDER', 'CampusConnect <noreply@campusconnect.edu>')
        debug_log = app.config.get('MAIL_DEBUG_LOG', True)

        if not mail_enabled:
            if debug_log:
                logger.info(f"[Email Disabled] To: {to_email} | Subject: {subject}")
            return True

        if not to_email:
            logger.warning("Attempted to send email to empty recipient address.")
            return False

        if text_body is None:
            text_body = html_to_plain_text(html_body)

        # Build multipart message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = Header(subject, 'utf-8').encode()
        
        # Parse sender
        sender_name, sender_addr = parseaddr(default_sender)
        if not sender_addr:
            sender_addr = 'noreply@campusconnect.edu'
            sender_name = 'CampusConnect'
        msg['From'] = formataddr((str(Header(sender_name, 'utf-8')), sender_addr))
        msg['To'] = to_email

        msg.attach(MIMEText(text_body, 'plain', 'utf-8'))
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))

        try:
            if mail_use_ssl:
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(mail_server, mail_port, context=context, timeout=10) as server:
                    if mail_username and mail_password:
                        server.login(mail_username, mail_password)
                    server.sendmail(sender_addr, [to_email], msg.as_string())
            else:
                with smtplib.SMTP(mail_server, mail_port, timeout=10) as server:
                    if mail_use_tls:
                        context = ssl.create_default_context()
                        server.starttls(context=context)
                    if mail_username and mail_password:
                        server.login(mail_username, mail_password)
                    server.sendmail(sender_addr, [to_email], msg.as_string())

            logger.info(f"Email successfully delivered to {to_email}: {subject}")
            return True
        except Exception as e:
            # If in local dev or SMTP server is unreachable, log details cleanly without throwing
            if debug_log:
                logger.warning(
                    f"[Email Delivery Simulation / SMTP Notice] Could not connect to SMTP server ({mail_server}:{mail_port}). "
                    f"Message to '{to_email}' with subject '{subject}' was logged locally. Details: {e}"
                )
            return False


def send_email(to_email, subject, html_content, text_content=None, async_send=True):
    """
    Send an email notification to the recipient.
    By default runs asynchronously in a daemon thread so request processing is not blocked.
    """
    app = current_app._get_current_object()
    
    if app.config.get('TESTING') or not async_send:
        return _send_smtp_message(app, to_email, subject, html_content, text_content)
    
    thread = threading.Thread(
        target=_send_smtp_message,
        args=(app, to_email, subject, html_content, text_content),
        daemon=True
    )
    thread.start()
    return True


# ==========================================
# Event-Driven Notification Dispatchers
# ==========================================

def send_announcement_email(user, announcement):
    """Send email notification for a new announcement if user preferences allow."""
    if not user or not user.wants_email('announcement'):
        return False

    base_url = current_app.config.get('APP_BASE_URL', 'http://localhost:5000')
    subject = f"[Campus Announcement] {announcement.title}"
    
    html = render_template(
        'emails/announcement.html',
        user=user,
        announcement=announcement,
        base_url=base_url,
        subject=subject
    )
    return send_email(user.email, subject, html)


def send_bulk_announcement_email(users, announcement):
    """Send announcement emails in batch to opted-in users."""
    for user in users:
        if user.wants_email('announcement'):
            send_announcement_email(user, announcement)


def send_assignment_created_email(user, assignment):
    """Send email notification when a new assignment is created."""
    if not user or not user.wants_email('assignment'):
        return False

    base_url = current_app.config.get('APP_BASE_URL', 'http://localhost:5000')
    subject = f"[New Assignment] {assignment.title} - {assignment.subject.name}"
    
    html = render_template(
        'emails/assignment_new.html',
        user=user,
        assignment=assignment,
        base_url=base_url,
        subject=subject
    )
    return send_email(user.email, subject, html)


def send_bulk_assignment_created_email(users, assignment):
    """Send assignment notification to all enrolled students."""
    for user in users:
        if user.wants_email('assignment'):
            send_assignment_created_email(user, assignment)


def send_assignment_due_reminder_email(user, assignment):
    """Send reminder when an assignment deadline is approaching."""
    if not user or not user.wants_email('assignment'):
        return False

    base_url = current_app.config.get('APP_BASE_URL', 'http://localhost:5000')
    subject = f"[Reminder: Due Soon] {assignment.title} ({assignment.subject.name})"
    
    html = render_template(
        'emails/assignment_due.html',
        user=user,
        assignment=assignment,
        base_url=base_url,
        subject=subject
    )
    return send_email(user.email, subject, html)


def send_assignment_graded_email(user, submission):
    """Send notification when a teacher grades an assignment submission."""
    if not user or not user.wants_email('assignment'):
        return False

    base_url = current_app.config.get('APP_BASE_URL', 'http://localhost:5000')
    subject = f"[Assignment Graded] {submission.assignment.title} - Score: {submission.marks_obtained}/{submission.assignment.max_marks}"
    
    html = render_template(
        'emails/assignment_graded.html',
        user=user,
        submission=submission,
        base_url=base_url,
        subject=subject
    )
    return send_email(user.email, subject, html)


def send_result_published_email(user, result):
    """Send notification when an exam result or course grade is published."""
    if not user or not user.wants_email('result'):
        return False

    base_url = current_app.config.get('APP_BASE_URL', 'http://localhost:5000')
    subject = f"[Grade Published] {result.subject.name} - Grade {result.grade}"
    
    html = render_template(
        'emails/result_published.html',
        user=user,
        result=result,
        base_url=base_url,
        subject=subject
    )
    return send_email(user.email, subject, html)


def send_attendance_alert_email(user, attendance_record=None, overall_percentage=None):
    """Send alert email when student attendance is low or an absence is logged."""
    if not user or not user.wants_email('attendance'):
        return False

    base_url = current_app.config.get('APP_BASE_URL', 'http://localhost:5000')
    subject = f"[Attendance Notice] Update on your academic attendance"
    
    html = render_template(
        'emails/attendance_alert.html',
        user=user,
        attendance_record=attendance_record,
        overall_percentage=overall_percentage,
        subject=attendance_record.subject if attendance_record else None,
        base_url=base_url
    )
    return send_email(user.email, subject, html)


def send_event_registration_email(user, event):
    """Send registration confirmation email for a campus event."""
    if not user or not user.wants_email('event'):
        return False

    base_url = current_app.config.get('APP_BASE_URL', 'http://localhost:5000')
    subject = f"[Event Confirmed] {event.title}"
    
    html = render_template(
        'emails/event_confirmation.html',
        user=user,
        event=event,
        base_url=base_url,
        subject=subject
    )
    return send_email(user.email, subject, html)


def send_test_email(user):
    """Send a diagnostic test email to verify user's SMTP setup."""
    base_url = current_app.config.get('APP_BASE_URL', 'http://localhost:5000')
    mail_server = current_app.config.get('MAIL_SERVER', 'localhost')
    mail_port = current_app.config.get('MAIL_PORT', 587)
    mail_enabled = current_app.config.get('MAIL_ENABLED', True)
    
    delivery_mode = f"SMTP ({mail_server}:{mail_port})" if mail_enabled else "Simulated / Logged Mode"
    sent_time = datetime.utcnow().strftime('%b %d, %Y at %I:%M:%S %p UTC')
    subject = "[CampusConnect] System Test Email Verification"

    html = render_template(
        'emails/test_email.html',
        user=user,
        smtp_server=f"{mail_server}:{mail_port}",
        delivery_mode=delivery_mode,
        sent_time=sent_time,
        base_url=base_url,
        subject=subject
    )
    return send_email(user.email, subject, html)


def check_and_send_due_assignment_reminders(hours_ahead=24):
    """
    Find assignments due in the next `hours_ahead` hours and notify students who have not yet submitted.
    """
    from app.models.assignment import Assignment, AssignmentSubmission
    from app.models.academic import ClassStudent

    now = datetime.utcnow()
    deadline_window = now + timedelta(hours=hours_ahead)

    upcoming_assignments = Assignment.query.filter(
        Assignment.due_date > now,
        Assignment.due_date <= deadline_window
    ).all()

    reminders_sent = 0
    for assignment in upcoming_assignments:
        classroom = assignment.classroom
        if not classroom:
            continue
        
        # Find students enrolled in this class
        enrolled_students = [cs.student for cs in classroom.students if cs.student and cs.student.is_active_account]
        for student in enrolled_students:
            # Check if student already submitted
            submission = AssignmentSubmission.query.filter_by(
                assignment_id=assignment.id,
                student_id=student.id
            ).first()

            if not submission or submission.status not in ('Submitted', 'Graded'):
                if student.wants_email('assignment'):
                    send_assignment_due_reminder_email(student, assignment)
                    reminders_sent += 1

    return reminders_sent
