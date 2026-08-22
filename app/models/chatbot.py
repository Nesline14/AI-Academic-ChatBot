from datetime import datetime
from extensions import db


class ChatMessage(db.Model):
    """Chat message history between student and CampusBot."""
    __tablename__ = 'chat_messages'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    intent = db.Column(db.String(50), nullable=True)  # e.g., 'attendance', 'assignments', 'results', 'events', 'general'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', back_populates='chat_logs')

    def __repr__(self):
        return f'<ChatMessage User:{self.user_id} Intent:{self.intent} Time:{self.timestamp}>'
