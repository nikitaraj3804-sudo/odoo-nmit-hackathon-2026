/**
 * Dayflow HRMS - Dashboard UI & Navigation Controller
 */

let allEmployees = [];

document.addEventListener('DOMContentLoaded', () => {
  const isDashboardPage = document.getElementById('sec-employees') || document.getElementById('sec-emp-home');
  if (!isDashboardPage) return;

  const isAdminPage = !!document.getElementById('sec-employees');
  const currentUser = checkAuthGuard(isAdminPage ? 'admin' : 'employee');
  if (!currentUser) return;

  if (isAdminPage) {
    initAdminDashboard(currentUser);
  } else {
    initEmployeeDashboard(currentUser);
  }
});

/**
 * Initialize HR Admin Dashboard
 */

async function initAdminDashboard(user) {
  document.getElementById('admin-name').textContent = user.full_name || 'Admin Officer';
  document.getElementById('admin-email').textContent = user.email || 'admin@dayflow.com';

  await loadAdminEmployees();
  await loadAdminAttendance();
  await loadAdminLeaves();
  await loadAdminPayroll();
}

/**
 * Initialize Employee Dashboard
 */
async function initEmployeeDashboard(user) {
  document.getElementById('emp-display-name').textContent = user.full_name || 'Employee';
  document.getElementById('emp-display-code').textContent = user.employee_id || 'EMP';

  await loadTodayAttendanceStatus();
  await loadEmployeeProfile(user.employee_db_id);
  await loadEmployeeAttendance();
  await loadEmployeeLeaves();
  await loadOwnPayroll();
}

/**
 * Switch Navigation View (Admin)
 */
function switchAdminSection(secName) {
  const sections = ['employees', 'attendance', 'leaves', 'payroll', 'reports'];
  sections.forEach(s => {
    const secEl = document.getElementById(`sec-${s}`);
    const navEl = document.getElementById(`nav-${s}`);
    if (secEl && navEl) {
      if (s === secName) {
        secEl.style.display = 'block';
        navEl.classList.add('active');
      } else {
        secEl.style.display = 'none';
        navEl.classList.remove('active');
      }
    }
  });

  const titleMap = {
    employees: 'Employee Directory',
    attendance: 'Attendance Logs & Matrix',
    leaves: 'Leave Request Approvals',
    payroll: 'Payroll Structure Management',
    reports: 'Reports & Exportable Analytics'
  };

  const titleEl = document.getElementById('page-title');
  if (titleEl) titleEl.textContent = titleMap[secName] || 'Dashboard';
}

/**
 * Switch Navigation View (Employee)
 */
function switchEmpSection(secName) {
  const sections = ['home', 'profile', 'attendance', 'leaves', 'payroll'];
  sections.forEach(s => {
    const secEl = document.getElementById(`sec-emp-${s}`);
    const navEl = document.getElementById(`nav-emp-${s}`);
    if (secEl && navEl) {
      if (s === secName) {
        secEl.style.display = 'block';
        navEl.classList.add('active');
      } else {
        secEl.style.display = 'none';
        navEl.classList.remove('active');
      }
    }
  });
}

/**
 * Load Employee List for Admin Directory
 */
async function loadAdminEmployees() {
  try {
    const data = await apiFetch('/employees');
    allEmployees = data.employees || [];
    renderEmployeeTable(allEmployees);

    // Update metric card
    const metricCount = document.getElementById('metric-total-employees');
    if (metricCount) metricCount.textContent = allEmployees.length;

    // Populate dropdowns in modals
    populateEmployeeDropdowns(allEmployees);

  } catch (err) {
    showToast(`Failed to load employee list: ${err.message}`, 'error');
  }
}

/**
 * Render Employee Table DOM
 */
function renderEmployeeTable(employees) {
  const tbody = document.getElementById('employee-table-body');
  if (!tbody) return;

  if (!employees.length) {
    tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; color:var(--text-muted);">No employee records found.</td></tr>`;
    return;
  }

  tbody.innerHTML = employees.map(emp => `
    <tr>
      <td>
        <div style="display:flex; align-items:center; gap:10px;">
          <img src="${emp.profile_pic_url || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400'}" class="avatar">
          <div>
            <div style="font-weight:600;">${emp.full_name}</div>
            <div style="font-size:12px; color:var(--text-muted);">${emp.email}</div>
          </div>
        </div>
      </td>
      <td><span class="badge badge-leave">${emp.employee_id}</span></td>
      <td>${emp.department}</td>
      <td>${emp.designation}</td>
      <td>${emp.date_of_joining || 'N/A'}</td>
      <td>
        <button class="btn btn-secondary" style="padding:4px 10px; font-size:12px;" onclick="openViewEmployeeModal(${emp.id})">
          👁 View / Edit
        </button>
      </td>
    </tr>
  `).join('');
}

/**
 * Filter Employee Directory Table
 */
