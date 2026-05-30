from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Vehicle, MaintenanceRecord
from sqlalchemy import func

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    return render_template('main/index.html', title='AutoLog — Registro de Mantenimiento')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    vehicles = Vehicle.query.filter_by(user_id=current_user.id).order_by(Vehicle.created_at.desc()).all()
    # Stats per vehicle
    stats = {}
    for v in vehicles:
        total = db.session.query(func.sum(MaintenanceRecord.cost)).filter_by(vehicle_id=v.id).scalar() or 0
        count = MaintenanceRecord.query.filter_by(vehicle_id=v.id).count()
        last = MaintenanceRecord.query.filter_by(vehicle_id=v.id).order_by(MaintenanceRecord.date.desc()).first()
        stats[v.id] = {'total': total, 'count': count, 'last': last}
    return render_template('main/dashboard.html', vehicles=vehicles, stats=stats, title='Mi garaje')


@main_bp.route('/status')
def status():
    try:
        db.session.execute(db.text('SELECT 1'))
        db_ok = True
    except Exception:
        db_ok = False
    payload = {
        'status': 'ok' if db_ok else 'degraded',
        'app': 'AutoLog',
        'database': 'connected' if db_ok else 'error',
        'version': '1.0.0'
    }
    return jsonify(payload), 200 if db_ok else 503


def page_not_found(e):
    return render_template('errors/404.html', title='Página no encontrada'), 404
