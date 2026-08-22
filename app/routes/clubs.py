from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from app.models.club import Club, ClubMember, ClubActivity
from app.models.user import User
from app.services.notification_service import send_notification
from app.utils.decorators import role_required

clubs_bp = Blueprint('clubs', __name__, url_prefix='/clubs')


@clubs_bp.route('/')
@login_required
def index():
    category = request.args.get('category', '')
    query = Club.query
    if category:
        query = query.filter_by(category=category)

    clubs = query.order_by(Club.name).all()
    categories = ['Technical', 'Cultural', 'Sports', 'Literary', 'Social Impact', 'Innovation']

    return render_template('clubs/index.html', clubs=clubs, categories=categories, selected_category=category)


@clubs_bp.route('/create', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'coordinator')
def create():
    categories = ['Technical', 'Cultural', 'Sports', 'Literary', 'Social Impact', 'Innovation']
    coordinators = User.query.filter(User.role.in_(['coordinator', 'teacher', 'admin'])).order_by(User.full_name).all()

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        code = request.form.get('code', '').strip().upper()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', 'Technical')
        coordinator_id = request.form.get('coordinator_id', type=int) or current_user.id
        meeting_schedule = request.form.get('meeting_schedule', 'Every Friday at 4:00 PM').strip()
        website_url = request.form.get('website_url', '').strip()

        if not name or not code or not description:
            flash('Name, code, and description are required.', 'warning')
            return render_template('clubs/create.html', categories=categories, coordinators=coordinators)

        existing = Club.query.filter((Club.name == name) | (Club.code == code)).first()
        if existing:
            flash('A club with this name or code already exists.', 'danger')
            return render_template('clubs/create.html', categories=categories, coordinators=coordinators)

        new_club = Club(
            name=name,
            code=code,
            description=description,
            category=category,
            coordinator_id=coordinator_id,
            meeting_schedule=meeting_schedule,
            website_url=website_url or None
        )
        db.session.add(new_club)
        db.session.commit()

        flash(f'Club "{name}" registered successfully!', 'success')
        return redirect(url_for('clubs.detail', club_id=new_club.id))

    return render_template('clubs/create.html', categories=categories, coordinators=coordinators)


@clubs_bp.route('/<int:club_id>')
@login_required
def detail(club_id):
    club = Club.query.get_or_404(club_id)
    is_member = club.is_student_member(current_user.id)
    is_manager = current_user.is_admin or club.coordinator_id == current_user.id

    return render_template('clubs/detail.html', club=club, is_member=is_member, is_manager=is_manager)


@clubs_bp.route('/<int:club_id>/join', methods=['POST'])
@login_required
def join_club(club_id):
    club = Club.query.get_or_404(club_id)
    existing = ClubMember.query.filter_by(club_id=club_id, student_id=current_user.id).first()

    if existing:
        flash('You are already a member of this club.', 'info')
    else:
        member = ClubMember(club_id=club_id, student_id=current_user.id, role='Member', status='Active')
        db.session.add(member)
        db.session.commit()

        # Send notification to student & coordinator
        send_notification(
            user_id=current_user.id,
            title='Club Membership Active',
            message=f'Welcome to {club.name}! Check out regular meetups and activities.',
            category='club',
            link_url=f'/clubs/{club.id}'
        )

        flash(f'Welcome to {club.name}! You are now an active member.', 'success')

    return redirect(url_for('clubs.detail', club_id=club_id))


@clubs_bp.route('/<int:club_id>/leave', methods=['POST'])
@login_required
def leave_club(club_id):
    member = ClubMember.query.filter_by(club_id=club_id, student_id=current_user.id).first_or_404()
    db.session.delete(member)
    db.session.commit()
    flash('You have left the club.', 'info')
    return redirect(url_for('clubs.detail', club_id=club_id))


@clubs_bp.route('/<int:club_id>/add-activity', methods=['POST'])
@login_required
def add_activity(club_id):
    club = Club.query.get_or_404(club_id)
    if not current_user.is_admin and club.coordinator_id != current_user.id:
        flash('Only the coordinator or admin can post club activities.', 'danger')
        return redirect(url_for('clubs.detail', club_id=club_id))

    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    act_date_str = request.form.get('activity_date')
    location = request.form.get('location', 'Club Hub').strip()
    points = request.form.get('points', default=10, type=int)

    if not title or not description or not act_date_str:
        flash('Activity title, description, and date are required.', 'warning')
        return redirect(url_for('clubs.detail', club_id=club_id))

    try:
        activity_date = datetime.strptime(act_date_str, '%Y-%m-%dT%H:%M')
    except ValueError:
        activity_date = datetime.strptime(act_date_str, '%Y-%m-%d')

    new_act = ClubActivity(
        club_id=club_id,
        title=title,
        description=description,
        activity_date=activity_date,
        location=location,
        points=points
    )
    db.session.add(new_act)
    db.session.commit()

    flash(f'Club activity "{title}" added!', 'success')
    return redirect(url_for('clubs.detail', club_id=club_id))
