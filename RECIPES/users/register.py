# RECIPES/users/register

from flask import Blueprint, render_template, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo
from RECIPES.database.db_init import get_db_connection

register_bp = Blueprint('register', __name__, template_folder='../templates', static_folder='../static')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

@register_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        conn = get_db_connection()
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            existing = cursor.fetchone()

        if existing:
            flash('Username already exists')
            # *** ОСТАЕТСЯ НА СТРАНИЦЕ РЕГИСТРАЦИИ ***
            return render_template('register.html', form=form)
        else:
            conn = get_db_connection()
            with conn:
                conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            flash('Registration successful! Please log in.')
            # Перенаправляем на страницу логина после успешной регистрации
            return redirect(url_for('login.login'))

    return render_template('register.html', form=form)