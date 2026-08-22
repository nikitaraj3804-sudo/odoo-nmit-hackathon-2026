from datetime import datetime
from flask import Blueprint, request, jsonify
from backend.models import db
from backend.models.employee import Employee
from backend.models.user import User
from backend.utils.auth import token_required, role_required

employees_bp = Blueprint('employees', __name__, url_prefix='/api/employees')

@employees_bp.route('', methods=['GET'])
@token_required
@role_required(['admin'])
def list_employees():
    """
    Lists all employees with optional search filter by name, department, or employee_id.
    Query Params: ?search=...&department=...
    """
    search = request.args.get('search', '').strip()
    department = request.args.get('department', '').strip()

    query = Employee.query.join(User)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Employee.first_name.ilike(search_pattern)) |
            (Employee.last_name.ilike(search_pattern)) |
            (User.employee_id.ilike(search_pattern)) |
            (User.email.ilike(search_pattern))
        )

    if department:
        query = query.filter(Employee.department == department)

    employees = query.all()
    return jsonify({
        'count': len(employees),
        'employees': [emp.to_dict() for emp in employees]
    }), 200


@employees_bp.route('/<int:emp_id>', methods=['GET'])
@token_required
def get_employee(emp_id):
    """
    Gets single employee detail profile.
    Employees can view their own profile; Admins can view any profile.
    """
    emp = Employee.query.get(emp_id)
    if not emp:
        return jsonify({'error': 'Employee profile not found.'}), 404

    curr_user = request.current_user
    # Authorization check
    if curr_user['role'] != 'admin' and emp.user_id != curr_user['user_id']:
        return jsonify({'error': 'Forbidden: You can only view your own profile.'}), 403

    return jsonify({'employee': emp.to_dict()}), 200


@employees_bp.route('/<int:emp_id>', methods=['PUT'])
@token_required
def update_employee(emp_id):
    """
    Updates employee profile details.
    Enforces server-side permission splitting:
    - Employees can update: phone, address, profile_pic_url.
    - Admins can update: first_name, last_name, designation, department, date_of_joining, phone, address, profile_pic_url, documents.
    """
    emp = Employee.query.get(emp_id)
    if not emp:
        return jsonify({'error': 'Employee profile not found.'}), 404

    curr_user = request.current_user
    is_admin = (curr_user['role'] == 'admin')
    is_owner = (emp.user_id == curr_user['user_id'])

    if not is_admin and not is_owner:
        return jsonify({'error': 'Forbidden: You do not have permission to update this profile.'}), 403

    data = request.get_json() or {}

    try:
        # Both Employee and Admin can update phone, address, profile picture
        if 'phone' in data:
            emp.phone = str(data['phone']).strip()
        if 'address' in data:
            emp.address = str(data['address']).strip()
        if 'profile_pic_url' in data:
            emp.profile_pic_url = str(data['profile_pic_url']).strip()

        # Only Admin can update core details
        if is_admin:
            if 'first_name' in data and data['first_name']:
                emp.first_name = str(data['first_name']).strip()
            if 'last_name' in data and data['last_name']:
                emp.last_name = str(data['last_name']).strip()
            if 'designation' in data and data['designation']:
                emp.designation = str(data['designation']).strip()
            if 'department' in data and data['department']:
                emp.department = str(data['department']).strip()
            if 'date_of_joining' in data and data['date_of_joining']:
                try:
                    emp.date_of_joining = datetime.strptime(data['date_of_joining'], '%Y-%m-%d').date()
                except ValueError:
                    return jsonify({'error': 'Invalid date_of_joining format. Use YYYY-MM-DD.'}), 400
            if 'documents' in data:
                emp.documents = data['documents']

        db.session.commit()
        return jsonify({
            'message': 'Profile updated successfully.',
            'employee': emp.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update profile: {str(e)}'}), 500