function filterEmployees() {
  const search = document.getElementById('employee-search')?.value.toLowerCase() || '';
  const dept = document.getElementById('department-filter')?.value || '';

  const filtered = allEmployees.filter(emp => {
    const matchSearch = emp.full_name.toLowerCase().includes(search) ||
                        emp.employee_id.toLowerCase().includes(search) ||
                        emp.email.toLowerCase().includes(search);
    const matchDept = !dept || emp.department === dept;
    return matchSearch && matchDept;
  });

  renderEmployeeTable(filtered);
}

/**
 * Populate Dropdowns
 */
function populateEmployeeDropdowns(employees) {
  const attEmpSelect = document.getElementById('att-filter-emp');
  const overrideSelect = document.getElementById('override-emp-select');

  if (attEmpSelect) {
    attEmpSelect.innerHTML = `<option value="">All Employees</option>` +
      employees.map(e => `<option value="${e.id}">${e.full_name} (${e.employee_id})</option>`).join('');
  }

  if (overrideSelect) {
    overrideSelect.innerHTML = employees.map(e => `<option value="${e.id}">${e.full_name} (${e.employee_id})</option>`).join('');
  }
}

/**
 * View / Edit Employee Modal (Admin View-as-Employee Mode)
 */
async function openViewEmployeeModal(empId) {
  try {
    const data = await apiFetch(`/employees/${empId}`);
    const emp = data.employee;

    document.getElementById('modal-emp-db-id').value = emp.id;
    document.getElementById('modal-emp-title').textContent = `Manage: ${emp.full_name}`;
    document.getElementById('modal-emp-name').textContent = emp.full_name;
    document.getElementById('modal-emp-code').textContent = emp.employee_id;
    document.getElementById('modal-emp-pic').src = emp.profile_pic_url || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400';
    
    document.getElementById('modal-first-name').value = emp.first_name;
    document.getElementById('modal-last-name').value = emp.last_name;
    document.getElementById('modal-dept').value = emp.department;
    document.getElementById('modal-desig').value = emp.designation;
    document.getElementById('modal-phone').value = emp.phone;
    document.getElementById('modal-doj').value = emp.date_of_joining;
    document.getElementById('modal-address').value = emp.address;

    document.getElementById('employee-modal').classList.add('active');
  } catch (err) {
    showToast(err.message, 'error');
  }
}

/**
 * Close Modal Dialog
 */
function closeModal(modalId) {
  const el = document.getElementById(modalId);
  if (el) el.classList.remove('active');
}

/**
 * Save Admin Profile Changes
 */
async function saveEmployeeProfileAdmin(event) {
  event.preventDefault();
  const empId = document.getElementById('modal-emp-db-id').value;

  const payload = {
    first_name: document.getElementById('modal-first-name').value.trim(),
    last_name: document.getElementById('modal-last-name').value.trim(),
    department: document.getElementById('modal-dept').value.trim(),
    designation: document.getElementById('modal-desig').value.trim(),
    phone: document.getElementById('modal-phone').value.trim(),
    date_of_joining: document.getElementById('modal-doj').value,
    address: document.getElementById('modal-address').value.trim()
  };

  try {
    await apiFetch(`/employees/${empId}`, {
      method: 'PUT',
      body: JSON.stringify(payload)
    });
    showToast('Employee profile updated successfully!', 'success');
    closeModal('employee-modal');
    loadAdminEmployees();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

/**
 * Load Employee Self Profile
 */
async function loadEmployeeProfile(empDbId) {
  if (!empDbId) return;
  try {
    const data = await apiFetch(`/employees/${empDbId}`);
    const emp = data.employee;

    document.getElementById('self-full-name').textContent = emp.full_name;
    document.getElementById('self-role-dept').textContent = `${emp.designation} • ${emp.department}`;
    document.getElementById('self-emp-id').value = emp.employee_id;
    document.getElementById('self-email').value = emp.email;
    document.getElementById('self-phone').value = emp.phone || '';
    document.getElementById('self-address').value = emp.address || '';
    document.getElementById('self-avatar-url').value = emp.profile_pic_url || '';
    if (emp.profile_pic_url) {
      document.getElementById('self-profile-pic').src = emp.profile_pic_url;
      document.getElementById('emp-avatar').src = emp.profile_pic_url;
    }
  } catch (err) {
    console.error('Failed to load profile:', err);
  }
}

/**
 * Handle Employee Self Profile Update
 */
async function handleEmployeeSelfUpdate(event) {
  event.preventDefault();
  const user = JSON.parse(localStorage.getItem('dayflow_user'));

  const payload = {
    phone: document.getElementById('self-phone').value.trim(),
    address: document.getElementById('self-address').value.trim(),
    profile_pic_url: document.getElementById('self-avatar-url').value.trim()
  };

  try {
    await apiFetch(`/employees/${user.employee_db_id}`, {
      method: 'PUT',
      body: JSON.stringify(payload)
    });
    showToast('Your profile has been updated!', 'success');
    loadEmployeeProfile(user.employee_db_id);
  } catch (err) {
    showToast(err.message, 'error');
  }
}
