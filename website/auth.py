from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, mail, app
from flask_login import login_user, login_required, logout_user, current_user
from flask_mail import Message
from flask_bcrypt import Bcrypt

auth = Blueprint('auth', __name__)

@auth.route('/')
def landing():
    return render_template("LandingPg.html", user=current_user)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/search')
def Search():
    return render_template("search.html", user=current_user)


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        mobileNum = request.form.get('mobileNumber')
        address = request.form.get('address')
        Fname = request.form.get('firstName')
        Lname = request.form.get('lastName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(Fname) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        elif len(mobileNum) != 13:
            flash('Mobile number must be at least 13 characters (including +91).', category='error')
        elif len(address) < 3:
            flash('Complete address must filled.', category='error')
        else:
            new_user = User(email=email, first_name=Fname, last_name=Lname, mobile_number=mobileNum, address=address, password=generate_password_hash(
                password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)

def send_mail(user):
    token=user.get_token()
    msg=Message('Password Reset Request', recipients=[user.email], sender='noreply@website.com')
    msg.body=f''' To reset your password please follow the link below.

    {url_for('auth.reset_token', token=token, _external=True)}

    If you didnt send a password request then please ignore this message.

    '''
    mail.send(msg)

@auth.route('/Reset_request', methods=['GET', 'POST'])
def Reset_request():
    if request.method == 'POST':
        email2 = request.form.get('email')
        user = User.query.filter_by(email=email2).first()
        if user:
            send_mail(user)
            flash('Reset request has been sent. Check your mail')
        else:
            flash('Email not found.', category='error')
    return render_template("Reset_request.html", user=current_user)

@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    user=User.verify_token(token)
    if user is None:
        flash('Token is invalid or has expired. Please try again', category='error')
        return redirect(url_for('auth.Reset_request'))
    if request.method == 'POST':
        p1 = request.form.get('password')
        p2 = request.form.get('confirm_password')
        if (p1 == p2) and (len(p1)>6):
            valid = True
        else:
            valid = False
        if valid == True:
            hashed_password=generate_password_hash(p1, method='sha256')
            user.password = hashed_password
            db.session.commit()
            flash('Password has been change', 'success')
            return redirect(url_for('auth.login'))

    return render_template("change_password.html", user=current_user)


