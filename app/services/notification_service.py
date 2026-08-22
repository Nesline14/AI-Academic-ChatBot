from extensions import db
from app.models.notification import Notification


def send_notification(user_id, title, message, category='system', link_url=None):
    """Create and dispatch a new in-app notification to a specific user."""
    notif = Notification(
        user_id=user_id,
        title=title,
        message=message,
        category=category,
        link_url=link_url,
        is_read=False
    )
    db.session.add(notif)
    db.session.commit()
    return notif


def send_bulk_notification(user_ids, title, message, category='system', link_url=None):
    """Create and dispatch notifications to multiple users at once."""
    notifs = []
    for uid in user_ids:
        notif = Notification(
            user_id=uid,
            title=title,
            message=message,
            category=category,
            link_url=link_url,
            is_read=False
        )
        db.session.add(notif)
        notifs.append(notif)
    
    db.session.commit()
    return notifs
