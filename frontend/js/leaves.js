/**
 * Dayflow HRMS - Leave Management Module
 */

let currentLeaveFilter = '';

/**
 * Handle Apply for Leave (Employee)
 */
async function handleApplyLeave(event) {
  event.preventDefault();
  const leave_type = document.getElementById('leave-type').value;
  const start_date = document.getElementById('leave-start').value;
  const end_date = document.getElementById('leave-end').value;
  const remarks = document.getElementById('leave-remarks').value.trim();

  if (new Date(end_date) < new Date(start_date)) {
    showToast('End date cannot be earlier than start date.', 'error');
    return;
  }

  try {
    const res = await apiFetch('/leaves', {
      method: 'POST',
      body: JSON.stringify({ leave_type, start_date, end_date, remarks })
    });
    showToast('Leave request submitted successfully!', 'success');
    event.target.reset();
    await loadEmployeeLeaves();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

/**
 * Load Employee Leave History
 */
async function loadEmployeeLeaves() {
  const tbody = document.getElementById('emp-leaves-body');
  if (!tbody) return;

  try {
    const data = await apiFetch('/leaves');
    const list = data.leaves || [];

    // Metric counters
    const approvedCount = list.filter(l => l.status === 'Approved').reduce((acc, l) => acc + l.total_days, 0);
    const pendingCount = list.filter(l => l.status === 'Pending').length;

    const statLeaves = document.getElementById('emp-stat-leaves');
    const statPending = document.getElementById('emp-stat-pending');

    if (statLeaves) statLeaves.textContent = `${approvedCount} Days`;
    if (statPending) statPending.textContent = `${pendingCount} Pending`;

    if (!list.length) {
      tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; color:var(--text-muted);">No leave applications found.</td></tr>`;
      return;
    }

    tbody.innerHTML = list.map(l => `
      <tr>
        <td><span class="badge badge-leave">${l.leave_type}</span></td>
        <td>${l.start_date} to ${l.end_date}</td>
        <td>${l.total_days} Day(s)</td>
        <td><span class="badge badge-${l.status.toLowerCase()}">${l.status}</span></td>
        <td>${l.admin_comment || '--'}</td>
      </tr>
    `).join('');

  } catch (err) {
    showToast(`Failed to load leave history: ${err.message}`, 'error');
  }
}

/**
 * Load Admin Leave Queue
 */
async function loadAdminLeaves() {
  const tbody = document.getElementById('admin-leaves-body');
  if (!tbody) return;

  let url = '/leaves?';
  if (currentLeaveFilter) url += `status=${currentLeaveFilter}`;

  try {
    const data = await apiFetch(url);
    const list = data.leaves || [];

    // Metric update
    const pendingItems = list.filter(l => l.status === 'Pending').length;
    const metricPending = document.getElementById('metric-pending-leaves');
    const badgePending = document.getElementById('pending-count-badge');

    if (metricPending) metricPending.textContent = pendingItems;
    if (badgePending) {
      badgePending.textContent = pendingItems;
      badgePending.style.display = pendingItems > 0 ? 'inline-flex' : 'none';
    }

    if (!list.length) {
      tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; color:var(--text-muted);">No leave applications match filter.</td></tr>`;
      return;
    }

    tbody.innerHTML = list.map(l => `
      <tr>
        <td>
          <div style="font-weight:600;">${l.employee_name}</div>
          <div style="font-size:12px; color:var(--text-muted);">${l.department} (${l.employee_code})</div>
        </td>
        <td><span class="badge badge-leave">${l.leave_type}</span></td>
        <td>${l.start_date} → ${l.end_date}</td>
        <td>${l.total_days} Day(s)</td>
        <td>${l.remarks || 'N/A'}</td>
        <td><span class="badge badge-${l.status.toLowerCase()}">${l.status}</span></td>
        <td>
          ${l.status === 'Pending' ? `
            <div style="display:flex; gap:6px;">
              <button class="btn btn-success" style="padding:4px 8px; font-size:12px;" onclick="approveOrRejectLeave(${l.id}, 'Approved')">Approve</button>
              <button class="btn btn-danger" style="padding:4px 8px; font-size:12px;" onclick="approveOrRejectLeave(${l.id}, 'Rejected')">Reject</button>
            </div>
          ` : `<span style="font-size:12px; color:var(--text-muted);">${l.admin_comment || 'Processed'}</span>`}
        </td>
      </tr>
    `).join('');

  } catch (err) {
    console.error('Failed to load admin leaves:', err);
  }
}

/**
 * Filter Leave Status Queue
 */
function filterLeaveStatus(status) {
  currentLeaveFilter = status;
  loadAdminLeaves();
}

/**
 * Approve or Reject Leave Request (Admin)
 */
async function approveOrRejectLeave(leaveId, status) {
  const admin_comment = prompt(`Enter optional comment for setting leave status to ${status}:`) || '';

  try {
    const res = await apiFetch(`/leaves/${leaveId}/approve`, {
      method: 'PUT',
      body: JSON.stringify({ status, admin_comment })
    });
    showToast(res.message, 'success');
    await loadAdminLeaves();
    await loadAdminAttendance(); // Sync attendance table UI
  } catch (err) {
    showToast(err.message, 'error');
  }
}
