from flask import Blueprint, render_template, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from extensions import db
from app.models.notification import Notification

notifications_bp = Blueprint('notifications', __name__, url_prefix='/notifications')


@notifications_bp.route('/')
@login_required
def index():
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    return render_template('notifications/index.html', notifications=notifications)


@notifications_bp.route('/read/<int:notification_id>', methods=['POST', 'GET'])
@login_required
def mark_read(notification_id):
    notif = Notification.query.filter_by(id=notification_id, user_id=current_user.id).first_or_404()
    notif.is_read = True
    db.session.commit()
    if notif.link_url:
        return redirect(notif.link_url)
    return redirect(url_for('notifications.index'))


@notifications_bp.route('/mark-all-read', methods=['POST'])
@login_required
def mark_all_read():
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    flash('All notifications marked as read.', 'success')
    return redirect(url_for('notifications.index'))


@notifications_bp.route('/unread-count')
@login_required
def unread_count():
    count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    return jsonify({'unread_count': count})
