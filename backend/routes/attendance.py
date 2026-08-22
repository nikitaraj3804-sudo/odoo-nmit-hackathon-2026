from datetime import datetime, date, timedelta, timezone
from flask import Blueprint, request, jsonify
from backend.models import db
from backend.models.attendance import Attendance
from backend.models.employee import Employee
from backend.utils.auth import token_required, role_required

attendance_bp = Blueprint('attendance', __name__, url_prefix='/api/attendance')

@attendance_bp.route('/check-in', methods=['POST'])
@token_required
def check_in():
    """
    Records employee check-in timestamp for today.
    """
    curr_user = request.current_user
    emp = Employee.query.filter_by(user_id=curr_user['user_id']).first()
    if not emp:
        return jsonify({'error': 'Employee profile not found.'}), 404

    today = datetime.now(timezone.utc).date()
    now_dt = datetime.now(timezone.utc)

    # Fetch or create today's attendance record
    record = Attendance.query.filter_by(employee_id=emp.id, date=today).first()
    if not record:
        record = Attendance(
            employee_id=emp.id,
            date=today,
            check_in=now_dt,
            status='Present'
        )
        db.session.add(record)
    else:
        if record.check_in:
            return jsonify({'error': 'You have already checked in today.', 'record': record.to_dict()}), 400
        record.check_in = now_dt
        record.status = 'Present'

    db.session.commit()
    return jsonify({
        'message': 'Check-in recorded successfully.',
        'record': record.to_dict()
    }), 200


@attendance_bp.route('/check-out', methods=['POST'])
@token_required
def check_out():
    """
    Records employee check-out timestamp for today.
    """
    curr_user = request.current_user
    emp = Employee.query.filter_by(user_id=curr_user['user_id']).first()
    if not emp:
        return jsonify({'error': 'Employee profile not found.'}), 404

    today = datetime.now(timezone.utc).date()
    now_dt = datetime.now(timezone.utc)

    record = Attendance.query.filter_by(employee_id=emp.id, date=today).first()
    if not record or not record.check_in:
        return jsonify({'error': 'You must check in before checking out.'}), 400

    if record.check_out:
        return jsonify({'error': 'You have already checked out today.', 'record': record.to_dict()}), 400

    record.check_out = now_dt
    
    # Half-day calculation (if total duration < 4 hours)
    duration = (now_dt - record.check_in.replace(tzinfo=timezone.utc)).total_seconds() / 3600.0
    if duration < 4.0 and record.status != 'Leave':
        record.status = 'Half-day'

    db.session.commit()
    return jsonify({
        'message': 'Check-out recorded successfully.',
        'record': record.to_dict()
    }), 200


@attendance_bp.route('', methods=['GET'])
@token_required
def list_attendance():
    """
    Retrieves attendance records.
    Query Params: ?employee_id=...&start_date=...&end_date=...&view=daily|weekly
    Employees can view only their own records; Admin can view all.
    """
    curr_user = request.current_user
    emp_id_param = request.args.get('employee_id', type=int)
    start_date_param = request.args.get('start_date')
    end_date_param = request.args.get('end_date')
    view_type = request.args.get('view', 'daily')

    query = Attendance.query.join(Employee)

    # Role filter
    if curr_user['role'] != 'admin':
        curr_emp = Employee.query.filter_by(user_id=curr_user['user_id']).first()
        if not curr_emp:
            return jsonify({'attendance': []}), 200
        query = query.filter(Attendance.employee_id == curr_emp.id)
    elif emp_id_param:
        query = query.filter(Attendance.employee_id == emp_id_param)

    # Date range filters
    if start_date_param:
        try:
            s_date = datetime.strptime(start_date_param, '%Y-%m-%d').date()
            query = query.filter(Attendance.date >= s_date)
        except ValueError:
            pass

    if end_date_param:
        try:
            e_date = datetime.strptime(end_date_param, '%Y-%m-%d').date()
            query = query.filter(Attendance.date <= e_date)
        except ValueError:
            pass

    # Weekly view default (last 7 days) if dates omitted and view==weekly
    if view_type == 'weekly' and not start_date_param:
        today = datetime.now(timezone.utc).date()
        week_ago = today - timedelta(days=7)
        query = query.filter(Attendance.date >= week_ago)

    records = query.order_by(Attendance.date.desc()).all()
    return jsonify({
        'view': view_type,
        'count': len(records),
        'attendance': [r.to_dict() for r in records]
    }), 200


@attendance_bp.route('/mark', methods=['POST'])
@token_required
@role_required(['admin'])
def mark_attendance():
    """
    Admin manual attendance mark/override endpoint.
    Payload: { employee_id, date, status }
    """
    data = request.get_json() or {}
    employee_id = data.get('employee_id')
    date_str = data.get('date')
    status = data.get('status')

    if not employee_id or not date_str or not status:
        return jsonify({'error': 'employee_id, date, and status are required.'}), 400

    if status not in ['Present', 'Absent', 'Half-day', 'Leave']:
        return jsonify({'error': 'Invalid status value.'}), 400

    try:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD.'}), 400

    record = Attendance.query.filter_by(employee_id=employee_id, date=target_date).first()
    if not record:
        record = Attendance(
            employee_id=employee_id,
            date=target_date,
            status=status
        )
        db.session.add(record)
    else:
        record.status = status

    db.session.commit()
    return jsonify({
        'message': f'Attendance marked as {status} for date {date_str}.',
        'record': record.to_dict()
    }), 200
