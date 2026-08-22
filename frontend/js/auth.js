/**
 * Dayflow HRMS - Authentication & API Utility Module
 */

// RAILWAY / PRODUCTION API BASE URL CONFIGURATION
// If frontend is deployed separately (e.g. Netlify/Vercel), replace with your Railway backend URL:
// const API_BASE_URL = 'https://your-dayflow-backend.up.railway.app/api';
const API_BASE_URL = (window.location.origin.includes('localhost') || window.location.origin.includes('127.0.0.1'))
  ? (window.location.port === '8000' ? 'http://127.0.0.1:5005/api' : `${window.location.origin}/api`)
  : `${window.location.origin}/api`;

/**
 * Toast Notification Utility
 */
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `
    <span>${message}</span>
    <span style="cursor:pointer; margin-left:12px;" onclick="this.parentElement.remove()">✕</span>
  `;
  container.appendChild(toast);

  setTimeout(() => {
    if (toast.parentElement) toast.remove();
  }, 4000);
}

/**
 * Authenticated API Fetch Wrapper
 */
async function apiFetch(endpoint, options = {}) {
  const token = localStorage.getItem('dayflow_token');
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {})
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || 'API Request failed');
    }
    return data;
  } catch (err) {
    console.error(`API Error on ${endpoint}:`, err);
    throw err;
  }
}

/**
 * Tab Switcher for Auth Portal
 */
function switchTab(tabName) {
  ['login', 'signup', 'verify'].forEach(t => {
    const tabBtn = document.getElementById(`tab-${t}`);
    const form = document.getElementById(`form-${t}`);
    if (tabBtn && form) {
      if (t === tabName) {
        tabBtn.classList.add('active');
        form.style.display = 'block';
      } else {
        tabBtn.classList.remove('active');
        form.style.display = 'none';
      }
    }
  });
  
  const alertBox = document.getElementById('auth-alert');
  if (alertBox) alertBox.style.display = 'none';
}

/**
 * Client-side Password Validation
 */
function validatePasswordClientSide() {
  const pwd = document.getElementById('signup-password')?.value || '';
  const rules = document.getElementById('pwd-rules');
  if (!rules) return;

  const hasLength = pwd.length >= 8;
  const hasUpper = /[A-Z]/.test(pwd);
  const hasLower = /[a-z]/.test(pwd);
  const hasNum = /[0-9]/.test(pwd);
  const hasSpecial = /[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]/.test(pwd);

  if (hasLength && hasUpper && hasLower && hasNum && hasSpecial) {
    rules.style.color = 'var(--success)';
    rules.textContent = '✓ Password meets all security rules.';
  } else {
    rules.style.color = 'var(--warning)';
    rules.textContent = 'Password must be 8+ chars, contain uppercase, lowercase, digit, & special char.';
  }
}

/**
 * Sign In Handler
 */
async function handleLogin(event) {
  if (event && event.preventDefault) event.preventDefault();
  const email = (document.getElementById('login-email')?.value || '').trim();
  const password = document.getElementById('login-password')?.value || '';

  const alertBox = document.getElementById('auth-alert');
  if (alertBox) alertBox.style.display = 'none';

  if (!email || !password) {
    showToast('Please enter both email and password.', 'error');
    return;
  }

  try {
    const res = await apiFetch('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });

    localStorage.setItem('dayflow_token', res.token);
    localStorage.setItem('dayflow_user', JSON.stringify(res.user));

    showToast('Sign in successful!', 'success');

    // SPA-style Redirect based on Role
    setTimeout(() => {
      if (res.user.role === 'admin') {
        window.location.href = 'admin-dashboard.html';
      } else {
        window.location.href = 'employee-dashboard.html';
      }
    }, 600);

  } catch (err) {
    if (alertBox) {
      alertBox.style.display = 'block';
      alertBox.style.borderColor = 'var(--danger)';
      alertBox.style.color = 'var(--danger)';
      alertBox.textContent = err.message;
    }
    showToast(err.message, 'error');
  }
}

/**
 * Sign Up Handler
 */
async function handleSignup(event) {
  if (event && event.preventDefault) event.preventDefault();
  const first_name = (document.getElementById('signup-firstname')?.value || '').trim();
  const last_name = (document.getElementById('signup-lastname')?.value || '').trim();
  const employee_id = (document.getElementById('signup-empid')?.value || '').trim();
  const email = (document.getElementById('signup-email')?.value || '').trim();
  const role = document.getElementById('signup-role')?.value || 'employee';
  const password = document.getElementById('signup-password')?.value || '';

  try {
    const res = await apiFetch('/auth/signup', {
      method: 'POST',
      body: JSON.stringify({ first_name, last_name, employee_id, email, role, password })
    });

    showToast('Registration successful!', 'success');
    
    // Auto-fill token in verification tab for convenience
    switchTab('verify');
    const verifyInput = document.getElementById('verify-token');
    if (verifyInput && res.verification_token) {
      verifyInput.value = res.verification_token;
    }

    const alertBox = document.getElementById('auth-alert');
    if (alertBox) {
      alertBox.style.display = 'block';
      alertBox.style.borderColor = 'var(--success)';
      alertBox.style.color = 'var(--success)';
      alertBox.textContent = `Account registered! Verification token generated: ${res.verification_token}`;
    }

  } catch (err) {
    showToast(err.message, 'error');
  }
}

/**
 * Email Verification Handler
 */
async function handleEmailVerification(event) {
  if (event && event.preventDefault) event.preventDefault();
  const token = (document.getElementById('verify-token')?.value || '').trim();

  try {
    const res = await apiFetch(`/auth/verify/${token}`, { method: 'GET' });
    showToast('Email verified successfully! You can now log in.', 'success');
    switchTab('login');
  } catch (err) {
    showToast(err.message, 'error');
  }
}

/**
 * Sign Out Handler
 */
function handleLogout() {
  localStorage.removeItem('dayflow_token');
  localStorage.removeItem('dayflow_user');
  showToast('Logged out of Dayflow.', 'info');
  window.location.href = 'index.html';
}

/**
 * Auth Guard Check
 */
function checkAuthGuard(requiredRole = null) {
  const token = localStorage.getItem('dayflow_token');
  const userStr = localStorage.getItem('dayflow_user');
  
  if (!token || !userStr) {
    window.location.href = 'index.html';
    return null;
  }

  const user = JSON.parse(userStr);
  if (requiredRole && user.role !== requiredRole) {
    showToast('Access denied: Unauthorized role.', 'error');
    if (user.role === 'admin') window.location.href = 'admin-dashboard.html';
    else window.location.href = 'employee-dashboard.html';
    return null;
  }

  return user;
}
