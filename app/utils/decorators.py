from functools import wraps
from flask import abort, flash, redirect, url_for, request
from flask_login import current_user


def role_required(*roles):
    """Decorator to enforce role-based access control."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please sign in to access this page.', 'warning')
                return redirect(url_for('auth.login', next=request.url))
            
            if current_user.role not in roles and current_user.role != 'admin':
                flash('Access denied: You do not have permission to view this resource.', 'danger')
                abort(403)
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    """Requires strictly Admin role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please sign in as Administrator.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        if not current_user.is_admin:
            flash('Administrator privileges required.', 'danger')
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def teacher_required(f):
    """Requires Teacher or Admin role."""
    return role_required('teacher', 'admin')(f)


def student_required(f):
    """Requires Student or Admin role."""
    return role_required('student', 'admin')(f)


def coordinator_required(f):
    """Requires Club Coordinator or Admin role."""
    return role_required('coordinator', 'admin')(f)
