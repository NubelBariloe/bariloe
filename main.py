from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy.model import Model
from flask_wtf import FlaskForm
from sqlalchemy import Null
from wtforms import StringField, SubmitField, SelectField, DateField, ValidationError, Form
from wtforms.fields.numeric import IntegerField
from wtforms.fields.simple import TextAreaField, PasswordField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase,Mapped, mapped_column, Session
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from smtplib import SMTP_SSL
from email.message import EmailMessage
from random import randint
from datetime import timedelta, datetime
db = SQLAlchemy()


app = Flask(__name__, template_folder='html', static_folder='static')
bootsrap = Bootstrap5(app)
app.secret_key = "ben"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///schools.db"
db.init_app(app)
app.permanent_session_lifetime = timedelta(minutes= 5)


login_manager = LoginManager()
login_manager.init_app(app)

@app.before_request
def before_request():
    session.permanent = True
    session.modified = True
    if current_user.is_authenticated:

        now = datetime.now()

        last_activity = session.get('last_activity')

        if last_activity:
            last_activity = datetime.fromisoformat(last_activity)

            if now - last_activity > timedelta(minutes=1):
                logout_user()
                session.clear()
                return redirect(url_for('logg'))

        session['last_activity'] = now.isoformat()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

passwords = "gxue dors rfbw fsdi"
my_email = "nubelbariloe133@gmail.com"


class User(UserMixin, db.Model):
    registration = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    number = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    course = db.Column(db.String(120), nullable=False)
    username = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(120), nullable=False)
    score = db.Column(db.String(120), default=Null)
    role = db.Column(db.String(20), default="student")

    def get_id(self):
        return str(self.registration)

class Enquiry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    number = db.Column(db.Integer, nullable=False)
    subject = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/pricing')
def pricing():
    return render_template('pricing.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/contact', methods=['GET','POST'])
def contact():
    class MessageForm(FlaskForm):
        name = StringField('Name', validators=[DataRequired()])
        email = StringField('Email', validators=[DataRequired(), Email()])
        number = StringField('Number', validators=[DataRequired()])
        subject = StringField('Subject', validators=[DataRequired()])
        message = TextAreaField('Message', validators=[DataRequired(), Length(min=50, max=1000)])
        submit = SubmitField('Submit')

    form = MessageForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        number = form.number.data
        subject = form.subject.data
        message = form.message.data
        flash('Message sent successfully', category='success')


        with app.app_context():
            db.create_all()
            db.session.add(Enquiry(
                    name=name,
                    email=email,
                    number=number,
                    subject=subject,
                    message=message
                ))
            db.session.commit()
        return redirect(url_for('contact'))


    return render_template('contact.html', form=form)

@app.route('/register', methods=['GET','POST'])
def register():
    class RegistrationForm(FlaskForm):
        name = StringField('Name', validators=[DataRequired()])
        email = StringField('Email', validators=[DataRequired(), Email()])
        number = StringField('Number', validators=[DataRequired()])
        course = SelectField(choices=([('Data Analysis', 'Data Analysis'),
                                   ('full-stack development', 'Full-Stack Development'),
                                   ('project management', 'Project Management'),
                                   ('robotics', 'Robotics'),
                                   ('Web development', 'Web Development'),
                                   ('cybersecurity','Cybersecurity')]),
                         validators=[DataRequired()])
        username = StringField('Username', validators=[DataRequired(), Length(min=6, max=20)])
        password = PasswordField('Password', validators=[DataRequired(),
                                                         Length(min=6, max=20),
                                                         Regexp(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*(),.?":{}|<>]).*$',
                                                            message="Password must contain at least one lowercase letter,"
                                                                    " one uppercase letter, and one symbol.")])
        confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
        submit = SubmitField('Register')

    form = RegistrationForm()
    if form.validate_on_submit():
        name = form.name.data
        number = form.number.data
        email = form.email.data
        course = form.course.data
        username = form.username.data
        password = generate_password_hash(form.password.data, method="pbkdf2:sha256", salt_length=20)
        reg_number = randint(111111,99999999)

        user = User.query.filter_by(username=username).first()
        if user:
            message = f'Username {username} already exists.'
            return render_template('register.html', form=form, message=message)
        user = User.query.filter_by(registration=reg_number).first()
        if user:
            reg_number = randint(1111110, 999999999)
        user = User.query.filter_by(email=email).first()
        if user:
            message = f'Email {email} already exists.'
            return render_template('register.html', form=form, message=message)

        body = f"""Dear {name},

        Congratulations! 🎉

        We are pleased to confirm that you have successfully registered for the {course} course at Nubels Digital Academy.

        Your registration details are:

        Course:{course}
        Registration Number:{ reg_number }

        Please keep your registration number safe, as you may need it for accessing your course information and other academic activities.

        Thank you for choosing Nubels Digital Academy. We look forward to supporting you throughout your learning journey.

        Best regards,
        Nubels Digital Academy
        Digital Skills for a Better Future
        """




        with SMTP_SSL("smtp.gmail.com", 465, timeout=30) as smtp:
            email_msg = EmailMessage()
            email_msg["Subject"] = "Registration Confirmation"
            email_msg["From"] = my_email
            email_msg["To"] = email
            email_msg.set_content(body)
            smtp.login(my_email, passwords)
            smtp.send_message(email_msg)





        with app.app_context():
            db.create_all()
            db.session.add(User(
                registration = reg_number,
                name= name,
                number=number,
                email=email,
                course=course,
                username=username,
                password=password

            ))
            db.session.commit()


        return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET','POST'])
def login():
    class LoginForm(FlaskForm):
        email = StringField('Email', validators=[DataRequired(), Email()])
        password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=20)])
        submit = SubmitField('Login')

    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        if not user:
            message = f'Username {email} does not exist.'
            return render_template('login.html', form=form, message=message)
        elif not check_password_hash(user.password, password):
            message = f'invalid password.'
            return render_template('login.html', form=form, message=message)

        elif not user or  not check_password_hash(user.password, password):
            message = f'Email and Password does not exist.'
            return render_template('login.html', form=form, message=message)
        else:
            login_user(user, remember=True)
            return redirect(url_for('home'))



    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/results')
def results():
    return render_template('results.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    users = User.query.all()
    class UserForm(FlaskForm):
        reg_num = StringField('Registration Number', validators=[DataRequired(), Length(min=6, max=20)])
        score = StringField('Score', validators=[DataRequired()])
        submit = SubmitField('Update Score')

    form = UserForm()
    if form.validate_on_submit():
        score = form.score.data
        reg_num = form.reg_num.data

        user = User.query.filter_by(registration=reg_num).first()
        if user:
            user.score = score
            db.session.commit()
            message = f'Score has been updated.'
            return render_template('admin.html', students=users, form=form, message=message)

        else:
            message = f'Registration Number {reg_num} does not exist.'
            return render_template('admin.html', form=form, message=message)



    return render_template('admin.html', students=users, form=form)

if __name__ == '__main__':
    app.run(debug=True)

