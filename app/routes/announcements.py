from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from app.models.announcement import Announcement
from app.models.academic import Department, ClassRoom
from app.models.user import User
from app.services.notification_service import send_bulk_notification
from app.services.email_service import send_bulk_announcement_email
from app.utils.decorators import teacher_required

announcements_bp = Blueprint('announcements', __name__, url_prefix='/announcements')


@announcements_bp.route('/')
@login_required
def index():
    category = request.args.get('category', '')
    priority = request.args.get('priority', '')
    query_str = request.args.get('q', '').strip()

    query = Announcement.query

    # Target role filter for students vs teachers
    if current_user.is_student:
        query = query.filter(Announcement.target_role.in_(['All', 'Students']))
    elif current_user.is_teacher:
        query = query.filter(Announcement.target_role.in_(['All', 'Teachers']))

    if category:
        query = query.filter_by(category=category)
    if priority:
        query = query.filter_by(priority=priority)
    if query_str:
        query = query.filter(
            (Announcement.title.ilike(f'%{query_str}%')) |
            (Announcement.content.ilike(f'%{query_str}%'))
        )

    announcements = query.order_by(Announcement.is_pinned.desc(), Announcement.created_at.desc()).all()

    return render_template(
        'announcements/index.html',
        announcements=announcements,
        selected_category=category,
        selected_priority=priority,
        search_query=query_str
    )


@announcements_bp.route('/create', methods=['GET', 'POST'])
@login_required
@teacher_required
def create():
    departments = Department.query.order_by(Department.name).all()
    classes = ClassRoom.query.order_by(ClassRoom.name).all()

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        category = request.form.get('category', 'General')
        priority = request.form.get('priority', 'Medium')
        target_role = request.form.get('target_role', 'All')
        department_id = request.form.get('department_id', type=int)
        class_id = request.form.get('class_id', type=int)
        is_pinned = bool(request.form.get('is_pinned'))
        expiry_str = request.form.get('expiry_date')

        if not title or not content:
            flash('Title and content are required.', 'warning')
            return render_template('announcements/create.html', departments=departments, classes=classes)

        expiry_date = None
        if expiry_str:
            try:
                expiry_date = datetime.strptime(expiry_str, '%Y-%m-%d').date()
            except ValueError:
                expiry_date = None

        new_ann = Announcement(
            title=title,
            content=content,
            category=category,
            priority=priority,
            target_role=target_role,
            department_id=department_id if department_id else None,
            class_id=class_id if class_id else None,
            is_pinned=is_pinned,
            expiry_date=expiry_date,
            author_id=current_user.id
        )
        db.session.add(new_ann)
        db.session.commit()

        # Send notifications to targeted users
        target_users = []
        if target_role == 'Students':
            target_users = User.query.filter_by(role='student', is_active_account=True).all()
        elif target_role == 'Teachers':
            target_users = User.query.filter_by(role='teacher', is_active_account=True).all()
        else:
            target_users = User.query.filter_by(is_active_account=True).all()

        user_ids = [u.id for u in target_users if u.id != current_user.id]
        if user_ids:
            send_bulk_notification(
                user_ids=user_ids,
                title=f'New Announcement: {title}',
                message=f'[{category}] {title}',
                category='announcement',
                link_url=f'/announcements/{new_ann.id}'
            )
            # Dispatch email notifications to users who opted in
            send_bulk_announcement_email(
                users=[u for u in target_users if u.id != current_user.id],
                announcement=new_ann
            )

        flash('Announcement published successfully!', 'success')
        return redirect(url_for('announcements.index'))

    return render_template('announcements/create.html', departments=departments, classes=classes)


@announcements_bp.route('/<int:announcement_id>')
@login_required
def detail(announcement_id):
    ann = Announcement.query.get_or_404(announcement_id)
    return render_template('announcements/detail.html', announcement=ann)


@announcements_bp.route('/delete/<int:announcement_id>', methods=['POST'])
@login_required
@teacher_required
def delete(announcement_id):
    ann = Announcement.query.get_or_404(announcement_id)
    if not current_user.is_admin and ann.author_id != current_user.id:
        flash('You can only delete your own announcements.', 'danger')
        return redirect(url_for('announcements.index'))

    db.session.delete(ann)
    db.session.commit()
    flash('Announcement deleted successfully.', 'info')
    return redirect(url_for('announcements.index'))
