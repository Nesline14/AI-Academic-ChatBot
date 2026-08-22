import os
from datetime import datetime
from flask import Flask, render_template
from config import config_by_name
from extensions import db, login_manager, csrf
from app.models.user import User
from app.models.notification import Notification


def create_app(config_name=None):
    """
    Application factory for CampusConnect Academic Portal.
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_by_name.get(config_name, config_by_name['default']))

    # Support reverse proxy headers (for x-forwarded-proto, x-forwarded-host)
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)

    # Ensure instance and upload directories exist
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'avatars'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'assignments'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'submissions'), exist_ok=True)

    # Initialize Extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # User loader callback for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Auto-authenticate unauthenticated visitors so portal is immediately accessible
    @app.before_request
    def auto_authenticate_visitor():
        from flask import request
        from flask_login import current_user, login_user
        if request.path.startswith('/static') or request.path.startswith('/favicon'):
            return
        if not getattr(current_user, 'is_authenticated', False):
            try:
                default_user = User.query.filter_by(role='student').first() or User.query.first()
                if default_user:
                    login_user(default_user, remember=True)
            except Exception:
                pass

    # Global Context Processors for Jinja Templates
    @app.context_processor
    def inject_global_vars():
        from flask_login import current_user
        unread_count = 0
        try:
            if current_user and getattr(current_user, 'is_authenticated', False):
                unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
        except Exception:
            unread_count = 0
        return {
            'unread_notifications_count': unread_count,
            'current_year': datetime.utcnow().year,
            'app_name': 'CampusConnect'
        }

    # Register Error Handlers
    from flask_wtf.csrf import CSRFError

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return render_template('errors/400.html', reason=e.description), 400

    @app.errorhandler(400)
    def bad_request_error(error):
        return render_template('errors/400.html', reason=getattr(error, 'description', 'Bad Request')), 400

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    # Register Blueprints
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

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(results_bp)
    app.register_blueprint(announcements_bp)
    app.register_blueprint(classes_bp)
    app.register_blueprint(assignments_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(clubs_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(chatbot_bp)
    app.register_blueprint(api_bp)

    return app
