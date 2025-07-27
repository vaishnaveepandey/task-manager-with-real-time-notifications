from flask import Blueprint, render_template, url_for, flash, redirect, request
from app.forms import RegistrationForm, LoginForm, TaskForm
from app.models import User, Task
from app import db, mail
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from werkzeug.security import generate_password_hash, check_password_hash

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Login Unsuccessful. Check email and password', 'danger')
    return render_template('login.html', form=form)

@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        user = User(username=form.username.data, email=form.email.data, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created!', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

@main.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = TaskForm()
    if form.validate_on_submit():
        task = Task(title=form.title.data, due_date=form.due_date.data, author=current_user)
        db.session.add(task)
        db.session.commit()

        msg = Message('New Task Created',
                      sender='noreply@example.com',
                      recipients=[current_user.email])
        msg.body = f"Task '{task.title}' is scheduled for {task.due_date}."
        mail.send(msg)

        flash('Task created and email sent!', 'success')
        return redirect(url_for('main.dashboard'))
    tasks = Task.query.filter_by(author=current_user)
    return render_template('dashboard.html', form=form, tasks=tasks)

@main.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.login'))
