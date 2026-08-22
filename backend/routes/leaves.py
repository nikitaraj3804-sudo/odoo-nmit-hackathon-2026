from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from backend.models import db
from backend.models.leave import Leave
from backend.models.employee import Employee
from backend.models.attendance import Attendance
from backend.utils.auth import token_required, role_required
from backend.utils.validators import validate_date_range

leaves_bp = Blueprint('leaves', __name__, url_prefix='/api/leaves')

@leaves_bp.route('', methods=['POST'])
@token_required
def apply_leave():
    """
    Employee applies for leave.
    Payload: { leave_type, start_date, end_date, remarks }
    """
    curr_user = request.current_user
    emp = Employee.query.filter_by(user_id=curr_user['user_id']).first()
    if not emp:
        return jsonify({'error': 'Employee profile not found.'}), 404

    data = request.get_json() or {}
    leave_type = data.get('leave_type', 'Paid')
    start_date_str = data.get('start_date')
    end_date_str = data.get('end_date')
    remarks = data.get('remarks', '').strip()

    if leave_type not in ['Paid', 'Sick', 'Unpaid']:
        return jsonify({'error': "leave_type must be 'Paid', 'Sick', or 'Unpaid'."}), 400

    is_valid, date_err, total_days = validate_date_range(start_date_str, end_date_str)
    if not is_valid:
        return jsonify({'error': date_err}), 400

    start_d = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    end_d = datetime.strptime(end_date_str, '%Y-%m-%d').date()

    # Create Leave record
    new_leave = Leave(
        employee_id=emp.id,
        leave_type=leave_type,
        start_date=start_d,
        end_date=end_d,
        total_days=total_days,
        remarks=remarks,
        status='Pending'
    )
    db.session.add(new_leave)
    db.session.commit()

    return jsonify({
        'message': 'Leave application submitted successfully.',
        'leave': new_leave.to_dict()
    }), 201


@leaves_bp.route('', methods=['GET'])
@token_required
def list_leaves():
    """
    Lists leave applications.
    Query Params: ?status=...&employee_id=...
    Employees can view only their own leave requests; Admins can view all.
    """
    curr_user = request.current_user
    status_filter = request.args.get('status', '').strip()
    emp_id_param = request.args.get('employee_id', type=int)

    query = Leave.query.join(Employee)

    if curr_user['role'] != 'admin':
        curr_emp = Employee.query.filter_by(user_id=curr_user['user_id']).first()
        if not curr_emp:
            return jsonify({'leaves': []}), 200
        query = query.filter(Leave.employee_id == curr_emp.id)
    elif emp_id_param:
        query = query.filter(Leave.employee_id == emp_id_param)

    if status_filter in ['Pending', 'Approved', 'Rejected']:
        query = query.filter(Leave.status == status_filter)

    leaves_list = query.order_by(Leave.created_at.desc()).all()
    return jsonify({
        'count': len(leaves_list),
        'leaves': [l.to_dict() for l in leaves_list]
    }), 200


@leaves_bp.route('/<int:leave_id>/approve', methods=['PUT'])
@token_required
@role_required(['admin'])
def approve_or_reject_leave(leave_id):
    """
    Admin approves or rejects a leave request.
    Payload: { status: 'Approved' | 'Rejected', admin_comment: '...' }
    If approved, automatically creates/updates Attendance records for the date range with status='Leave'.
    """
    leave_req = Leave.query.get(leave_id)
    if not leave_req:
        return jsonify({'error': 'Leave request not found.'}), 404

    data = request.get_json() or {}
    new_status = data.get('status')
    admin_comment = data.get('admin_comment', '').strip()

    if new_status not in ['Approved', 'Rejected']:
        return jsonify({'error': "status must be either 'Approved' or 'Rejected'."}), 400

    leave_req.status = new_status
    leave_req.admin_comment = admin_comment

    # If approved, sync with Attendance table across date range
    if new_status == 'Approved':
        current_d = leave_req.start_date
        while current_d <= leave_req.end_date:
            att_record = Attendance.query.filter_by(
                employee_id=leave_req.employee_id,
                date=current_d
            ).first()

            if not att_record:
                att_record = Attendance(
                    employee_id=leave_req.employee_id,
                    date=current_d,
                    status='Leave'
                )
                db.session.add(att_record)
            else:
                att_record.status = 'Leave'
            
            current_d += timedelta(days=1)

    db.session.commit()
    return jsonify({
        'message': f'Leave request has been {new_status.lower()}.',
        'leave': leave_req.to_dict()
    }), 200
