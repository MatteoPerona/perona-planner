from flask import Flask, Blueprint, render_template, request, current_app, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime
from . import db
from .models import Project, Task

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return 'Index'

# CREATE DELIVERABLES #

@main.route('/add_project', methods=['POST'])
def add_project():
    title = request.form.get('title')
    new_project = Project(title=title, user_id=current_user.id)  # assuming user authentication
    db.session.add(new_project)
    db.session.commit()
    return redirect(url_for('main.profile'))  # Redirect back to the profile page

@main.route('/add_task', methods=['POST'])
def add_task():
    title = request.form.get('title')
    project_id = request.form.get('project_id')

    start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
    end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d')

    new_task = Task(
        title=title, 
        project_id=project_id, 
        start_time=start_date, 
        end_time=end_date
    )
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for('main.profile'))  # Redirect back to the profile page

@main.route('/profile')
def profile():
    # Load projects for the dropdown
    projects = Project.query.all()
    tasks = {
        project.id: list(Task.query.filter_by(project_id=project.id)) \
        for project in projects
    }
    for project_id in tasks:
        try: current_app.logger.debug(tasks[project_id][0].title)
        except: current_app.logger.debug(None)

    return render_template(
        'profile.html', 
        projects=projects, 
        tasks=tasks,
        name=current_user.username)

# DELETE DELIVERABLES #

@main.route('/delete_project/<int:project_id>', methods=['POST'])
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    return redirect(url_for('main.profile'))

@main.route('/delete_task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('main.profile'))

# EDIT DELIVERABLES #

@main.route('/edit_project/<int:project_id>', methods=['POST'])
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)  # Fetch the project or return 404
    new_title = request.form['new_title']  # Get the new title from the form

    # Update the project's title
    project.title = new_title
    db.session.commit()  # Commit the changes to the database

    return redirect(url_for('main.profile'))  # Redirect back to the profile page or wherever appropriate


@main.route('/edit_task/<int:task_id>', methods=['POST'])
def edit_task(task_id):
    task = Task.query.get_or_404(task_id) 
    new_title = request.form['new_title'] 
    new_project_id = request.form['new_project_id']  
    new_start_date = datetime.strptime(request.form['new_start_date'], '%Y-%m-%d')
    new_end_date = datetime.strptime(request.form['new_end_date'], '%Y-%m-%d')

    # Update the project's title
    task.title = new_title
    task.project_id = new_project_id
    task.start_time = new_start_date
    task.end_time = new_end_date
    db.session.commit()  # Commit the changes to the database

    return redirect(url_for('main.profile'))  # Redirect back to the profile page or wherever appropriate
    