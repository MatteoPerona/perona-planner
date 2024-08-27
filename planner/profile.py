from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from . import db
from .models import Project, Task
import datetime

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile')
@login_required
def profile():
    # Load projects for the dropdown
    projects = Project.query.filter_by(user_id=current_user.id)
    tasks = {
        project.id: list(Task.query.filter_by(project_id=project.id)) \
        for project in projects
    }

    # List of colors to choose from
    colors = [
        ('#A1612B', 'Rust'),
        ('#056DAC', 'Blue'),
        ('#03A0DA', 'Sky'),
        ('#969741', 'Booger'),
        ('#83898A', 'Stone'),
        ('#423F24', 'Army'),
        ('#2D3638', 'Graphite'),
    ]

    return render_template(
        'profile.html', 
        projects=projects, 
        tasks=tasks,
        colors=colors,
        name=current_user.username
    )

@profile_bp.route('/add_project', methods=['POST'])
def add_project():
    title = request.form.get('title')
    color = request.form.get('color')
    new_project = Project(title=title, color=color, user_id=current_user.id)  # assuming user authentication
    db.session.add(new_project)
    db.session.commit()
    return redirect(url_for('profile.profile'))  # Redirect back to the profile page

@profile_bp.route('/add_task', methods=['POST'])
def add_task():
    title = request.form.get('title')
    project_id = request.form.get('project_id')

    start_date = datetime.datetime.strptime(request.form['start_date'], '%Y-%m-%d')
    end_date = datetime.datetime.strptime(request.form['end_date'], '%Y-%m-%d')

    if start_date > end_date:
        flash('Start date cannot be after the end date.', 'error')  # Flash error message
        return redirect(url_for('profile.profile'))  # Redirect back to the task form

    task_type = request.form.get('task_type')

    new_task = Task(
        title=title, 
        project_id=project_id, 
        start_time=start_date, 
        end_time=end_date,
        task_type = task_type
    )
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for('profile.profile'))  # Redirect back to the profile page

# DELETE TASKS AND PROJECTS #

@profile_bp.route('/delete_project/<int:project_id>', methods=['POST'])
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    return redirect(url_for('profile.profile'))

@profile_bp.route('/delete_task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('profile.profile'))

# EDIT TASKS AND PROJECTS #

@profile_bp.route('/edit_project/<int:project_id>', methods=['POST'])
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)  # Fetch the project or return 404
    new_title = request.form['new_title']  # Get the new title from the form
    new_color = request.form['new_color']  # Get the new color from the form

    # Update the project's attributes
    project.title = new_title
    project.color = new_color
    db.session.commit()  # Commit the changes to the database

    return redirect(url_for('profile.profile'))  # Redirect back to the profile page or wherever appropriate


@profile_bp.route('/edit_task/<int:task_id>', methods=['POST'])
def edit_task(task_id):
    task = Task.query.get_or_404(task_id) 
    new_title = request.form['new_title'] 
    new_project_id = request.form['new_project_id']  
    new_start_date = datetime.datetime.strptime(request.form['new_start_date'], '%Y-%m-%d')
    new_end_date = datetime.datetime.strptime(request.form['new_end_date'], '%Y-%m-%d')
    new_task_type = request.form['new_task_type']

    # Update the project's title
    task.title = new_title
    task.project_id = new_project_id
    task.start_time = new_start_date
    task.end_time = new_end_date
    task.task_type = new_task_type
    db.session.commit()  # Commit the changes to the database

    return redirect(url_for('profile.profile'))  # Redirect back to the profile page or wherever appropriate


@profile_bp.route('/task_completion/<int:task_id>', methods=['POST'])
def task_completion(task_id):
    task = Task.query.get_or_404(task_id)
    
    data = request.get_json()
    task_completed = data.get('task_completed', False)

    task.completed = task_completed
    db.session.commit()

    return jsonify({'status': 'success', 'task_completed': task_completed})
    