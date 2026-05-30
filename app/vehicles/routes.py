from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user
from app import db
from app.models import Vehicle, MaintenanceRecord
from app.vehicles.forms import VehicleForm, MaintenanceRecordForm
from sqlalchemy import func

vehicles_bp = Blueprint('vehicles', __name__)


# ── VEHICLES ─────────────────────────────────────────────────────────────────

@vehicles_bp.route('/vehicles/new', methods=['GET', 'POST'])
@login_required
def new_vehicle():
    form = VehicleForm()
    if form.validate_on_submit():
        v = Vehicle(
            user_id=current_user.id,
            brand=form.brand.data,
            model=form.model.data,
            year=form.year.data,
            plate=form.plate.data.upper()
        )
        db.session.add(v)
        db.session.commit()
        flash(f'Vehículo {v.brand} {v.model} registrado correctamente.', 'success')
        return redirect(url_for('main.dashboard'))
    return render_template('vehicles/vehicle_form.html', form=form, title='Nuevo vehículo', action='new')


@vehicles_bp.route('/vehicles/<int:vid>/edit', methods=['GET', 'POST'])
@login_required
def edit_vehicle(vid):
    v = Vehicle.query.get_or_404(vid)
    if v.user_id != current_user.id:
        abort(403)
    form = VehicleForm(obj=v)
    if form.validate_on_submit():
        v.brand = form.brand.data
        v.model = form.model.data
        v.year = form.year.data
        v.plate = form.plate.data.upper()
        db.session.commit()
        flash('Vehículo actualizado correctamente.', 'success')
        return redirect(url_for('main.dashboard'))
    return render_template('vehicles/vehicle_form.html', form=form, title='Editar vehículo', action='edit', vehicle=v)


@vehicles_bp.route('/vehicles/<int:vid>/delete', methods=['POST'])
@login_required
def delete_vehicle(vid):
    v = Vehicle.query.get_or_404(vid)
    if v.user_id != current_user.id:
        abort(403)
    db.session.delete(v)
    db.session.commit()
    flash('Vehículo eliminado.', 'info')
    return redirect(url_for('main.dashboard'))


# ── MAINTENANCE RECORDS ───────────────────────────────────────────────────────

@vehicles_bp.route('/vehicles/<int:vid>/records', methods=['GET'])
@login_required
def vehicle_records(vid):
    v = Vehicle.query.get_or_404(vid)
    if v.user_id != current_user.id:
        abort(403)
    q = request.args.get('q', '').strip()
    query = MaintenanceRecord.query.filter_by(vehicle_id=vid)
    if q:
        query = query.filter(MaintenanceRecord.service_type.ilike(f'%{q}%'))
    records = query.order_by(MaintenanceRecord.date.desc()).all()
    total_cost = db.session.query(func.sum(MaintenanceRecord.cost)).filter_by(vehicle_id=vid).scalar() or 0
    return render_template('vehicles/records.html', vehicle=v, records=records,
                           total_cost=total_cost, q=q, title=f'{v.brand} {v.model}')


@vehicles_bp.route('/vehicles/<int:vid>/records/new', methods=['GET', 'POST'])
@login_required
def new_record(vid):
    v = Vehicle.query.get_or_404(vid)
    if v.user_id != current_user.id:
        abort(403)
    form = MaintenanceRecordForm()
    if form.validate_on_submit():
        r = MaintenanceRecord(
            vehicle_id=vid,
            service_type=form.service_type.data,
            description=form.description.data,
            date=form.date.data,
            mileage=form.mileage.data,
            cost=form.cost.data,
            workshop=form.workshop.data
        )
        db.session.add(r)
        db.session.commit()
        flash('Registro de mantenimiento guardado.', 'success')
        return redirect(url_for('vehicles.vehicle_records', vid=vid))
    return render_template('vehicles/record_form.html', form=form, vehicle=v,
                           title='Nuevo registro', action='new')


@vehicles_bp.route('/records/<int:rid>/edit', methods=['GET', 'POST'])
@login_required
def edit_record(rid):
    r = MaintenanceRecord.query.get_or_404(rid)
    if r.vehicle.user_id != current_user.id:
        abort(403)
    form = MaintenanceRecordForm(obj=r)
    if form.validate_on_submit():
        r.service_type = form.service_type.data
        r.description = form.description.data
        r.date = form.date.data
        r.mileage = form.mileage.data
        r.cost = form.cost.data
        r.workshop = form.workshop.data
        db.session.commit()
        flash('Registro actualizado.', 'success')
        return redirect(url_for('vehicles.vehicle_records', vid=r.vehicle_id))
    return render_template('vehicles/record_form.html', form=form, vehicle=r.vehicle,
                           title='Editar registro', action='edit')


@vehicles_bp.route('/records/<int:rid>/delete', methods=['POST'])
@login_required
def delete_record(rid):
    r = MaintenanceRecord.query.get_or_404(rid)
    if r.vehicle.user_id != current_user.id:
        abort(403)
    vid = r.vehicle_id
    db.session.delete(r)
    db.session.commit()
    flash('Registro eliminado.', 'info')
    return redirect(url_for('vehicles.vehicle_records', vid=vid))
