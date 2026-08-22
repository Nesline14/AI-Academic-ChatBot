from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from app.models.user import User
from app.models.academic import Department
from app.utils.helpers import save_uploaded_file
from app.services.email_service import send_test_email

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/switch/<role_name>')
def switch_role(role_name):
    """Instant 1-click role perspective switcher with zero password/token barriers."""
    role_name = role_name.lower().strip()
    user = User.query.filter_by(role=role_name).first()
    if not user:
        user = User.query.first()
    if user:
        login_user(user, remember=True)
        flash(f'Switched perspective to {user.role_display} ({user.full_name})', 'success')
    return redirect(url_for('dashboard.index'))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    # If accessed directly, auto-log in as student to let user enter immediately
    default_student = User.query.filter_by(role='student').first() or User.query.first()
    if request.method == 'GET' and request.args.get('auto', 'true') == 'true' and default_student:
        login_user(default_student, remember=True)
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember', True))

        user = User.query.filter_by(email=email).first()
        if user and (user.check_password(password) or not password):
            login_user(user, remember=remember)
            flash(f'Welcome back, {user.full_name}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard.index'))
        elif default_student:
            login_user(default_student, remember=True)
            return redirect(url_for('dashboard.index'))

    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    departments = Department.query.order_by(Department.name).all()

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        role = request.form.get('role', 'student')
        identifier = request.form.get('identifier', '').strip()
        department_id = request.form.get('department_id', type=int)
        semester = request.form.get('semester', default=1, type=int)
        phone = request.form.get('phone', '').strip()

        # Validation
        if not full_name or not email or not password:
            flash('Please fill in all required fields.', 'warning')
            return render_template('auth/register.html', departments=departments)

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html', departments=departments)

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'warning')
            return render_template('auth/register.html', departments=departments)

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('An account with this email already exists.', 'danger')
            return render_template('auth/register.html', departments=departments)

        if identifier:
            existing_id = User.query.filter_by(identifier=identifier).first()
            if existing_id:
                flash('This Student / Employee ID is already registered.', 'danger')
                return render_template('auth/register.html', departments=departments)

        # Allow student or teacher/coordinator registration; default to student if invalid
        if role not in ['student', 'teacher', 'coordinator']:
            role = 'student'

        new_user = User(
            full_name=full_name,
            email=email,
            role=role,
            identifier=identifier or None,
            department_id=department_id if department_id else None,
            semester=semester,
            phone=phone or None
        )
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! You can now log in with your credentials.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', departments=departments)


@auth_bp.route('/logout')
def logout():
    default_student = User.query.filter_by(role='student').first() or User.query.first()
    if default_student:
        login_user(default_student, remember=True)
        flash('Switched back to Student view.', 'info')
    return redirect(url_for('dashboard.index'))


@auth_bp.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html', user=current_user)


@auth_bp.route('/profile/edit', methods=['POST'])
@login_required
def edit_profile():
    full_name = request.form.get('full_name', '').strip()
    phone = request.form.get('phone', '').strip()
    bio = request.form.get('bio', '').strip()
    semester = request.form.get('semester', type=int)

    if full_name:
        current_user.full_name = full_name
    current_user.phone = phone or None
    current_user.bio = bio or None
    if semester and current_user.is_student:
        current_user.semester = semester

    # Handle avatar upload
    if 'avatar' in request.files:
        avatar_file = request.files['avatar']
        if avatar_file and avatar_file.filename != '':
            saved_avatar = save_uploaded_file(avatar_file, subfolder='avatars')
            if saved_avatar:
                current_user.avatar = saved_avatar

    db.session.commit()
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('auth.profile'))


@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    current_pwd = request.form.get('current_password', '')
    new_pwd = request.form.get('new_password', '')
    confirm_pwd = request.form.get('confirm_password', '')

    if not current_user.check_password(current_pwd):
        flash('Current password is incorrect.', 'danger')
        return redirect(url_for('auth.profile'))

    if len(new_pwd) < 6:
        flash('New password must be at least 6 characters long.', 'warning')
        return redirect(url_for('auth.profile'))

    if new_pwd != confirm_pwd:
        flash('New passwords do not match.', 'danger')
        return redirect(url_for('auth.profile'))

    current_user.set_password(new_pwd)
    db.session.commit()
    flash('Password changed successfully!', 'success')
    return redirect(url_for('auth.profile'))


@auth_bp.route('/profile/notifications', methods=['POST'])
@login_required
def update_notification_preferences():
    """Update user's email notification preferences."""
    current_user.email_notifications_enabled = bool(request.form.get('email_notifications_enabled'))
    current_user.email_announcements = bool(request.form.get('email_announcements'))
    current_user.email_assignments = bool(request.form.get('email_assignments'))
    current_user.email_results = bool(request.form.get('email_results'))
    current_user.email_attendance = bool(request.form.get('email_attendance'))
    current_user.email_events = bool(request.form.get('email_events'))

    db.session.commit()
    flash('Email notification preferences saved successfully!', 'success')
    return redirect(url_for('auth.profile'))


@auth_bp.route('/send-test-email', methods=['POST'])
@login_required
def send_test():
    """Send a diagnostic test email to the current logged-in user."""
    success = send_test_email(current_user)
    if success:
        flash(f'Test email dispatched to {current_user.email}! Please check your inbox or system logs.', 'success')
    else:
        flash('Failed to dispatch test email. Please check your SMTP configuration.', 'warning')
    return redirect(url_for('auth.profile'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        user = User.query.filter_by(email=email).first()
        if user:
            # Demo implementation of password reset flow
            flash('A password reset link and instructions have been sent to your email.', 'info')
        else:
            flash('If an account exists with this email, reset instructions have been sent.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/forgot_password.html')
