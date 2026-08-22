from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from app.models.project import AcademicProject, ProjectMember
from app.models.user import User
from app.services.notification_service import send_notification

projects_bp = Blueprint('projects', __name__, url_prefix='/projects')


@projects_bp.route('/')
@login_required
def index():
    status_filter = request.args.get('status', '')
    category_filter = request.args.get('category', '')

    query = AcademicProject.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    if category_filter:
        query = query.filter_by(category=category_filter)

    projects = query.order_by(AcademicProject.created_at.desc()).all()
    categories = ['Web Development', 'Machine Learning', 'IoT', 'Mobile App', 'Research', 'Embedded Systems', 'Cloud Computing']
    statuses = ['Planning', 'In Progress', 'Completed', 'On Hold']

    return render_template(
        'projects/index.html',
        projects=projects,
        categories=categories,
        statuses=statuses,
        selected_status=status_filter,
        selected_category=category_filter
    )


@projects_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    teachers = User.query.filter_by(role='teacher', is_active_account=True).order_by(User.full_name).all()
    students = User.query.filter_by(role='student', is_active_account=True).order_by(User.full_name).all()
    categories = ['Web Development', 'Machine Learning', 'IoT', 'Mobile App', 'Research', 'Embedded Systems', 'Cloud Computing']

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', 'Web Development')
        guide_id = request.form.get('guide_id', type=int)
        deadline_str = request.form.get('deadline')
        repository_url = request.form.get('repository_url', '').strip()
        selected_members = request.form.getlist('team_members')

        if not title or not description:
            flash('Project title and description are required.', 'warning')
            return render_template('projects/create.html', teachers=teachers, students=students, categories=categories)

        deadline = None
        if deadline_str:
            try:
                deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date()
            except ValueError:
                deadline = None

        new_project = AcademicProject(
            title=title,
            description=description,
            category=category,
            creator_id=current_user.id,
            guide_id=guide_id if guide_id else None,
            deadline=deadline,
            repository_url=repository_url or None,
            status='Planning',
            progress_percentage=10
        )
        db.session.add(new_project)
        db.session.flush()

        # Add creator as lead member
        lead_member = ProjectMember(project_id=new_project.id, student_id=current_user.id, role_in_project='Project Lead')
        db.session.add(lead_member)

        # Add team members
        for m_id_str in selected_members:
            try:
                m_id = int(m_id_str)
                if m_id != current_user.id:
                    member_obj = ProjectMember(project_id=new_project.id, student_id=m_id, role_in_project='Collaborator')
                    db.session.add(member_obj)
                    send_notification(
                        user_id=m_id,
                        title='Added to Academic Project',
                        message=f'You have been added to "{title}" by {current_user.full_name}.',
                        category='project',
                        link_url=f'/projects/{new_project.id}'
                    )
            except ValueError:
                continue

        db.session.commit()
        flash(f'Project "{title}" created successfully!', 'success')
        return redirect(url_for('projects.detail', project_id=new_project.id))

    return render_template('projects/create.html', teachers=teachers, students=students, categories=categories)


@projects_bp.route('/<int:project_id>')
@login_required
def detail(project_id):
    project = AcademicProject.query.get_or_404(project_id)
    is_member = project.is_member(current_user.id)
    is_guide = project.guide_id == current_user.id or current_user.is_admin
    students = User.query.filter_by(role='student', is_active_account=True).order_by(User.full_name).all()
    current_member_ids = {m.student_id for m in project.members}
    available_students = [s for s in students if s.id not in current_member_ids]

    return render_template(
        'projects/detail.html',
        project=project,
        is_member=is_member,
        is_guide=is_guide,
        available_students=available_students
    )


@projects_bp.route('/<int:project_id>/update-progress', methods=['POST'])
@login_required
def update_progress(project_id):
    project = AcademicProject.query.get_or_404(project_id)
    if not project.is_member(current_user.id) and not current_user.is_admin and project.guide_id != current_user.id:
        flash('Unauthorized to update this project.', 'danger')
        return redirect(url_for('projects.detail', project_id=project_id))

    status = request.form.get('status', project.status)
    progress = request.form.get('progress_percentage', type=int)
    repo_url = request.form.get('repository_url', '').strip()

    if status in ['Planning', 'In Progress', 'Completed', 'On Hold']:
        project.status = status
    if progress is not None and 0 <= progress <= 100:
        project.progress_percentage = progress
    if repo_url:
        project.repository_url = repo_url

    db.session.commit()
    flash('Project progress updated!', 'success')
    return redirect(url_for('projects.detail', project_id=project_id))


@projects_bp.route('/<int:project_id>/feedback', methods=['POST'])
@login_required
def give_feedback(project_id):
    project = AcademicProject.query.get_or_404(project_id)
    if project.guide_id != current_user.id and not current_user.is_admin:
        flash('Only the assigned mentor/guide or admin can give evaluation feedback.', 'danger')
        return redirect(url_for('projects.detail', project_id=project_id))

    feedback_text = request.form.get('feedback', '').strip()
    project.feedback = feedback_text
    db.session.commit()

    # Notify project creator
    send_notification(
        user_id=project.creator_id,
        title='Mentor Feedback on Project',
        message=f'{current_user.full_name} provided feedback on "{project.title}".',
        category='project',
        link_url=f'/projects/{project.id}'
    )

    flash('Feedback recorded and sent to team!', 'success')
    return redirect(url_for('projects.detail', project_id=project_id))
