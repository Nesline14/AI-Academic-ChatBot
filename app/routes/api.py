from datetime import datetime, date
from flask import Blueprint, jsonify, request
from flask_login import current_user
from extensions import csrf
from app.models.announcement import Announcement
from app.models.event import CampusEvent
from app.models.assignment import Assignment
from app.models.notification import Notification
from app.models.user import User
from app.models.academic import ClassRoom, Department

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/health', methods=['GET'])
@csrf.exempt
def health_check():
    """Service health monitoring check endpoint."""
    return jsonify({
        'service': 'CampusConnect Student Academic Management System',
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    }), 200


@api_bp.route('/announcements', methods=['GET'])
@csrf.exempt
def get_announcements():
    """Retrieve list of active announcements."""
    limit = request.args.get('limit', default=10, type=int)
    announcements = Announcement.query.order_by(Announcement.is_pinned.desc(), Announcement.created_at.desc()).limit(limit).all()
    
    return jsonify({
        'count': len(announcements),
        'announcements': [{
            'id': a.id,
            'title': a.title,
            'content': a.content,
            'category': a.category,
            'priority': a.priority,
            'target_role': a.target_role,
            'author': a.author.full_name if a.author else 'System',
            'created_at': a.created_at.isoformat()
        } for a in announcements]
    })


@api_bp.route('/events', methods=['GET'])
@csrf.exempt
def get_events():
    """Retrieve campus events."""
    limit = request.args.get('limit', default=10, type=int)
    events = CampusEvent.query.filter(CampusEvent.event_date >= date.today()).order_by(CampusEvent.event_date.asc()).limit(limit).all()

    return jsonify({
        'count': len(events),
        'events': [{
            'id': e.id,
            'title': e.title,
            'description': e.description,
            'category': e.category,
            'event_date': e.event_date.isoformat(),
            'start_time': e.start_time,
            'location': e.location,
            'max_participants': e.max_participants,
            'registered_count': e.registered_count
        } for e in events]
    })


@api_bp.route('/assignments', methods=['GET'])
@csrf.exempt
def get_assignments():
    """Retrieve public assignment metadata."""
    limit = request.args.get('limit', default=10, type=int)
    assignments = Assignment.query.order_by(Assignment.due_date.asc()).limit(limit).all()

    return jsonify({
        'count': len(assignments),
        'assignments': [{
            'id': a.id,
            'title': a.title,
            'description': a.description,
            'subject': a.subject.name if a.subject else 'General',
            'class': a.classroom.name if a.classroom else 'All',
            'due_date': a.due_date.isoformat(),
            'max_marks': a.max_marks
        } for a in assignments]
    })


@api_bp.route('/notifications', methods=['GET'])
@csrf.exempt
def get_notifications():
    """Retrieve notifications for current session user."""
    if not current_user.is_authenticated:
        return jsonify({'error': 'Authentication required'}), 401

    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).limit(15).all()

    return jsonify({
        'count': len(notifications),
        'notifications': [{
            'id': n.id,
            'title': n.title,
            'message': n.message,
            'category': n.category,
            'link_url': n.link_url,
            'is_read': n.is_read,
            'created_at': n.created_at.isoformat()
        } for n in notifications]
    })


@api_bp.route('/stats', methods=['GET'])
@csrf.exempt
def get_stats():
    """Public platform statistics overview."""
    return jsonify({
        'total_students': User.query.filter_by(role='student').count(),
        'total_teachers': User.query.filter_by(role='teacher').count(),
        'total_classes': ClassRoom.query.count(),
        'total_departments': Department.query.count(),
        'total_events': CampusEvent.query.count()
    })
