from datetime import datetime, timezone
from backend.models import db

class Payroll(db.Model):
    """
    Payroll entity managing salary components for an employee.
    """
    __tablename__ = 'payroll'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id', ondelete='CASCADE'), nullable=False, unique=True)
    basic_salary = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    allowances = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    deductions = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    net_salary = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    def calculate_net_salary(self):
        """Recalculates net salary on server side."""
        basic = float(self.basic_salary or 0)
        allow = float(self.allowances or 0)
        ded = float(self.deductions or 0)
        self.net_salary = round(basic + allow - ded, 2)
        return self.net_salary

    def to_dict(self):
        """Converts payroll entity to JSON-serializable dictionary."""
        emp = self.employee
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'employee_name': emp.full_name if emp else 'Unknown',
            'employee_code': emp.user.employee_id if emp and emp.user else '',
            'designation': emp.designation if emp else '',
            'department': emp.department if emp else '',
            'basic_salary': float(self.basic_salary),
            'allowances': float(self.allowances),
            'deductions': float(self.deductions),
            'net_salary': float(self.net_salary),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
