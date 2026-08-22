from sqlalchemy import Column, Integer, String, Date, ForeignKey
from backend.database.database import Base

class Leave(Base):
    __tablename__ = "leaves"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    leave_type = Column(String)  # Paid, Sick, Unpaid
    start_date = Column(Date)
    end_date = Column(Date)
    remarks = Column(String, nullable=True)
    status = Column(String, default="Pending")  # Pending, Approved, Rejected
    