from datetime import datetime
from extensions import db


class CampusEvent(db.Model):
    """Campus events, workshops, cultural fests, and seminars."""
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    # Category: Academic, Cultural, Sports, Workshop, Seminar, Competition, Club Activity
    category = db.Column(db.String(50), default='Academic')
    
    event_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.String(10), nullable=False)  # e.g., '14:00'
    end_time = db.Column(db.String(10), nullable=True)    # e.g., '17:00'
    location = db.Column(db.String(150), nullable=False)  # e.g., 'Auditorium A'
    
    organizer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    organizing_body = db.Column(db.String(100), default='Student Affairs')
    
    max_participants = db.Column(db.Integer, default=100)
    registration_deadline = db.Column(db.DateTime, nullable=True)
    banner_url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    organizer = db.relationship('User', foreign_keys=[organizer_id], backref='organized_events')
    registrations = db.relationship('EventRegistration', back_populates='event', cascade='all, delete-orphan', lazy=True)

    @property
    def registered_count(self):
        return len(self.registrations)

    @property
    def is_full(self):
        return self.max_participants > 0 and self.registered_count >= self.max_participants

    @property
    def is_past(self):
        return self.event_date < datetime.utcnow().date()

    @property
    def category_badge_class(self):
        badges = {
            'Academic': 'primary',
            'Cultural': 'warning text-dark',
            'Sports': 'success',
            'Workshop': 'info',
            'Seminar': 'dark',
            'Competition': 'danger',
            'Club Activity': 'secondary'
        }
        return badges.get(self.category, 'primary')

    def is_user_registered(self, user_id):
        return any(r.user_id == user_id for r in self.registrations)

    def __repr__(self):
        return f'<CampusEvent {self.title} on {self.event_date}>'


class EventRegistration(db.Model):
    """User registration record for campus events."""
    __tablename__ = 'event_registrations'

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Status: 'Registered', 'Attended', 'Cancelled'
    status = db.Column(db.String(20), default='Registered')

    # Relationships
    event = db.relationship('CampusEvent', back_populates='registrations')
    user = db.relationship('User', back_populates='event_registrations')

    def __repr__(self):
        return f'<EventRegistration User:{self.user_id} Event:{self.event_id}>'
