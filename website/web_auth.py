import json

from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify
from .web_models import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy import func
from . import app_name, db
import imghdr
import base64



# -----------------------------Blueprint-----------------------------

auth = Blueprint('web_auth', __name__)

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        user_name = request.form.get('user_name')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        user = User.query.filter_by(user_name=user_name).first()
        if user:
            flash("This user already exists. Log in or use a different user_name", category='error')
        elif password != confirm_password:
            flash("Passwords aren't matching", category='error')
        elif len(password) < 5:
            flash("Password is too short use at least 5 letters", category='error')
        else:
            new_user = User(user_name=user_name, is_seller=False, password=generate_password_hash(password, method='sha256'))

            db.session.add(new_user)
            db.session.commit()

            flash("Whoa! Your account is successfully created.", category='success')
            login_user(new_user, remember=True)
            return redirect(url_for('web_views.home', app_name=app_name))

    return render_template('sign-up.html')


@auth.route('/user/login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        user_name = request.form.get('user_name')
        password = request.form.get('password')
        user = User.query.filter_by(user_name=user_name, is_seller=False).first()
        if user and check_password_hash(user.password, password):
            flash('Logged in', category='success')
            login_user(user, remember=True)
            return redirect(url_for('web_views.home', app_name=app_name))
        else:
            flash("Incorrect username or password", category='error')
    return render_template('user_login.html', app_name=app_name)


@auth.route('/seller/login', methods=['GET', 'POST'])
def seller_login():
    if request.method == 'POST':
        user_name = request.form.get('user_name')
        password = request.form.get('password')
        user =User.query.filter_by(user_name=user_name, is_seller=True).first()
        if user and check_password_hash(user.password, password):
            flash('Logged in', category='success')
            login_user(user, remember=True)
            return redirect(url_for('web_views.sell', app_name=app_name))
        else:
            flash("Incorrect username or password", category='error')
    return render_template('seller_login.html', app_name=app_name)


@auth.route('/seller/become-a-seller', methods=['GET', 'POST'])
def seller_sign_up():
    if request.method == 'POST':
        user_name = request.form.get('user_name')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        seller = User.query.filter_by(user_name=user_name).first()
        if seller:
            flash("This user already exists. Log in or use a different user_name", category='error')
        elif password != confirm_password:
            flash("Passwords aren't matching", category='error')
        elif len(password) < 5:
            flash("Password is too short use at least 5 letters", category='error')
        else:
            new_seller = User(user_name=user_name, is_seller=True, password=generate_password_hash(password, method='sha256'))

            db.session.add(new_seller)
            db.session.commit()

            flash("Whoa! Now you can start selling", category='success')
            login_user(new_seller, remember=True)
            return redirect(url_for('web_views.sell', app_name=app_name))
            

    return render_template('become_seller.html', app_name=app_name)


@auth.route('/log-out')
@login_required
def log_out():
    logout_user()
    return redirect(url_for('web_views.home', app_name=app_name))