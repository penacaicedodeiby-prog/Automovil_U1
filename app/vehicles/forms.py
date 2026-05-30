from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, TextAreaField, DateField, SelectField, DecimalField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


SERVICE_TYPES = [
    ('', 'Selecciona un tipo...'),
    ('Cambio de aceite', 'Cambio de aceite'),
    ('Cambio de filtro de aire', 'Cambio de filtro de aire'),
    ('Cambio de filtro de combustible', 'Cambio de filtro de combustible'),
    ('Cambio de llantas', 'Cambio de llantas'),
    ('Frenos', 'Revisión / cambio de frenos'),
    ('Batería', 'Cambio de batería'),
    ('Revisión general', 'Revisión general'),
    ('Mantenimiento preventivo', 'Mantenimiento preventivo'),
    ('Reparación mecánica', 'Reparación mecánica'),
    ('Aire acondicionado', 'Aire acondicionado'),
    ('Alineación y balanceo', 'Alineación y balanceo'),
    ('Revisión eléctrica', 'Revisión eléctrica'),
    ('Lavado y detallado', 'Lavado y detallado'),
    ('Otro', 'Otro'),
]


class VehicleForm(FlaskForm):
    brand = StringField('Marca', validators=[
        DataRequired(message='La marca es obligatoria.'),
        Length(max=64)
    ])
    model = StringField('Modelo', validators=[
        DataRequired(message='El modelo es obligatorio.'),
        Length(max=64)
    ])
    year = IntegerField('Año', validators=[
        DataRequired(message='El año es obligatorio.'),
        NumberRange(min=1900, max=2100, message='Ingresa un año válido.')
    ])
    plate = StringField('Placa', validators=[
        DataRequired(message='La placa es obligatoria.'),
        Length(max=20)
    ])
    submit = SubmitField('Guardar vehículo')


class MaintenanceRecordForm(FlaskForm):
    service_type = SelectField('Tipo de servicio', choices=SERVICE_TYPES, validators=[
        DataRequired(message='Selecciona un tipo de servicio.')
    ])
    description = TextAreaField('Descripción', validators=[Optional(), Length(max=500)])
    date = DateField('Fecha', validators=[DataRequired(message='La fecha es obligatoria.')])
    mileage = IntegerField('Kilometraje', validators=[
        Optional(),
        NumberRange(min=0, message='El kilometraje no puede ser negativo.')
    ])
    cost = DecimalField('Costo (COP)', places=2, validators=[
        DataRequired(message='El costo es obligatorio.'),
        NumberRange(min=0, message='El costo no puede ser negativo.')
    ])
    workshop = StringField('Taller / lugar', validators=[Optional(), Length(max=100)])
    submit = SubmitField('Guardar registro')
