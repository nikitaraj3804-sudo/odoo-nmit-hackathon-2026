import json
from datetime import datetime, timezone
from backend.models import db

class Employee(db.Model):
    """
    Employee profile entity containing personal details, job roles, and documents.
    """
    __tablename__ = 'employees'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.Text, nullable=True)
    designation = db.Column(db.String(100), nullable=False, default='Software Engineer')
    department = db.Column(db.String(100), nullable=False, default='Engineering')
    date_of_joining = db.Column(db.Date, nullable=False)
    profile_pic_url = db.Column(db.String(500), nullable=True)
    documents = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    attendances = db.relationship('Attendance', backref='employee', cascade='all, delete-orphan')
    leaves = db.relationship('Leave', backref='employee', cascade='all, delete-orphan')
    payroll = db.relationship('Payroll', backref='employee', uselist=False, cascade='all, delete-orphan')

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def to_dict(self):
        """Converts employee profile entity to JSON-serializable dictionary."""
        docs = self.documents
        if isinstance(docs, str):
            try:
                docs = json.loads(docs)
            except Exception:
                docs = []
                
        return {
            'id': self.id,
            'user_id': self.user_id,
            'employee_id': self.user.employee_id if self.user else None,
            'email': self.user.email if self.user else None,
            'role': self.user.role if self.user else 'employee',
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'phone': self.phone or '',
            'address': self.address or '',
            'designation': self.designation,
            'department': self.department,
            'date_of_joining': self.date_of_joining.isoformat() if self.date_of_joining else None,
            'profile_pic_url': self.profile_pic_url or '',
            'documents': docs or [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
