import os
from app import create_app
from extensions import db
from seed_data import seed_database
from sqlalchemy import text, inspect

# Create the Flask application instance
app = create_app(os.environ.get('FLASK_ENV', 'development'))


def ensure_db_schema():
    """Ensure newly introduced model columns exist in existing database tables."""
    inspector = inspect(db.engine)
    if 'users' in inspector.get_table_names():
        existing_cols = [c['name'] for c in inspector.get_columns('users')]
        user_new_cols = [
            ('email_notifications_enabled', 'BOOLEAN DEFAULT 1'),
            ('email_announcements', 'BOOLEAN DEFAULT 1'),
            ('email_assignments', 'BOOLEAN DEFAULT 1'),
            ('email_results', 'BOOLEAN DEFAULT 1'),
            ('email_attendance', 'BOOLEAN DEFAULT 1'),
            ('email_events', 'BOOLEAN DEFAULT 1'),
        ]
        for col_name, col_def in user_new_cols:
            if col_name not in existing_cols:
                try:
                    db.session.execute(text(f'ALTER TABLE users ADD COLUMN {col_name} {col_def}'))
                    db.session.commit()
                except Exception:
                    db.session.rollback()


# Ensure database tables and initial demo seed data are initialized
with app.app_context():
    db.create_all()
    ensure_db_schema()
    seed_database()

if __name__ == '__main__':
    # Bind to host 0.0.0.0 and port from environment (default 5000)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
