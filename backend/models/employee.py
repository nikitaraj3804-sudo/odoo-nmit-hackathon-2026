from sqlalchemy import Column, Integer, String, ForeignKey
from backend.database.database import Base

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    full_name = Column(String)
    phone = Column(String, nullable=True)
    address = Column(String, nullable=True)
    job_title = Column(String, nullable=True)
    department = Column(String, nullable=True)
    profile_picture = Column(String, nullable=True)