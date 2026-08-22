import pytest
from app import create_app
from extensions import db
from seed_data import seed_database
from app.models.user import User
from app.models.announcement import Announcement
from app.models.assignment import Assignment, AssignmentSubmission
from app.models.result import Result
from app.models.event import CampusEvent
from app.services.email_service import (
    send_announcement_email,
    send_assignment_created_email,
    send_assignment_due_reminder_email,
    send_assignment_graded_email,
    send_result_published_email,
    send_event_registration_email,
    send_test_email,
    send_attendance_alert_email,
    check_and_send_due_assignment_reminders
)


@pytest.fixture
def app_instance():
    app = create_app('testing')
    app.config['MAIL_ENABLED'] = False  # Keep in logged/test mode
    with app.app_context():
        db.create_all()
        seed_database()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app_instance):
    return app_instance.test_client()


def test_user_email_preferences_defaults(app_instance):
    with app_instance.app_context():
        user = User.query.filter_by(email='student@campusconnect.com').first()
        assert user is not None
        assert user.email_notifications_enabled is True
        assert user.wants_email('announcement') is True
        assert user.wants_email('assignment') is True
        assert user.wants_email('result') is True
        assert user.wants_email('attendance') is True
        assert user.wants_email('event') is True


def test_user_email_preferences_opt_out(app_instance):
    with app_instance.app_context():
        user = User.query.filter_by(email='student@campusconnect.com').first()
        user.email_announcements = False
        db.session.commit()

        assert user.wants_email('announcement') is False
        assert user.wants_email('assignment') is True

        # Master switch disables all
        user.email_notifications_enabled = False
        db.session.commit()
        assert user.wants_email('assignment') is False
        assert user.wants_email('result') is False


def test_email_dispatch_rendering(app_instance):
    with app_instance.app_context():
        user = User.query.filter_by(email='student@campusconnect.com').first()
        ann = Announcement.query.first()
        assign = Assignment.query.first()
        result = Result.query.first()
        event = CampusEvent.query.first()

        assert send_announcement_email(user, ann) is True
        assert send_assignment_created_email(user, assign) is True
        assert send_assignment_due_reminder_email(user, assign) is True
        assert send_result_published_email(user, result) is True
        assert send_event_registration_email(user, event) is True
        assert send_test_email(user) is True
        assert send_attendance_alert_email(user, overall_percentage=72.0) is True


def test_notification_preferences_update_endpoint(client, app_instance):
    # Log in as student
    client.post('/auth/login', data={
        'email': 'student@campusconnect.com',
        'password': 'Student123!'
    }, follow_redirects=True)

    # Update notification preferences via POST
    response = client.post('/auth/profile/notifications', data={
        'email_notifications_enabled': '1',
        'email_announcements': '1',
        # email_assignments not included -> should be False
        'email_results': '1'
    }, follow_redirects=True)

    assert response.status_code == 200

    with app_instance.app_context():
        user = User.query.filter_by(email='student@campusconnect.com').first()
        assert user.email_announcements is True
        assert user.email_assignments is False
        assert user.email_results is True
