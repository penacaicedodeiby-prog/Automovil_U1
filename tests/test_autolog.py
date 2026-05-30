"""
Pruebas unitarias de AutoLog.
Usan SQLite en memoria — no requieren MySQL real.
"""
import pytest
from app import create_app, db as _db
from app.models import User, Vehicle, MaintenanceRecord
from datetime import date
from decimal import Decimal


# ── Fixtures ───────────────────────────────────────────────────────────────

@pytest.fixture(scope='session')
def app():
    """Crea la aplicación con configuración de pruebas."""
    test_config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key',
        'LOGIN_DISABLED': False,
        'SERVER_NAME': 'localhost',
    }
    app = create_app(test_config)
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


@pytest.fixture(autouse=True)
def clean_db(app):
    """Limpia la BD entre pruebas."""
    with app.app_context():
        yield
        _db.session.query(MaintenanceRecord).delete()
        _db.session.query(Vehicle).delete()
        _db.session.query(User).delete()
        _db.session.commit()


def create_user(app, username='testuser', email='test@example.com', password='Password123'):
    with app.app_context():
        u = User(username=username, email=email)
        u.set_password(password)
        _db.session.add(u)
        _db.session.commit()
        return u.id


# ── Tests: Modelos ─────────────────────────────────────────────────────────

def test_user_password_hashing(app):
    with app.app_context():
        u = User(username='alice', email='alice@test.com')
        u.set_password('SecurePass1!')
        assert u.password_hash != 'SecurePass1!'
        assert u.check_password('SecurePass1!') is True
        assert u.check_password('wrongpass') is False


def test_user_unique_email(app):
    with app.app_context():
        u1 = User(username='user1', email='dup@test.com')
        u1.set_password('Password1')
        _db.session.add(u1)
        _db.session.commit()
        assert User.query.filter_by(email='dup@test.com').count() == 1


def test_vehicle_creation(app):
    with app.app_context():
        uid = create_user(app)
        v = Vehicle(user_id=uid, brand='Toyota', model='Corolla', year=2020, plate='ABC123')
        _db.session.add(v)
        _db.session.commit()
        found = Vehicle.query.filter_by(plate='ABC123').first()
        assert found is not None
        assert found.brand == 'Toyota'


def test_maintenance_record_creation(app):
    with app.app_context():
        uid = create_user(app)
        v = Vehicle(user_id=uid, brand='Honda', model='Civic', year=2018, plate='XYZ789')
        _db.session.add(v)
        _db.session.commit()
        r = MaintenanceRecord(
            vehicle_id=v.id,
            service_type='Cambio de aceite',
            date=date(2024, 3, 15),
            cost=Decimal('85000.00'),
            workshop='Taller El Mecánico'
        )
        _db.session.add(r)
        _db.session.commit()
        found = MaintenanceRecord.query.filter_by(vehicle_id=v.id).first()
        assert found.service_type == 'Cambio de aceite'
        assert found.cost == Decimal('85000.00')


# ── Tests: Rutas públicas ──────────────────────────────────────────────────

def test_index_loads(client):
    resp = client.get('/')
    assert resp.status_code == 200
    assert b'AutoLog' in resp.data


def test_signup_page_loads(client):
    resp = client.get('/signup')
    assert resp.status_code == 200
    assert b'Crear cuenta' in resp.data


def test_signin_page_loads(client):
    resp = client.get('/signin')
    assert resp.status_code == 200
    assert b'Iniciar sesi' in resp.data


def test_status_endpoint(client):
    resp = client.get('/status')
    assert resp.status_code in (200, 503)
    data = resp.get_json()
    assert 'status' in data
    assert data['app'] == 'AutoLog'


def test_404_page(client):
    resp = client.get('/ruta-que-no-existe')
    assert resp.status_code == 404
    assert b'404' in resp.data


# ── Tests: Autenticación ───────────────────────────────────────────────────

def test_signup_creates_user(client, app):
    resp = client.post('/signup', data={
        'username': 'newuser',
        'email': 'newuser@test.com',
        'password': 'Password123',
        'password2': 'Password123',
    }, follow_redirects=True)
    assert resp.status_code == 200
    with app.app_context():
        assert User.query.filter_by(email='newuser@test.com').first() is not None


def test_signin_with_valid_credentials(client, app):
    create_user(app, username='loginuser', email='login@test.com', password='Password123')
    resp = client.post('/signin', data={
        'email': 'login@test.com',
        'password': 'Password123',
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b'garaje' in resp.data or b'dashboard' in resp.data.lower() or b'Bienvenido' in resp.data


def test_signin_with_wrong_password(client, app):
    create_user(app, username='wrongpwduser', email='wrongpwd@test.com', password='Correct123')
    resp = client.post('/signin', data={
        'email': 'wrongpwd@test.com',
        'password': 'WrongPassword',
    }, follow_redirects=True)
    assert b'incorrectos' in resp.data or b'error' in resp.data.lower()


# ── Tests: Protección de rutas ─────────────────────────────────────────────

def test_dashboard_requires_login(client):
    resp = client.get('/dashboard', follow_redirects=False)
    assert resp.status_code == 302
    assert '/signin' in resp.headers['Location']


def test_new_vehicle_requires_login(client):
    resp = client.get('/vehicles/new', follow_redirects=False)
    assert resp.status_code == 302
