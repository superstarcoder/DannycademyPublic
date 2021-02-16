import os
import secrets

from flask import Blueprint, redirect, url_for, flash, render_template, request
from flask_login import current_user, login_required, login_user, logout_user
from flask_mail import Message

from dannycademy.forms import SignUpForm, UpdateAccountForm, LogInForm, RequestResetForm, ResetPasswordForm
from dannycademy import bcrypt, db, mail, app
from dannycademy.main.main import urlProfilePics
from dannycademy.models import User
from dannycademy import login_manager

from PIL import Image


users = Blueprint('users', __name__)


@users.route('/signUp', methods=['GET', 'POST'])
def signUp():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = SignUpForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created! You can now log in', 'success')
        return redirect(url_for('users.login'))

    print(form.errors)
    print(form.username.errors)
    print(form.email.errors)
    print(form.password.errors)
    print(form.confirm_password.errors)

    return render_template('signUp.html', title='Register', form=form)


def save_picture(form_picture, urlFor, output_size):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'templates', urlFor, picture_fn)

    # output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)

    i.save(picture_path)
    return picture_fn


@users.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data, urlProfilePics, (125, 125))
            oldImg = current_user.image_file
            current_user.image_file = picture_file
            if oldImg != "default.jpg":
                os.remove(os.path.join(app.root_path, 'templates', urlProfilePics, oldImg))

        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('users.account'))  # get request
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_path = urlProfilePics + "/" + current_user.image_file
    print("debug: ", image_path)
    return render_template('account.html', title='Account', image_path=image_path, form=form)


# @login_manager.unauthorized_handler
# def unauthorized_callback():
#     return redirect(url_for('users.login'))


@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LogInForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,
                                               form.password.data):  # if user exists and password matches
            login_user(user, remember=form.remember.data)

            # the next args are created by default because of the flask login_required
            # so next_page would be the page the user is redirected to after logging in
            next_page = request.args.get('next')
            print("debug output:", next_page)
            if next_page:
                return redirect(next_page)
            else:
                print("im going home")
                return redirect(url_for('main.index'))
        else:
            flash("Login Unsuccessful. Please check username and password", "danger")

    return render_template('login.html', title='Login', form=form)


@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='dannycademy@gmail.com', recipients=[user.email])
    #     msg.body = f'''To reset your Password visit the following link
    # {url_for('reset_token', token=token, _external=True)}
    # If you did not make this request, then simply ignore this email and no changes will be made'''
    msg.body = f'''To reset your Password visit the following link
{url_for('users.reset_token', _external=True)}?token={token}
If you did not make this request, then simply ignore this email and no changes will be made'''

    mail.send(msg)


# this is user requesting for a reset
@users.route('/reset_request', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('users.login'))
    return render_template('resetRequest.html', title='Reset Password', form=form)


#
# @users.route('/reset_password/<token>', methods=['GET', 'POST'])
# def reset_token(token):
@users.route('/reset_password', methods=['GET', 'POST'])
def reset_token():
    token = request.args.get("token")

    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_token(token)

    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash(f'Your password has been updated! You can now log in', 'success')
        return redirect(url_for('users.login'))

    return render_template('resetToken.html', title='Reset Password', form=form)
