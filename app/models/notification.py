from datetime import datetime
from extensions import db


class Notification(db.Model):
    """User notifications for assignments, results, announcements, and events."""
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    
    # Category: 'announcement', 'assignment', 'result', 'event', 'project', 'club', 'attendance', 'system'
    category = db.Column(db.String(30), default='system')
    link_url = db.Column(db.String(255), nullable=True)
    is_read = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', back_populates='notifications')

    @property
    def icon(self):
        icons = {
            'announcement': 'bi-megaphone',
            'assignment': 'bi-journal-check',
            'result': 'bi-mortarboard',
            'event': 'bi-calendar-event',
            'project': 'bi-kanban',
            'club': 'bi-people',
            'attendance': 'bi-clock-history',
            'system': 'bi-bell'
        }
        return icons.get(self.category, 'bi-bell')

    @property
    def badge_color(self):
        colors = {
            'announcement': 'warning text-dark',
            'assignment': 'primary',
            'result': 'success',
            'event': 'info text-dark',
            'project': 'dark',
            'club': 'secondary',
            'attendance': 'danger',
            'system': 'light text-dark'
        }
        return colors.get(self.category, 'secondary')

    def __repr__(self):
        return f'<Notification User:{self.user_id} Title:{self.title} Read:{self.is_read}>'
