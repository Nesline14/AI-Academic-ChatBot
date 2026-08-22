from datetime import datetime, date
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from app.models.event import CampusEvent, EventRegistration
from app.services.notification_service import send_notification
from app.services.email_service import send_event_registration_email
from app.utils.decorators import role_required

events_bp = Blueprint('events', __name__, url_prefix='/events')


@events_bp.route('/')
@login_required
def index():
    category = request.args.get('category', '')
    filter_type = request.args.get('filter', 'upcoming')  # upcoming, past, all
    today = date.today()

    query = CampusEvent.query
    if category:
        query = query.filter_by(category=category)

    if filter_type == 'upcoming':
        query = query.filter(CampusEvent.event_date >= today).order_by(CampusEvent.event_date.asc())
    elif filter_type == 'past':
        query = query.filter(CampusEvent.event_date < today).order_by(CampusEvent.event_date.desc())
    else:
        query = query.order_by(CampusEvent.event_date.asc())

    events = query.all()
    return render_template('events/index.html', events=events, selected_category=category, filter_type=filter_type)


@events_bp.route('/create', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'teacher', 'coordinator')
def create():
    categories = ['Academic', 'Cultural', 'Sports', 'Workshop', 'Seminar', 'Competition', 'Club Activity']

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', 'Academic')
        event_date_str = request.form.get('event_date')
        start_time = request.form.get('start_time', '10:00 AM').strip()
        end_time = request.form.get('end_time', '').strip()
        location = request.form.get('location', '').strip()
        organizing_body = request.form.get('organizing_body', 'Student Council').strip()
        max_participants = request.form.get('max_participants', default=100, type=int)

        if not title or not description or not event_date_str or not location:
            flash('Please fill in title, description, date, and location.', 'warning')
            return render_template('events/create.html', categories=categories)

        try:
            event_date = datetime.strptime(event_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid event date format.', 'danger')
            return render_template('events/create.html', categories=categories)

        new_event = CampusEvent(
            title=title,
            description=description,
            category=category,
            event_date=event_date,
            start_time=start_time,
            end_time=end_time or None,
            location=location,
            organizing_body=organizing_body,
            organizer_id=current_user.id,
            max_participants=max_participants
        )
        db.session.add(new_event)
        db.session.commit()

        flash(f'Campus Event "{title}" published successfully!', 'success')
        return redirect(url_for('events.detail', event_id=new_event.id))

    return render_template('events/create.html', categories=categories)


@events_bp.route('/<int:event_id>')
@login_required
def detail(event_id):
    event = CampusEvent.query.get_or_404(event_id)
    is_registered = event.is_user_registered(current_user.id)
    return render_template('events/detail.html', event=event, is_registered=is_registered)


@events_bp.route('/<int:event_id>/register', methods=['POST'])
@login_required
def register_event(event_id):
    event = CampusEvent.query.get_or_404(event_id)

    if event.is_past:
        flash('Cannot register for a past event.', 'warning')
        return redirect(url_for('events.detail', event_id=event_id))

    if event.is_full:
        flash('Sorry, this event has reached maximum capacity.', 'danger')
        return redirect(url_for('events.detail', event_id=event_id))

    existing = EventRegistration.query.filter_by(event_id=event_id, user_id=current_user.id).first()
    if existing:
        flash('You are already registered for this event.', 'info')
    else:
        reg = EventRegistration(event_id=event_id, user_id=current_user.id)
        db.session.add(reg)
        db.session.commit()

        # Send confirmation notification
        send_notification(
            user_id=current_user.id,
            title='Event Registration Confirmed',
            message=f'You have registered for "{event.title}" on {event.event_date.strftime("%b %d, %Y")} at {event.location}.',
            category='event',
            link_url=f'/events/{event.id}'
        )

        # Dispatch email confirmation
        send_event_registration_email(current_user, event)

        flash(f'Successfully registered for {event.title}!', 'success')

    return redirect(url_for('events.detail', event_id=event_id))


@events_bp.route('/<int:event_id>/cancel', methods=['POST'])
@login_required
def cancel_registration(event_id):
    reg = EventRegistration.query.filter_by(event_id=event_id, user_id=current_user.id).first_or_404()
    db.session.delete(reg)
    db.session.commit()
    flash('Event registration cancelled.', 'info')
    return redirect(url_for('events.detail', event_id=event_id))
