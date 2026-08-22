from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database.database import Base, engine
from backend import models  # ensures all models are registered

# Create all tables in the database
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Dayflow HRMS")

# Allow frontend (HTML/JS) to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Dayflow HRMS backend is running"}

# Routers will be added here once auth.py and other routes are ready
# from backend.routes import auth, employees, attendance, leaves, payroll
# app.include_router(auth.router, prefix="/auth", tags=["Auth"])
