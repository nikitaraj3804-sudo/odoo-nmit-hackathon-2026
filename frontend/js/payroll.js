/**
 * Dayflow HRMS - Payroll Operations Module
 */

/**
 * Load Read-Only Salary Breakdown (Employee)
 */
async function loadOwnPayroll() {
  const slipBasic = document.getElementById('slip-basic');
  const slipAllowances = document.getElementById('slip-allowances');
  const slipDeductions = document.getElementById('slip-deductions');
  const slipNet = document.getElementById('slip-net');

  if (!slipBasic) return;

  try {
    const data = await apiFetch('/payroll/me');
    const p = data.payroll;

    slipBasic.textContent = `$${p.basic_salary.toLocaleString('en-US', {minimumFractionDigits:2})}`;
    slipAllowances.textContent = `+$${p.allowances.toLocaleString('en-US', {minimumFractionDigits:2})}`;
    slipDeductions.textContent = `-$${p.deductions.toLocaleString('en-US', {minimumFractionDigits:2})}`;
    slipNet.textContent = `$${p.net_salary.toLocaleString('en-US', {minimumFractionDigits:2})}`;
  } catch (err) {
    showToast(`Failed to load salary details: ${err.message}`, 'error');
  }
}

/**
 * Load Admin Payroll Overview Table
 */
async function loadAdminPayroll() {
  const tbody = document.getElementById('admin-payroll-body');
  if (!tbody) return;

  try {
    // Fetch all employees to list their payroll
    const empData = await apiFetch('/employees');
    const employees = empData.employees || [];

    let totalPayrollExpenditure = 0;
    const payrollRows = [];

    for (const emp of employees) {
      try {
        const pRes = await apiFetch(`/payroll/${emp.id}`);
        const p = pRes.payroll;
        totalPayrollExpenditure += p.net_salary;

        payrollRows.push(`
          <tr>
            <td>
              <div style="font-weight:600;">${emp.full_name}</div>
              <div style="font-size:12px; color:var(--text-muted);">${emp.designation} (${emp.employee_id})</div>
            </td>
            <td>
              <input type="number" step="0.01" min="0" class="form-control" id="basic-${emp.id}" value="${p.basic_salary}" style="width:120px; padding:6px 10px;">
            </td>
            <td>
              <input type="number" step="0.01" min="0" class="form-control" id="allow-${emp.id}" value="${p.allowances}" style="width:120px; padding:6px 10px;">
            </td>
            <td>
              <input type="number" step="0.01" min="0" class="form-control" id="ded-${emp.id}" value="${p.deductions}" style="width:120px; padding:6px 10px;">
            </td>
            <td>
              <strong style="color:var(--accent);">$${p.net_salary.toLocaleString('en-US', {minimumFractionDigits:2})}</strong>
            </td>
            <td>
              <button class="btn btn-primary" style="padding:4px 10px; font-size:12px;" onclick="updateEmployeePayroll(${emp.id})">
                Save Structure
              </button>
            </td>
          </tr>
        `);
      } catch (e) {
        console.error(`Error loading payroll for emp ${emp.id}`, e);
      }
    }

    // Update total payroll metric card
    const metricPayroll = document.getElementById('metric-total-payroll');
    if (metricPayroll) {
      metricPayroll.textContent = `$${totalPayrollExpenditure.toLocaleString('en-US', {maximumFractionDigits:0})}`;
    }

    if (!payrollRows.length) {
      tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; color:var(--text-muted);">No payroll data available.</td></tr>`;
      return;
    }

    tbody.innerHTML = payrollRows.join('');

  } catch (err) {
    console.error('Failed to load admin payroll:', err);
  }
}

/**
 * Update Employee Payroll Structure (Admin)
 */
async function updateEmployeePayroll(empId) {
  const basic = parseFloat(document.getElementById(`basic-${empId}`).value) || 0;
  const allowances = parseFloat(document.getElementById(`allow-${empId}`).value) || 0;
  const deductions = parseFloat(document.getElementById(`ded-${empId}`).value) || 0;

  if (basic < 0 || allowances < 0 || deductions < 0) {
    showToast('Salary components cannot be negative numbers.', 'error');
    return;
  }

  try {
    const res = await apiFetch(`/payroll/${empId}`, {
      method: 'PUT',
      body: JSON.stringify({ basic_salary: basic, allowances, deductions })
    });
    showToast('Payroll updated and Net Salary recalculated!', 'success');
    await loadAdminPayroll();
  } catch (err) {
    showToast(err.message, 'error');
  }
}
