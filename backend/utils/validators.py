import re
from datetime import datetime

def validate_password(password: str) -> tuple[bool, str]:
    """
    Validates password complexity requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one numeric digit
    - At least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)
    
    Returns:
        (is_valid, error_message)
    """
    if not password or len(password) < 8:
        return False, "Password must be at least 8 characters long."
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter."
        
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter."
        
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one digit."
        
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password):
        return False, "Password must contain at least one special character."
        
    return True, ""

def validate_email(email: str) -> bool:
    """
    Validates RFC-compliant email address format using regular expression.
    """
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))

def validate_date_range(start_date_str: str, end_date_str: str) -> tuple[bool, str, int]:
    """
    Validates that end_date >= start_date and calculates total duration in days.
    Expected format: YYYY-MM-DD
    
    Returns:
        (is_valid, error_message, total_days)
    """
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return False, "Invalid date format. Expected YYYY-MM-DD.", 0
        
    if end_date < start_date:
        return False, "End date cannot be earlier than start date.", 0
        
    total_days = (end_date - start_date).days + 1
    return True, "", total_days

def validate_payroll_amounts(*amounts) -> tuple[bool, str]:
    """
    Ensures all payroll amounts (basic, allowances, deductions) are numeric and non-negative.
    
    Returns:
        (is_valid, error_message)
    """
    for amt in amounts:
        try:
            val = float(amt)
            if val < 0:
                return False, "Salary components cannot be negative numbers."
        except (ValueError, TypeError):
            return False, "Salary components must be valid numeric values."
    return True, ""
