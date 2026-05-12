# RECIPES/users/login

from flask import Blueprint, render_template, redirect, url_for, flash, session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from .work_db_users import get_db_connection

login_bp = Blueprint('login', __name__, template_folder='../templates', static_folder='../static')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        conn = get_db_connection()
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, password, is_admin FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()
            if user and user[1] == password:
                flash('Logged in successfully!')
                session['user_id'] = user[0]  # ← Сохраняем ID в сессии
                session['username'] = username  # Опционально для отображения
                session['is_admin'] = bool(user['is_admin'])  # ✅ new
                return redirect(url_for('index'))  # Перенаправляем на главную
            else:
                flash('Invalid username or password')
    return render_template('login.html', form=form)

@login_bp.route('/logout')
def logout():
    session.clear()
    flash('Вы вышли из аккаунта')
    return redirect(url_for('index'))
