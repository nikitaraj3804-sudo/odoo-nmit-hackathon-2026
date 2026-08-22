import uuid
from datetime import datetime, timedelta, timezone
from flask import Blueprint, request, jsonify
from backend.models import db
from backend.models.user import User, EmailVerification
from backend.models.employee import Employee
from backend.models.payroll import Payroll
from backend.utils.validators import validate_email, validate_password
from backend.utils.auth import hash_password, verify_password, generate_jwt_token, token_required

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/signup', methods=['POST'])
def signup():
    """
    Registers a new user account (Admin/HR Officer or Employee).
    Payload: { employee_id, email, password, role, first_name, last_name }
    """
    data = request.get_json() or {}
    employee_id = (data.get('employee_id') or '').strip()
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''
    role = (data.get('role') or 'employee').strip().lower()
    first_name = (data.get('first_name') or 'John').strip()
    last_name = (data.get('last_name') or 'Doe').strip()

    # Input validation
    if not employee_id:
        return jsonify({'error': 'Employee ID is required.'}), 400

    if not validate_email(email):
        return jsonify({'error': 'Invalid email address format.'}), 400

    is_valid_pwd, pwd_error = validate_password(password)
    if not is_valid_pwd:
        return jsonify({'error': pwd_error}), 400

    if role not in ['admin', 'employee']:
        return jsonify({'error': "Role must be either 'admin' or 'employee'."}), 400

    # Duplicate checks
    if User.query.filter_by(employee_id=employee_id).first():
        return jsonify({'error': f'Employee ID "{employee_id}" is already registered.'}), 409

    if User.query.filter_by(email=email).first():
        return jsonify({'error': f'Email "{email}" is already registered.'}), 409

    try:
        # Create User record
        pwd_hash = hash_password(password)
        new_user = User(
            employee_id=employee_id,
            email=email,
            password_hash=pwd_hash,
            role=role,
            is_verified=False
        )
        db.session.add(new_user)
        db.session.flush()

        # Create corresponding Employee record
        new_employee = Employee(
            user_id=new_user.id,
            first_name=first_name,
            last_name=last_name,
            designation='HR Officer' if role == 'admin' else 'Software Engineer',
            department='Human Resources' if role == 'admin' else 'Engineering',
            date_of_joining=datetime.now(timezone.utc).date()
        )
        db.session.add(new_employee)
        db.session.flush()

        # Initialize default Payroll record
        new_payroll = Payroll(
            employee_id=new_employee.id,
            basic_salary=75000.00 if role == 'admin' else 50000.00,
            allowances=10000.00,
            deductions=5000.00
        )
        new_payroll.calculate_net_salary()
        db.session.add(new_payroll)

        # Generate Email Verification Token
        verification_token = str(uuid.uuid4())
        expires = datetime.now(timezone.utc) + timedelta(hours=24)
        verification = EmailVerification(
            user_id=new_user.id,
            token=verification_token,
            expires_at=expires
        )
        db.session.add(verification)

        db.session.commit()

        return jsonify({
            'message': 'Account registered successfully. Please verify your email to continue.',
            'user': new_user.to_dict(),
            'verification_token': verification_token
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'An error occurred during registration: {str(e)}'}), 500


@auth_bp.route('/verify/<token>', methods=['GET'])
def verify_email(token):
    """
    Verifies user email using token.
    """
    verification = EmailVerification.query.filter_by(token=token).first()
    if not verification:
        return jsonify({'error': 'Invalid verification token.'}), 400

    # Compare UTC timestamps safely
    now_utc = datetime.now(timezone.utc)
    exp_at = verification.expires_at
    if exp_at.tzinfo is None:
        exp_at = exp_at.replace(tzinfo=timezone.utc)

    if now_utc > exp_at:
        return jsonify({'error': 'Verification token has expired.'}), 400

    user = User.query.get(verification.user_id)
    if not user:
        return jsonify({'error': 'Associated user account not found.'}), 404

    user.is_verified = True
    db.session.delete(verification)
    db.session.commit()

    return jsonify({
        'message': 'Email verified successfully! You can now log in to Dayflow.',
        'user': user.to_dict()
    }), 200


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Authenticates user credentials and returns JWT token upon success.
    Payload: { email, password }
    """
    data = request.get_json() or {}
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    if not email or not password:
        return jsonify({'error': 'Both email and password are required.'}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not verify_password(user.password_hash, password):
        return jsonify({'error': 'Invalid email or password. Please try again.'}), 401

    employee = user.employee_profile
    employee_db_id = employee.id if employee else None

    # Issue JWT Token
    token = generate_jwt_token(
        user_id=user.id,
        employee_id=user.employee_id,
        email=user.email,
        role=user.role
    )

    return jsonify({
        'message': 'Sign in successful.',
        'token': token,
        'user': {
            'id': user.id,
            'employee_id': user.employee_id,
            'employee_db_id': employee_db_id,
            'email': user.email,
            'role': user.role,
            'is_verified': user.is_verified,
            'full_name': employee.full_name if employee else 'User'
        }
    }), 200


@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user():
    """
    Fetches active user context and profile.
    """
    curr = request.current_user
    user = User.query.get(curr['user_id'])
    if not user:
        return jsonify({'error': 'User not found.'}), 404

    employee = user.employee_profile
    return jsonify({
        'user': user.to_dict(),
        'employee': employee.to_dict() if employee else None
    }), 200
