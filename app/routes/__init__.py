from app.routes.auth import auth_bp
from app.routes.dashboard import dashboard_bp
from app.routes.attendance import attendance_bp
from app.routes.results import results_bp
from app.routes.announcements import announcements_bp
from app.routes.classes import classes_bp
from app.routes.assignments import assignments_bp
from app.routes.events import events_bp
from app.routes.projects import projects_bp
from app.routes.clubs import clubs_bp
from app.routes.notifications import notifications_bp
from app.routes.chatbot import chatbot_bp
from app.routes.api import api_bp

__all__ = [
    'auth_bp',
    'dashboard_bp',
    'attendance_bp',
    'results_bp',
    'announcements_bp',
    'classes_bp',
    'assignments_bp',
    'events_bp',
    'projects_bp',
    'clubs_bp',
    'notifications_bp',
    'chatbot_bp',
    'api_bp'
]
