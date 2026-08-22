from datetime import datetime, timezone
from backend.models import db

class Leave(db.Model):
    """
    Leave request entity for managing employee time-off requests.
    """
    __tablename__ = 'leaves'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id', ondelete='CASCADE'), nullable=False)
    leave_type = db.Column(
        db.Enum('Paid', 'Sick', 'Unpaid', name='leave_type_enum'),
        nullable=False,
        default='Paid'
    )
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    total_days = db.Column(db.Integer, nullable=False, default=1)
    remarks = db.Column(db.Text, nullable=True)
    status = db.Column(
        db.Enum('Pending', 'Approved', 'Rejected', name='leave_status_enum'),
        nullable=False,
        default='Pending',
        index=True
    )
    admin_comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self):
        """Converts leave entity to JSON-serializable dictionary."""
        emp = self.employee
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'employee_name': emp.full_name if emp else 'Unknown',
            'employee_code': emp.user.employee_id if emp and emp.user else '',
            'department': emp.department if emp else '',
            'leave_type': self.leave_type,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'total_days': self.total_days,
            'remarks': self.remarks or '',
            'status': self.status,
            'admin_comment': self.admin_comment or '',
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
