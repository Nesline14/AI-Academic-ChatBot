from datetime import datetime
from extensions import db


class Club(db.Model):
    """Student societies, technical chapters, and interest clubs."""
    __tablename__ = 'clubs'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    code = db.Column(db.String(30), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)
    
    # Category: 'Technical', 'Cultural', 'Sports', 'Literary', 'Social Impact', 'Innovation'
    category = db.Column(db.String(50), default='Technical')
    
    coordinator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    logo_url = db.Column(db.String(255), nullable=True)
    meeting_schedule = db.Column(db.String(100), default='Every Friday at 4:00 PM')
    website_url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    coordinator = db.relationship('User', foreign_keys=[coordinator_id], backref='coordinated_clubs')
    members = db.relationship('ClubMember', back_populates='club', cascade='all, delete-orphan', lazy=True)
    activities = db.relationship('ClubActivity', back_populates='club', cascade='all, delete-orphan', lazy=True)

    @property
    def member_count(self):
        return len(self.members)

    @property
    def category_badge_class(self):
        badges = {
            'Technical': 'primary',
            'Cultural': 'warning text-dark',
            'Sports': 'success',
            'Literary': 'info',
            'Social Impact': 'danger',
            'Innovation': 'dark'
        }
        return badges.get(self.category, 'secondary')

    def is_student_member(self, student_id):
        return any(m.student_id == student_id for m in self.members)

    def __repr__(self):
        return f'<Club {self.name} ({self.category})>'


class ClubMember(db.Model):
    """Club membership records."""
    __tablename__ = 'club_members'

    id = db.Column(db.Integer, primary_key=True)
    club_id = db.Column(db.Integer, db.ForeignKey('clubs.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Role: 'Member', 'Leader', 'Treasurer', 'Secretary', 'Vice President'
    role = db.Column(db.String(50), default='Member')
    status = db.Column(db.String(20), default='Active')  # 'Active', 'Pending'
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    club = db.relationship('Club', back_populates='members')
    student = db.relationship('User', back_populates='club_memberships')

    def __repr__(self):
        return f'<ClubMember Club:{self.club_id} Student:{self.student_id} Role:{self.role}>'


class ClubActivity(db.Model):
    """Events, workshops, and weekly meetups organized by clubs."""
    __tablename__ = 'club_activities'

    id = db.Column(db.Integer, primary_key=True)
    club_id = db.Column(db.Integer, db.ForeignKey('clubs.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    activity_date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(150), default='Club Hub')
    points = db.Column(db.Integer, default=10)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    club = db.relationship('Club', back_populates='activities')

    def __repr__(self):
        return f'<ClubActivity {self.title} Date:{self.activity_date}>'
