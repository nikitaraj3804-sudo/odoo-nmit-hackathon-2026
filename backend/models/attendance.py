from datetime import datetime, timezone
from backend.models import db

class Attendance(db.Model):
    """
    Attendance record entity tracking check-in/out timestamps and status.
    """
    __tablename__ = 'attendance'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id', ondelete='CASCADE'), nullable=False)
    date = db.Column(db.Date, nullable=False, index=True)
    check_in = db.Column(db.DateTime, nullable=True)
    check_out = db.Column(db.DateTime, nullable=True)
    status = db.Column(
        db.Enum('Present', 'Absent', 'Half-day', 'Leave', name='attendance_status_enum'),
        nullable=False,
        default='Absent',
        index=True
    )
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        db.UniqueConstraint('employee_id', 'date', name='uq_employee_date'),
    )

    def to_dict(self):
        """Converts attendance entity to JSON-serializable dictionary."""
        emp = self.employee
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'employee_name': emp.full_name if emp else 'Unknown',
            'employee_code': emp.user.employee_id if emp and emp.user else '',
            'date': self.date.isoformat() if self.date else None,
            'check_in': self.check_in.isoformat() if self.check_in else None,
            'check_out': self.check_out.isoformat() if self.check_out else None,
            'check_in_time': self.check_in.strftime('%H:%M:%S') if self.check_in else None,
            'check_out_time': self.check_out.strftime('%H:%M:%S') if self.check_out else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
