from flask import Flask, Blueprint, render_template, request, current_app, redirect, url_for, jsonify
from flask_login import login_required, current_user
import datetime
import calendar
from . import db
from .models import Project, Task
from sqlalchemy import func


main = Blueprint('main', __name__)

@main.route('/')
@login_required
def index():
    projects = Project.query.filter_by(user_id=current_user.id)
    task_info = {
        project.id: {
            'tasks': list(Task.query.filter_by(project_id=project.id)),
            'task_types': set([
                task.task_type for task in \
                list(Task.query.filter_by(project_id=project.id))
            ])
        } \
        for project in projects
    }

    task_date_range = db.session.query(
        func.min(Task.start_time).label('earliest_start_date'),
        func.max(Task.end_time).label('latest_end_date')
    ).filter(Task.project_id.in_(task_info.keys())).one()

    earliest, latest = task_date_range.earliest_start_date, task_date_range.latest_end_date
    delta = latest-earliest

    # Generate the list of datetimes
    timeframe = []
    calendar = {}
    current = earliest
    while current <= latest:
        year = current.year
        month = current.month
        day = current.day
        
        if year not in calendar:
            calendar[year] = {}
        if month not in calendar[year]:
            calendar[year][month] = []
        
        calendar[year][month].append(day)

        timeframe.append(current)
        current += datetime.timedelta(days=1)

    year_days_count = {}

    # Iterate through the nested dictionary and count the days
    for year, months in calendar.items():
        total_days = sum(len(days) for days in months.values())
        year_days_count[year] = total_days

    project_dict = generate_project_dict(projects, earliest, latest)

    return render_template(
        'index.html', 
        name=current_user.username,
        projects=projects,
        task_info=task_info,
        num_days=delta.days,
        earliest=earliest.strftime('%Y-%m-%d'),
        latest=latest.strftime('%Y-%m-%d'),
        timeframe=timeframe,
        calendar=calendar,
        year_days_count=year_days_count,
        project_dict=project_dict
    )

def generate_project_dict(projects, start_date, end_date):

    # Initialize the output dictionary
    project_dict = {}

    # Process each project
    for project in projects:
        # Fetch tasks for the project
        tasks = Task.query.filter_by(project_id=project.id).all()

        # Organize tasks by task type
        task_type_dict = {}
        for task in tasks:
            if task.task_type not in task_type_dict:
                task_type_dict[task.task_type] = []

            # Calculate the number of days for the task
            day_count = (task.end_time - task.start_time).days
            task_details = {
                'day_count': day_count + 1,
                'title': task.title,
                'start_date': task.start_time,
                'end_date': task.end_time
            }
            task_type_dict[task.task_type].append(task_details)

        for task_type in task_type_dict:
            task_list = task_type_dict[task_type]
            sorted_list = sorted(task_list, key=lambda x: x['start_date'])
            task_type_dict[task_type] = list(sorted_list)

        # Add the task types and their tasks to the project dictionary
        project_dict[project.title] = task_type_dict

    # Add a task with no title to pad each task with the number of days between each
    for project in project_dict:
        for task_type in project_dict[project]:
            # Pad before the last task and after the last task if necessary
            first_task = project_dict[project][task_type][0]
            last_task = project_dict[project][task_type][-1]

            start_pad = generate_padder_task(start_date, first_task['start_date'])
            end_pad = generate_padder_task(last_task['end_date'], end_date)

            # Pad in between each of the tasks
            task_count = len(project_dict[project][task_type])
            ref_tasks = project_dict[project][task_type][:]
            for i in range(task_count - 2):
                task_a = ref_tasks[i]
                task_b = ref_tasks[i+1]
                pad = generate_padder_task(task_a['end_date'], task_b['start_date'])
                if pad != False:
                    project_dict[project][task_type].insert(i+i+1, pad)
                # tmp = project_dict[project][task_type][:]
                # project_dict[project][task_type] = tmp[:i+1] + i + tmp[i+1:-1]
            
            if start_pad != False: project_dict[project][task_type].insert(0, start_pad)
            if end_pad != False: project_dict[project][task_type].append(end_pad)

    return project_dict

def generate_padder_task(start, end):
    delta = (end-start).days - 1
    if delta < 1:
        return False
    return {
        'day_count': (end-start).days - 1,
        'title': '',
        'start_date': start,
        'end_date': end
    }














# CREATE TASKS AND PROJECTS #

@main.route('/profile')
@login_required
def profile():
    # Load projects for the dropdown
    projects = Project.query.filter_by(user_id=current_user.id)
    tasks = {
        project.id: list(Task.query.filter_by(project_id=project.id)) \
        for project in projects
    }

    return render_template(
        'profile.html', 
        projects=projects, 
        tasks=tasks,
        name=current_user.username
    )

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

    start_date = datetime.datetime.strptime(request.form['start_date'], '%Y-%m-%d')
    end_date = datetime.datetime.strptime(request.form['end_date'], '%Y-%m-%d')

    task_type = request.form.get('task_type');

    new_task = Task(
        title=title, 
        project_id=project_id, 
        start_time=start_date, 
        end_time=end_date,
        task_type = task_type
    )
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for('main.profile'))  # Redirect back to the profile page

# DELETE TASKS AND PROJECTS #

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

# EDIT TASKS AND PROJECTS #

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

    return redirect(url_for('main.profile'))  # Redirect back to the profile page or wherever appropriate

# @main.route('/task_completion/<int:task_id>', methods=['POST'])
# def task_completion(task_id):
#     task = Task.query.get_or_404(task_id) 
#     new_completion = request.form['task_completed']

#     task.completed = new_completion
#     dv.session.commit()

#     return redirect(url_for('main.profile'))


@main.route('/task_completion/<int:task_id>', methods=['POST'])
def task_completion(task_id):
    task = Task.query.get_or_404(task_id)
    
    data = request.get_json()
    task_completed = data.get('task_completed', False)

    task.completed = task_completed
    db.session.commit()

    return jsonify({'status': 'success', 'task_completed': task_completed})
    