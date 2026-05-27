# RECIPES/users/login

from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from werkzeug.security import check_password_hash, generate_password_hash
from RECIPES.database.db_init import get_db_connection
from RECIPES.database.db_settings import get_auth_code
import hashlib

login_bp = Blueprint('login', __name__, template_folder='../templates', static_folder='../static')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    auth_code = StringField('Authorization Code (if required)', validators=[])  # Обязательное поле
    submit = SubmitField('Login')

@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        auth_code = form.auth_code.data.strip() if form.auth_code.data else None

        conn = get_db_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, password_hash, is_admin FROM users WHERE username = %s", (username,))
                user = cursor.fetchone()

                if not user:
                    flash('Неверный логин или пароль', 'danger')
                    return render_template('login.html', form=form)

                # Проверить хэш пароля (BCRYPT по умолчанию)
                if not check_password_hash(user[1], password):
                    flash('Неверный логин или пароль', 'danger')
                    return render_template('login.html', form=form)
                
                user_is_admin = bool(user['is_admin'])

                # Проверка кода авторизации (только для не-админов)
                if not user['is_admin']:
                    stored_code = get_auth_code()
                    if stored_code and (not auth_code or auth_code != stored_code):
                        flash('Неверный код доступа', 'danger')
                        return render_template('login.html', form=form)

                # ✅ Успешный вход
                session['user_id'] = user[0]
                session['username'] = username
                session['is_admin'] = user_is_admin
                flash('Вход выполнен успешно!', 'success')
                return redirect(url_for('index'))

        except Exception as e:
            flash('Ошибка сервера. Попробуйте позже.', 'danger')
            return render_template('login.html', form=form)

    return render_template('login.html', form=form)

@login_bp.route('/logout')
def logout():
    session.clear()
    flash('Вы вышли из аккаунта', 'info')
    return redirect(url_for('index'))
