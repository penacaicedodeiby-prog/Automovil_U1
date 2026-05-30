from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app import db, limiter
from app.models import User
from app.auth.forms import SignupForm, SigninForm

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/signup', methods=['GET', 'POST'])
@limiter.limit("10 per hour")
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = SignupForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data.lower()
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('¡Cuenta creada exitosamente! Ahora puedes ingresar.', 'success')
        return redirect(url_for('auth.signin'))
    return render_template('auth/signup.html', form=form, title='Crear cuenta')


@auth_bp.route('/signin', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def signin():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = SigninForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            flash(f'¡Bienvenido de nuevo, {user.username}!', 'success')
            return redirect(next_page or url_for('main.dashboard'))
        flash('Correo o contraseña incorrectos. Intenta de nuevo.', 'danger')
    return render_template('auth/signin.html', form=form, title='Iniciar sesión')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada correctamente.', 'info')
    return redirect(url_for('main.index'))
