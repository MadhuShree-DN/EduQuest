from flask import Flask, render_template,request,flash,redirect,url_for,session,flash,jsonify
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import urlparse
from datetime import datetime,timedelta,timezone
import bcrypt
import smtplib
from email.mime.text import MIMEText
import random
import string
from flask_mail import Mail, Message

app = Flask(__name__, static_url_path='/static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
app.secret_key = 'secret_key'

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] =  465 
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'madhushreedn9376@gmail.com'
app.config['MAIL_PASSWORD'] = 'vlmh nbie qaky vbso'
app.config['MAIL_DEFAULT_SENDER'] = 'madhushreedn9376@gmail.com'
mail = Mail(app)



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

    def __init__(self, email, password, name):
        self.name = name
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    duration = db.Column(db.Integer, nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/base_student')
def base_student():
    return render_template('base_student.html')
    #return redirect(url_for('base_student.html'))

@app.route('/base_teacher')
def base_teacher():
    return render_template('base_teacher.html')
@app.route('/logout')
def logout():
    session.clear()
    return render_template('index.html')
@app.route('/index')
def home():
    
    return render_template('index.html')
@app.route('/course')
def course():
    return render_template('course.html')
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/base_student')
    return render_template('register.html')

def send_otp_email(email, otp):
    msg = Message('OTP Verification', sender='madhushreedn9376@gmail.com', recipients=[email])
    msg.body = f'Enter OTP for student login is : {otp}'
    mail.send(msg)


@app.route('/register_teacher',methods=['GET','POST'])
def register_teacher():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        new_user = User(name=name,email=email,password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/base_teacher')
    return render_template('register_teacher.html')

@app.route('/add_course', methods=['POST'])
def add_course():
    if request.method == 'POST':
        name = request.form['name']
        price = int(request.form['price'])
        duration = int(request.form['duration'])
        new_course = Course(name=name, price=price, duration=duration)
        db.session.add(new_course)
        db.session.commit()
        return redirect('/course')

@app.route('/delete_course/<int:id>', methods=['POST'])
def delete_course(id):
    course = Course.query.get_or_404(id)
    db.session.delete(course)
    db.session.commit()
    return redirect('/teacher_dashboard')




@app.route('/base_student', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['email'] = user.email
            otp = ''.join(random.choices(string.digits, k=6))
            print(otp)
            send_otp_email(email, otp)
            session['std_otp'] = otp
            session['std_email'] = email
            if user.email == 'teacher@example.com':
                return redirect('/Tverify_otp')
            else:
                
                return redirect('/verify_otp')
        else:
            return render_template('base_student.html', error='Invalid user')
    return render_template('base_student.html')

        
@app.route('/verify_otp',methods=['GET','POST'])
def verify_otp():
    if request.method == 'POST':
        user_otp = request.form['otp']
        stored_otp = session.get('std_otp')
        email = session.get('std_email')

        if user_otp == stored_otp:
            
            return redirect(url_for('dashboard'))
        else:
            return "Invalid OTP. Please try again."

    return render_template('verify_otp.html')

@app.route('/Tverify_otp',methods=['GET','POST'])
def Tverify_otp():
    if request.method == 'POST':
        user_otp = request.form['otp']
        stored_otp = session.get('std_otp')
        email = session.get('std_email')

        if user_otp == stored_otp:
            
            return redirect(url_for('teacher_dashboard'))
        else:
            return "Invalid OTP. Please try again."

    return render_template('Tverify_otp.html')


@app.route('/base_teacher',methods=['GET','POST'])
def login_teacher():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['email'] = user.email
            otp = ''.join(random.choices(string.digits, k=6))
            print(otp)
            send_otp_email(email, otp)
            session['std_otp'] = otp
            session['std_email'] = email
            return redirect('/Tverify_otp')
        else:
            return render_template('base_teacher.html',error='Invalid user')
    return render_template('base_teacher.html')

@app.route('/dashboard')
def dashboard():
    if 'email' in session:
        user = User.query.filter_by(email=session['email']).first()
        courses = Course.query.all()
        return render_template('dashboard.html', user=user, courses=courses)
    return redirect('/base_student')

@app.route('/teacher_dashboard')
def teacher_dashboard():
    if 'email' in session:
        user = User.query.filter_by(email=session['email']).first()
        courses = Course.query.all()  
        return render_template('teacher_dashboard.html', user=user, courses=courses)
    return redirect('/base_teacher')




if __name__ == '__main__':
    app.run(debug=True)
