from sqlalchemy import Column, Integer, Float, ForeignKey
from backend.database.database import Base

class Payroll(Base):
    __tablename__ = "payroll"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    basic_salary = Column(Float)
    hra = Column(Float, default=0.0)
    deductions = Column(Float, default=0.0)
    net_salary = Column(Float)