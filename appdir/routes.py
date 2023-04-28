from flask import render_template, flash, redirect, url_for, session, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from appdir import app, db
from appdir.forms import RegisterForm, LoginForm, QuestionForm, AnswerForm
from appdir.models import User, Question, Answer, Viewpoint, Comment, Follow, Invite
from datetime import datetime


@app.route('/', methods=['GET', 'POST'])
def root():
    # question_form = QuestionForm()
    # if question_form.validate_on_submit():
    #     return validate_question(question_form)
    # return render_template('index.html', question_form=question_form, username=session.get('USERNAME'))
    return redirect('/questions/new')


def validate_question(question_form,answer=None):
    now_time = datetime.now()
    print(question_form.choice1.data)
    data_list = [question_form.choice1.data,question_form.choice2.data,question_form.choice3.data,
                 question_form.choice4.data,answer]
    description = '，，'.join(data_list)
    print(description)
    new_question = Question(title=question_form.title.data, description=description,
                            user_id=session.get('USERID'), datetime=now_time)
    db.session.add(new_question)
    db.session.commit()
    flash('You have posted your question successfully!', 'success')
    return redirect(url_for('questions', type='new'))


@app.route('/index', methods=['GET', 'POST'])
def index():
    question_form = QuestionForm()
    session.clear()
    flash('You have logged out!', 'success')
    if question_form.validate_on_submit():
        return validate_question(question_form)
    return render_template('index.html', username=session.get('USERNAME'), question_form=question_form)



@app.route('/questions/<type>', methods=['GET', 'POST'])
def questions(type):
    question_form = QuestionForm()
    invites_in_db = Invite.query.filter(Invite.invitee_id == session.get('USERID'))
    invite_question_ids = []
    for invite in invites_in_db:
        invite_question_ids.append(invite.question_id)
    questions_in_db = Question.query.all()
    my_questions = []
    for question in questions_in_db:
        user = User.query.filter(User.id == question.user_id).first()
        answers_in_db = Answer.query.filter(Answer.question_id == question.id)
        new_question = {
            'id': question.id,
            'username': user.username,
            'title': question.title,
            'description': question.description,
            'answers': answers_in_db.count(),
            'time': question.datetime.strftime("%Y-%m-%d %H:%M:%S")
        }
        if type == 'invitation':
            if question.id in invite_question_ids:
                my_questions.append(new_question)
        else:
            my_questions.append(new_question)
    if question_form.validate_on_submit():
        return validate_question(question_form,request.form['answer'])
    if request.method=="POST":
        print('post')
    if type == 'hot':
        my_questions = sorted(my_questions, key=lambda keys: keys['answers'])
        my_questions.reverse()
        return render_template('hot.html', username=session.get('USERNAME'), question_form=question_form,
                               questions=my_questions)
    if type == 'new':
        my_questions = sorted(my_questions, key=lambda keys: keys['time'])
        my_questions.reverse()
        return render_template('new.html', username=session.get('USERNAME'), question_form=question_form,
                               questions=my_questions)




@app.route('/register', methods=['GET', 'POST'])
def register():
    question_form = QuestionForm()
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        return validate_register(register_form)
    return render_template('register.html', form=register_form)


def validate_register(form):
    if form.password.data != form.repassword.data:
        flash('Passwords do not match!', 'error')
        return redirect(url_for('register'))
    if User.query.filter(User.username == form.username.data).first():
        flash('The username has been used!', 'error')
        return redirect(url_for('register'))
    if User.query.filter(User.email == form.email.data).first():
        flash('The email has been used by other users!', 'error')
        return redirect(url_for('register'))
    password_hash = generate_password_hash(form.password.data)
    user = User(username=form.username.data, email=form.email.data, password_hash=password_hash)
    db.session.add(user)
    db.session.commit()
    flash('User registered with username: {}'.format(form.username.data), 'success')
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    question_form = QuestionForm()
    login_form = LoginForm()
    if login_form.validate_on_submit():
        return validate_login(login_form)
    return render_template('login.html', form=login_form)


def validate_login(form):
    user_in_db = User.query.filter(User.username == form.username.data).first()
    if not user_in_db:
        flash('No user found with username: {}'.format(form.username.data), 'error')
        return redirect(url_for('login'))
    if check_password_hash(user_in_db.password_hash, form.password.data):
        flash('Login successfully!', 'success')
        session["USERNAME"] = user_in_db.username
        session["USERID"] = user_in_db.id
        return redirect(url_for('root'))
    flash('Incorrect Password', 'error')
    return redirect(url_for('login'))
