from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from backend.database.database import Base
from datetime import datetime

class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    check_in = Column(DateTime, default=datetime.utcnow)
    check_out = Column(DateTime, nullable=True)
    status = Column(String, default="Present")  # Present, Absent, Half-day, Leave
    