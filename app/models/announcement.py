from datetime import datetime
from extensions import db


class Announcement(db.Model):
    """Campus announcements and official notices."""
    __tablename__ = 'announcements'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Priority: 'Low', 'Medium', 'High', 'Urgent'
    priority = db.Column(db.String(20), default='Medium')
    
    # Category: 'Academic', 'Examination', 'Event', 'General', 'Urgent'
    category = db.Column(db.String(30), default='General')
    
    # Target audience: 'All', 'Students', 'Teachers', 'Class', 'Department'
    target_role = db.Column(db.String(30), default='All')
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=True)
    
    expiry_date = db.Column(db.Date, nullable=True)
    is_pinned = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    author = db.relationship('User', backref='announcements_authored')
    department = db.relationship('Department', backref='announcements')
    classroom = db.relationship('ClassRoom', backref='announcements')

    @property
    def priority_badge_class(self):
        badges = {
            'Low': 'secondary',
            'Medium': 'info',
            'High': 'warning text-dark',
            'Urgent': 'danger'
        }
        return badges.get(self.priority, 'secondary')

    @property
    def category_badge_class(self):
        badges = {
            'Academic': 'primary',
            'Examination': 'danger',
            'Event': 'success',
            'General': 'secondary',
            'Urgent': 'dark'
        }
        return badges.get(self.category, 'primary')

    def __repr__(self):
        return f'<Announcement {self.title[:30]} ({self.category})>'
