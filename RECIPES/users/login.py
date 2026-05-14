# RECIPES/users/login

from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from .work_db_users import get_db_connection, get_auth_code

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
        auth_code = request.form.get('auth_code', '').strip() or None  # Может быть пустым

        conn = get_db_connection()
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, password, is_admin FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()

            if not user:
                flash('Неверный логин или пароль')
                return render_template('login.html', form=form)

            # Проверка пароля
            if user[1] != password:
                flash('Неверный логин или пароль')
                return render_template('login.html', form=form)

            # Проверка кода авторизации — только для не-админов
            if not user['is_admin']:  # Обычный пользователь
                stored_code = get_auth_code()
                if stored_code is None:
                    flash('Код авторизации не задан администратором. Войти невозможно.')
                    return render_template('login.html', form=form)
                if auth_code != stored_code:
                    flash('Неверное кодовое слово.')
                    return render_template('login.html', form=form)

            # ✅ Всё прошло успешно
            flash('Вход выполнен успешно!')
            session['user_id'] = user[0]
            session['username'] = username
            session['is_admin'] = bool(user['is_admin'])  # ✅ сохраняем флаг админа
            return redirect(url_for('index'))

    return render_template('login.html', form=form)


@login_bp.route('/logout')
def logout():
    session.clear()
    flash('Вы вышли из аккаунта')
    return redirect(url_for('index'))
