import os
import sys

# Ensure workspace root is in sys.path for relative package imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime, timezone
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

from backend.config import Config
from backend.models import db
from backend.models.user import User
from backend.models.employee import Employee
from backend.models.payroll import Payroll
from backend.utils.auth import hash_password


def create_app(config_class=Config):
    """
    Application factory for initializing the Dayflow Flask API application.
    Supports serving frontend static files when deployed as a unified service.
    """
    frontend_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))
    
    app = Flask(
        __name__,
        static_folder=frontend_folder,
        static_url_path=''
    )
    app.config.from_object(config_class)

    # Initialize CORS for cross-origin frontend requests
    CORS(app, resources={r"/api/*": {"origins": app.config['CORS_ORIGINS']}})

    # Initialize database extension
    db.init_app(app)

    # Register API Blueprints
    from backend.routes.auth import auth_bp
    from backend.routes.employees import employees_bp
    from backend.routes.attendance import attendance_bp
    from backend.routes.leaves import leaves_bp
    from backend.routes.payroll import payroll_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(employees_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(leaves_bp)
    app.register_blueprint(payroll_bp)

    # Root API health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'system': 'Dayflow HRMS API',
            'version': '1.0.0',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 200

    # Serve static frontend files when deployed together
    @app.route('/', methods=['GET'])
    def serve_frontend_index():
        if os.path.exists(os.path.join(frontend_folder, 'index.html')):
            return send_from_directory(frontend_folder, 'index.html')
        return jsonify({'message': 'Dayflow HRMS API Server Running'}), 200

    @app.route('/<path:path>', methods=['GET'])
    def serve_frontend_static(path):
        if os.path.exists(os.path.join(frontend_folder, path)):
            return send_from_directory(frontend_folder, path)
        # Fallback to index.html for SPA routing if path not found
        if os.path.exists(os.path.join(frontend_folder, 'index.html')):
            return send_from_directory(frontend_folder, 'index.html')
        return jsonify({'error': 'Resource not found'}), 404

    # Auto-create tables and seed initial demo accounts if needed
    with app.app_context():
        try:
            db.create_all()
            seed_initial_data()
        except Exception as e:
            app.logger.warning(f"Database initialization note: {e}")

    return app


def seed_initial_data():
    """
    Seeds initial HR Admin and sample Employee accounts if database is empty.
    """
    if User.query.first() is not None:
        return  # Data already exists

    try:
        # Seed 1: HR Admin
        admin_user = User(
            employee_id='EMP-ADMIN-01',
            email='admin@dayflow.com',
            password_hash=hash_password('Admin@1234'),
            role='admin',
            is_verified=True
        )
        db.session.add(admin_user)
        db.session.flush()

        admin_emp = Employee(
            user_id=admin_user.id,
            first_name='Sarah',
            last_name='Jenkins',
            phone='+1 (555) 019-2834',
            address='100 Corporate Plaza, Suite 400, New York, NY',
            designation='Head of HR Operations',
            department='Human Resources',
            date_of_joining=datetime.strptime('2022-01-15', '%Y-%m-%d').date(),
            profile_pic_url='https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=400'
        )
        db.session.add(admin_emp)
        db.session.flush()

        admin_payroll = Payroll(
            employee_id=admin_emp.id,
            basic_salary=95000.00,
            allowances=15000.00,
            deductions=8000.00
        )
        admin_payroll.calculate_net_salary()
        db.session.add(admin_payroll)

        # Seed 2: Regular Employee
        staff_user = User(
            employee_id='EMP-1001',
            email='alex.developer@dayflow.com',
            password_hash=hash_password('Employee@1234'),
            role='employee',
            is_verified=True
        )
        db.session.add(staff_user)
        db.session.flush()

        staff_emp = Employee(
            user_id=staff_user.id,
            first_name='Alex',
            last_name='Morgan',
            phone='+1 (555) 382-9102',
            address='42 Tech Lane, San Francisco, CA',
            designation='Senior Software Engineer',
            department='Engineering',
            date_of_joining=datetime.strptime('2023-03-01', '%Y-%m-%d').date(),
            profile_pic_url='https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400'
        )
        db.session.add(staff_emp)
        db.session.flush()

        staff_payroll = Payroll(
            employee_id=staff_emp.id,
            basic_salary=65000.00,
            allowances=12000.00,
            deductions=6000.00
        )
        staff_payroll.calculate_net_salary()
        db.session.add(staff_payroll)

        db.session.commit()
        print("Successfully seeded initial demo users: admin@dayflow.com and alex.developer@dayflow.com")
    except Exception as e:
        db.session.rollback()
        print(f"Error seeding data: {e}")


app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5005))
    app.run(host='0.0.0.0', port=port, debug=True)
