/**
 * Dayflow HRMS - Attendance Operations Module
 */

/**
 * Check In Handler (Employee)
 */
async function handleCheckIn() {
  try {
    const res = await apiFetch('/attendance/check-in', { method: 'POST' });
    showToast(res.message, 'success');
    await loadTodayAttendanceStatus();
    await loadEmployeeAttendance();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

/**
 * Check Out Handler (Employee)
 */
async function handleCheckOut() {
  try {
    const res = await apiFetch('/attendance/check-out', { method: 'POST' });
    showToast(res.message, 'success');
    await loadTodayAttendanceStatus();
    await loadEmployeeAttendance();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

/**
 * Load Today's Check-in Status
 */
async function loadTodayAttendanceStatus() {
  const badge = document.getElementById('today-status-badge');
  const btnIn = document.getElementById('btn-checkin');
  const btnOut = document.getElementById('btn-checkout');
  if (!badge) return;

  try {
    const data = await apiFetch('/attendance?view=daily');
    const records = data.attendance || [];
    const todayStr = new Date().toISOString().split('T')[0];
    const todayRec = records.find(r => r.date === todayStr);

    if (!todayRec || !todayRec.check_in) {
      badge.className = 'badge badge-absent';
      badge.textContent = 'Not Checked In Today';
      if (btnIn) btnIn.disabled = false;
      if (btnOut) btnOut.disabled = true;
    } else if (todayRec.check_in && !todayRec.check_out) {
      badge.className = 'badge badge-present';
      badge.textContent = `Checked In (${todayRec.check_in_time})`;
      if (btnIn) btnIn.disabled = true;
      if (btnOut) btnOut.disabled = false;
    } else {
      badge.className = 'badge badge-approved';
      badge.textContent = `Completed Today (${todayRec.check_in_time} - ${todayRec.check_out_time})`;
      if (btnIn) btnIn.disabled = true;
      if (btnOut) btnOut.disabled = true;
    }
  } catch (err) {
    console.error('Error fetching today status:', err);
  }
}

/**
 * Load Employee Attendance History
 */
async function loadEmployeeAttendance() {
  const tbody = document.getElementById('emp-attendance-body');
  if (!tbody) return;

  try {
    const data = await apiFetch('/attendance');
    const list = data.attendance || [];

    // Count present stat
    const presentCount = list.filter(r => r.status === 'Present' || r.status === 'Half-day').length;
    const statPresent = document.getElementById('emp-stat-present');
    if (statPresent) statPresent.textContent = `${presentCount} Days`;

    if (!list.length) {
      tbody.innerHTML = `<tr><td colspan="4" style="text-align:center; color:var(--text-muted);">No attendance records found.</td></tr>`;
      return;
    }

    tbody.innerHTML = list.map(r => `
      <tr>
        <td>${r.date}</td>
        <td>${r.check_in_time || '--:--'}</td>
        <td>${r.check_out_time || '--:--'}</td>
        <td>
          <span class="badge badge-${(r.status || 'absent').toLowerCase()}">${r.status}</span>
        </td>
      </tr>
    `).join('');
  } catch (err) {
    showToast(`Failed to load attendance logs: ${err.message}`, 'error');
  }
}

/**
 * Load Admin Attendance Matrix
 */
async function loadAdminAttendance() {
  const tbody = document.getElementById('admin-attendance-body');
  if (!tbody) return;

  const dateVal = document.getElementById('att-filter-date')?.value || '';
  const empVal = document.getElementById('att-filter-emp')?.value || '';

  let url = '/attendance?';
  if (dateVal) url += `start_date=${dateVal}&end_date=${dateVal}&`;
  if (empVal) url += `employee_id=${empVal}&`;

  try {
    const data = await apiFetch(url);
    const list = data.attendance || [];

    // Metric update
    const todayStr = new Date().toISOString().split('T')[0];
    const presentToday = list.filter(r => r.date === todayStr && (r.status === 'Present' || r.status === 'Half-day')).length;
    const metricPresent = document.getElementById('metric-present-today');
    if (metricPresent) metricPresent.textContent = presentToday;

    if (!list.length) {
      tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; color:var(--text-muted);">No attendance records found.</td></tr>`;
      return;
    }

    tbody.innerHTML = list.map(r => `
      <tr>
        <td>${r.date}</td>
        <td><strong>${r.employee_name}</strong> (${r.employee_code})</td>
        <td>${r.check_in_time || '--:--'}</td>
        <td>${r.check_out_time || '--:--'}</td>
        <td>
          <span class="badge badge-${(r.status || 'absent').toLowerCase()}">${r.status}</span>
        </td>
      </tr>
    `).join('');
  } catch (err) {
    console.error('Failed loading admin attendance:', err);
  }
}

/**
 * Open Mark Attendance Override Modal
 */
function openMarkAttendanceModal() {
  const modal = document.getElementById('mark-att-modal');
  const dateInput = document.getElementById('override-date');
  if (dateInput) dateInput.value = new Date().toISOString().split('T')[0];
  if (modal) modal.classList.add('active');
}

/**
 * Submit Attendance Override Form (Admin)
 */
async function submitMarkAttendance(event) {
  event.preventDefault();
  const employee_id = parseInt(document.getElementById('override-emp-select').value);
  const date = document.getElementById('override-date').value;
  const status = document.getElementById('override-status').value;

  try {
    const res = await apiFetch('/attendance/mark', {
      method: 'POST',
      body: JSON.stringify({ employee_id, date, status })
    });
    showToast(res.message, 'success');
    closeModal('mark-att-modal');
    loadAdminAttendance();
  } catch (err) {
    showToast(err.message, 'error');
  }
}
