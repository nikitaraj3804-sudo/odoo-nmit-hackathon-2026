from flask import Blueprint, request, jsonify
from backend.models import db
from backend.models.payroll import Payroll
from backend.models.employee import Employee
from backend.utils.auth import token_required, role_required
from backend.utils.validators import validate_payroll_amounts

payroll_bp = Blueprint('payroll', __name__, url_prefix='/api/payroll')

@payroll_bp.route('/me', methods=['GET'])
@token_required
def get_own_payroll():
    """
    Returns read-only salary details for the currently logged-in employee.
    """
    curr_user = request.current_user
    emp = Employee.query.filter_by(user_id=curr_user['user_id']).first()
    if not emp:
        return jsonify({'error': 'Employee profile not found.'}), 404

    payroll = Payroll.query.filter_by(employee_id=emp.id).first()
    if not payroll:
        # Create default payroll if not exists
        payroll = Payroll(employee_id=emp.id, basic_salary=50000.00, allowances=10000.00, deductions=5000.00)
        payroll.calculate_net_salary()
        db.session.add(payroll)
        db.session.commit()

    return jsonify({'payroll': payroll.to_dict()}), 200


@payroll_bp.route('/<int:emp_id>', methods=['GET'])
@token_required
@role_required(['admin'])
def get_employee_payroll(emp_id):
    """
    Admin endpoint to view payroll details for a specific employee.
    """
    emp = Employee.query.get(emp_id)
    if not emp:
        return jsonify({'error': 'Employee not found.'}), 404

    payroll = Payroll.query.filter_by(employee_id=emp.id).first()
    if not payroll:
        payroll = Payroll(employee_id=emp.id, basic_salary=50000.00, allowances=10000.00, deductions=5000.00)
        payroll.calculate_net_salary()
        db.session.add(payroll)
        db.session.commit()

    return jsonify({'payroll': payroll.to_dict()}), 200


@payroll_bp.route('/<int:emp_id>', methods=['PUT'])
@token_required
@role_required(['admin'])
def update_payroll(emp_id):
    """
    Admin endpoint to update salary breakdown for an employee.
    Payload: { basic_salary, allowances, deductions }
    Server recalculates net_salary and validates non-negative numeric inputs.
    """
    emp = Employee.query.get(emp_id)
    if not emp:
        return jsonify({'error': 'Employee not found.'}), 404

    data = request.get_json() or {}
    basic = data.get('basic_salary', 0.0)
    allow = data.get('allowances', 0.0)
    ded = data.get('deductions', 0.0)

    is_valid, err_msg = validate_payroll_amounts(basic, allow, ded)
    if not is_valid:
        return jsonify({'error': err_msg}), 400

    payroll = Payroll.query.filter_by(employee_id=emp.id).first()
    if not payroll:
        payroll = Payroll(employee_id=emp.id)
        db.session.add(payroll)

    payroll.basic_salary = float(basic)
    payroll.allowances = float(allow)
    payroll.deductions = float(ded)
    payroll.calculate_net_salary()

    db.session.commit()

    return jsonify({
        'message': 'Payroll structure updated successfully.',
        'payroll': payroll.to_dict()
    }), 200
