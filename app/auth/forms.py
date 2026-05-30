from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Regexp
from app.models import User


class SignupForm(FlaskForm):
    username = StringField('Nombre de usuario', validators=[
        DataRequired(message='El nombre de usuario es obligatorio.'),
        Length(min=3, max=64, message='Debe tener entre 3 y 64 caracteres.'),
        Regexp(r'^[A-Za-z0-9_]+$', message='Solo letras, números y guión bajo.')
    ])
    email = EmailField('Correo electrónico', validators=[
        DataRequired(message='El correo es obligatorio.'),
        Email(message='Ingresa un correo válido.')
    ])
    password = PasswordField('Contraseña', validators=[
        DataRequired(message='La contraseña es obligatoria.'),
        Length(min=8, message='Mínimo 8 caracteres.')
    ])
    password2 = PasswordField('Confirmar contraseña', validators=[
        DataRequired(message='Debes confirmar la contraseña.'),
        EqualTo('password', message='Las contraseñas no coinciden.')
    ])
    submit = SubmitField('Crear cuenta')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Ese nombre de usuario ya está en uso.')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('Ese correo ya está registrado.')


class SigninForm(FlaskForm):
    email = EmailField('Correo electrónico', validators=[
        DataRequired(message='El correo es obligatorio.'),
        Email(message='Ingresa un correo válido.')
    ])
    password = PasswordField('Contraseña', validators=[
        DataRequired(message='La contraseña es obligatoria.')
    ])
    submit = SubmitField('Ingresar')
