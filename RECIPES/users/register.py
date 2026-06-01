# RECIPES/users/register

from flask import Blueprint, render_template, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo
from werkzeug.security import generate_password_hash
from RECIPES.database.db_init import get_db_connection

register_bp = Blueprint('register', __name__, template_folder='../templates', static_folder='../static')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

@register_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        conn = get_db_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
                if cursor.fetchone():
                    flash('Имя пользователя уже занято', 'danger')
                    return render_template('register.html', form=form)

                # Хэширование пароля (BCRYPT)
                password_hash = generate_password_hash(password)

                cursor.execute("""
                    INSERT INTO users (username, password_hash, created_at)
                    VALUES (%s, %s, NOW())
                """, (username, password_hash))

                flash('Регистрация успешна! Перейдите на страницу входа.', 'success')
                return redirect(url_for('login.login'))

        except Exception:
            flash('Ошибка регистрации. Попробуйте позже.', 'danger')
            return render_template('register.html', form=form)

    return render_template('register.html', form=form)
