from flask import Flask, request, redirect, render_template_string
from flask_sqlalchemy import SQLAlchemy
# from models import User, Project, Task



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///planner.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    projects = db.relationship('Project', backref='user', lazy=True)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tasks = db.relationship('Task', backref='project', lazy=True)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)



# Model definitions (User, Project, Task) go here

with app.app_context():
    db.create_all()

# @app.before_first_request
# def create_tables():
#     db.create_all()

@app.route('/user/create', methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        username = request.form.get('username')
        if username:
            new_user = User(username=username)
            db.session.add(new_user)
            db.session.commit()
            return redirect('/users')
    return render_template_string('''
        <form method="post">
            Username: <input type="text" name="username"><br>
            <input type="submit" value="Create User">
        </form>
    ''')

@app.route('/users')
def list_users():
    users = User.query.all()
    users_list = '<br>'.join([user.username for user in users])
    return render_template_string(f'Users:<br>{users_list}')

if __name__ == '__main__':
    app.run(debug=True)
