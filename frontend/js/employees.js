/**
 * GARMENT TRACKER - EMPLOYEES JAVASCRIPT
 * Handles employee directory, assignments, status toggling, and add employee modal.
 */

document.addEventListener('DOMContentLoaded', () => {
  initEmployeesPage();
});

let empFilters = {
  search: '',
  department: 'all',
  status: 'all'
};

function initEmployeesPage() {
  const searchInput = document.getElementById('emp-search-input');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      empFilters.search = e.target.value.toLowerCase().trim();
      renderEmployeesTable();
    });
  }

  const deptFilter = document.getElementById('emp-filter-dept');
  if (deptFilter) {
    deptFilter.addEventListener('change', (e) => {
      empFilters.department = e.target.value;
      renderEmployeesTable();
    });
  }

  const statusFilter = document.getElementById('emp-filter-status');
  if (statusFilter) {
    statusFilter.addEventListener('change', (e) => {
      empFilters.status = e.target.value;
      renderEmployeesTable();
    });
  }

  const addBtn = document.getElementById('btn-add-employee');
  if (addBtn) {
    addBtn.addEventListener('click', openAddEmployeeModal);
  }

  renderEmployeesTable();
}

function renderEmployeesTable() {
  const tbody = document.getElementById('employees-table-tbody');
  const countBadge = document.getElementById('emp-count-badge');
  if (!tbody) return;

  const employees = DataStore.getEmployees();

  const filtered = employees.filter(emp => {
    const matchesSearch = !empFilters.search ||
      emp.id.toLowerCase().includes(empFilters.search) ||
      emp.name.toLowerCase().includes(empFilters.search) ||
      emp.role.toLowerCase().includes(empFilters.search);
    const matchesDept = empFilters.department === 'all' || emp.department === empFilters.department;
    const matchesStatus = empFilters.status === 'all' || emp.status === empFilters.status;

    return matchesSearch && matchesDept && matchesStatus;
  });

  if (countBadge) countBadge.textContent = `${filtered.length} Staff`;

  tbody.innerHTML = filtered.map(emp => `
    <tr>
      <td class="font-bold">${emp.id}</td>
      <td>
        <div style="display:flex; align-items:center; gap:10px;">
          <div style="width:32px; height:32px; border-radius:50%; background:#f1f5f9; display:flex; align-items:center; justify-content:center; font-weight:700; color:var(--primary-color); font-size:12px;">
            ${emp.name.split(' ').map(n=>n[0]).join('')}
          </div>
          <div>
            <div class="font-bold" style="font-size:13.5px;">${emp.name}</div>
          </div>
        </div>
      </td>
      <td><span class="badge" style="background:#f1f5f9; color:var(--text-dark);">${emp.department}</span></td>
      <td class="font-medium">${emp.role}</td>
      <td class="font-bold" style="text-align:center;">${emp.assignedOrders}</td>
      <td style="font-size:12.5px; color:var(--text-body); max-width:180px;">${emp.currentTask}</td>
      <td>
        <div style="display:flex; align-items:center; gap:8px;">
          <span style="font-weight:700; font-size:12.5px; color:var(--text-dark);">${emp.performance}%</span>
          <div style="width:50px; height:5px; background:#e2e8f0; border-radius:9999px; overflow:hidden;">
            <div style="width:${emp.performance}%; height:100%; background:var(--success-color);"></div>
          </div>
        </div>
      </td>
      <td>${getStatusBadge(emp.status)}</td>
      <td>
        <div class="table-actions">
          <a href="assign-worker.html?worker=${encodeURIComponent(emp.name)}" class="action-btn" title="Assign Order/Task">
            <i class="fa-solid fa-user-plus"></i>
          </a>
          <button class="action-btn" title="Toggle Status" onclick="toggleEmployeeStatus('${emp.id}')">
            <i class="fa-solid fa-repeat"></i>
          </button>
        </div>
      </td>
    </tr>
  `).join('');
}

function toggleEmployeeStatus(empId) {
  const employees = DataStore.getEmployees();
  const emp = employees.find(e => e.id === empId);
  if (!emp) return;

  const statusCycle = {
    'Available': 'Working',
    'Working': 'On Leave',
    'On Leave': 'Available'
  };

  emp.status = statusCycle[emp.status] || 'Available';
  DataStore.saveEmployees(employees);
  showToast(`${emp.name} status updated to ${emp.status}`, 'info');
  renderEmployeesTable();
}

function openAddEmployeeModal() {
  const existing = document.getElementById('add-employee-modal');
  if (existing) existing.remove();

  const nextId = 'EMP' + (100 + DataStore.getEmployees().length + 1);

  const modalHtml = `
    <div id="add-employee-modal" class="modal-overlay active">
      <div class="modal-container">
        <div class="modal-header">
          <h3 class="modal-title">Add New Factory Employee</h3>
          <button class="modal-close-btn" onclick="document.getElementById('add-employee-modal').remove()"><i class="fa-solid fa-xmark"></i></button>
        </div>
        <div class="modal-body">
          <form id="new-employee-form">
            <div class="form-grid">
              <div class="form-group">
                <label class="form-label">Employee ID</label>
                <input type="text" class="form-control" id="new-emp-id" value="${nextId}" readonly>
              </div>
              <div class="form-group">
                <label class="form-label">Full Name <span class="required">*</span></label>
                <input type="text" class="form-control" id="new-emp-name" placeholder="e.g. Mohammad Ali" required>
              </div>
              <div class="form-group">
                <label class="form-label">Department</label>
                <select class="form-control" id="new-emp-dept">
                  <option value="Production">Production</option>
                  <option value="Cutting">Cutting</option>
                  <option value="Finishing">Finishing</option>
                  <option value="Quality Control">Quality Control</option>
                  <option value="Packaging">Packaging</option>
                  <option value="Logistics">Logistics</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">Designation / Role <span class="required">*</span></label>
                <input type="text" class="form-control" id="new-emp-role" placeholder="e.g. Senior Machine Operator" required>
              </div>
              <div class="form-group">
                <label class="form-label">Initial Status</label>
                <select class="form-control" id="new-emp-status">
                  <option value="Available">Available</option>
                  <option value="Working">Working</option>
                  <option value="On Leave">On Leave</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">Current Task / Assignment</label>
                <input type="text" class="form-control" id="new-emp-task" placeholder="e.g. Sewing Line 4 Supervisor">
              </div>
            </div>
            <div class="modal-footer" style="margin: 0 -24px -24px -24px;">
              <button type="button" class="btn btn-secondary btn-sm" onclick="document.getElementById('add-employee-modal').remove()">Cancel</button>
              <button type="submit" class="btn btn-primary btn-sm">Save Employee</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  `;

  document.body.insertAdjacentHTML('beforeend', modalHtml);

  document.getElementById('new-employee-form').addEventListener('submit', (e) => {
    e.preventDefault();
    const newEmp = {
      id: document.getElementById('new-emp-id').value,
      name: document.getElementById('new-emp-name').value,
      department: document.getElementById('new-emp-dept').value,
      role: document.getElementById('new-emp-role').value,
      assignedOrders: 0,
      currentTask: document.getElementById('new-emp-task').value || 'Unassigned',
      performance: 92,
      status: document.getElementById('new-emp-status').value,
      efficiency: '90%',
      qualityScore: '95%'
    };

    DataStore.addEmployee(newEmp);
    document.getElementById('add-employee-modal').remove();
    showToast(`Employee ${newEmp.name} registered`, 'success');
    renderEmployeesTable();
  });
}
