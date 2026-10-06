/**
 * GARMENT TRACKER - PRODUCTION MANAGEMENT JAVASCRIPT
 * Handles production stages, stage tabs, progress tracking, and worker assignments.
 */

document.addEventListener('DOMContentLoaded', () => {
  initProductionPage();
});

let activeStageTab = 'All';
let prodFilters = {
  search: '',
  status: 'all'
};

function initProductionPage() {
  // Stage Tab Clicks
  const tabs = document.querySelectorAll('.stage-tab-btn');
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      activeStageTab = tab.getAttribute('data-stage');
      renderProductionTable();
    });
  });

  // Search & Status filters
  const searchInput = document.getElementById('prod-search-input');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      prodFilters.search = e.target.value.toLowerCase().trim();
      renderProductionTable();
    });
  }

  const statusFilter = document.getElementById('prod-filter-status');
  if (statusFilter) {
    statusFilter.addEventListener('change', (e) => {
      prodFilters.status = e.target.value;
      renderProductionTable();
    });
  }

  renderProductionTable();
}

function renderProductionTable() {
  const tbody = document.getElementById('production-table-tbody');
  const countBadge = document.getElementById('prod-count-badge');
  if (!tbody) return;

  const orders = DataStore.getOrders();

  const filtered = orders.filter(o => {
    const matchesTab = activeStageTab === 'All' || o.currentStage.toLowerCase() === activeStageTab.toLowerCase();
    const matchesSearch = !prodFilters.search ||
      o.id.toLowerCase().includes(prodFilters.search) ||
      o.product.toLowerCase().includes(prodFilters.search) ||
      (o.assignedWorker && o.assignedWorker.toLowerCase().includes(prodFilters.search));
    const matchesStatus = prodFilters.status === 'all' || o.status === prodFilters.status;

    return matchesTab && matchesSearch && matchesStatus;
  });

  if (countBadge) countBadge.textContent = `${filtered.length} Items`;

  if (filtered.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="9" style="text-align:center; padding: 40px; color: var(--text-muted);">
          <i class="fa-solid fa-boxes-packing" style="font-size:32px; color: var(--border-color); margin-bottom:10px; display:block;"></i>
          No production orders found matching the selected filter.
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = filtered.map(o => `
    <tr>
      <td>
        <a href="order-details.html?id=${o.id}" class="order-id-link font-bold">${o.id}</a>
      </td>
      <td class="font-medium">${o.product}</td>
      <td class="font-bold">${o.quantity.toLocaleString()}</td>
      <td>
        <span style="display:inline-flex; align-items:center; gap:6px; font-weight:600; color:var(--text-dark);">
          <i class="fa-solid fa-user-gear" style="color:var(--primary-color); font-size:12px;"></i>
          ${o.assignedWorker || 'Unassigned'}
        </span>
      </td>
      <td>${getStageBadge(o.currentStage)}</td>
      <td style="font-size:12px; color:var(--text-muted);">${formatDeadline(o.createdDate)}</td>
      <td style="font-size:12px; color:var(--text-muted);">${formatDeadline(o.deadline)}</td>
      <td style="min-width: 140px;">
        <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:4px;">
          <span style="font-size:11px; font-weight:700; color:var(--text-dark);">${o.progress || 0}%</span>
        </div>
        <div style="height:6px; background:#e2e8f0; border-radius:9999px; overflow:hidden;">
          <div style="width:${o.progress || 0}%; height:100%; background:var(--primary-color); border-radius:9999px;"></div>
        </div>
      </td>
      <td>${getStatusBadge(o.status)}</td>
      <td>
        <button class="btn btn-outline-primary btn-sm" onclick="openUpdateStageModal('${o.id}')">
          <i class="fa-solid fa-sliders"></i> Update
        </button>
      </td>
    </tr>
  `).join('');
}

function openUpdateStageModal(orderId) {
  const order = DataStore.getOrderById(orderId);
  if (!order) return;

  const existing = document.getElementById('update-stage-modal');
  if (existing) existing.remove();

  const stages = ['Cutting', 'Stitching', 'Finishing', 'Quality Check', 'Packaging', 'Dispatch'];
  const stageOptions = stages.map(st => `<option value="${st}" ${order.currentStage === st ? 'selected' : ''}>${st}</option>`).join('');

  const modalHtml = `
    <div id="update-stage-modal" class="modal-overlay active">
      <div class="modal-container">
        <div class="modal-header">
          <h3 class="modal-title">Update Production Stage: ${order.id}</h3>
          <button class="modal-close-btn" onclick="document.getElementById('update-stage-modal').remove()"><i class="fa-solid fa-xmark"></i></button>
        </div>
        <div class="modal-body">
          <form id="update-prod-form">
            <div class="form-grid">
              <div class="form-group">
                <label class="form-label">Current Stage</label>
                <select class="form-control" id="upd-stage" required>
                  ${stageOptions}
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">Production Status</label>
                <select class="form-control" id="upd-status" required>
                  <option value="In Progress" ${order.status === 'In Progress' ? 'selected' : ''}>In Progress</option>
                  <option value="Completed" ${order.status === 'Completed' ? 'selected' : ''}>Completed</option>
                  <option value="Pending" ${order.status === 'Pending' ? 'selected' : ''}>Pending</option>
                  <option value="Delayed" ${order.status === 'Delayed' ? 'selected' : ''}>Delayed</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">Progress Percentage (%)</label>
                <input type="number" min="0" max="100" class="form-control" id="upd-progress" value="${order.progress || 50}" required>
              </div>
              <div class="form-group">
                <label class="form-label">Assigned Lead / Worker</label>
                <input type="text" class="form-control" id="upd-worker" value="${order.assignedWorker || ''}" placeholder="e.g. Rahim Uddin">
              </div>
              <div class="form-group col-span-2">
                <label class="form-label">Stage Update Notes / Remarks</label>
                <textarea class="form-control" id="upd-notes" placeholder="Enter log details for this stage transition..."></textarea>
              </div>
            </div>
            <div class="modal-footer" style="margin: 0 -24px -24px -24px;">
              <button type="button" class="btn btn-secondary btn-sm" onclick="document.getElementById('update-stage-modal').remove()">Cancel</button>
              <button type="submit" class="btn btn-primary btn-sm">Save & Update</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  `;

  document.body.insertAdjacentHTML('beforeend', modalHtml);

  document.getElementById('update-prod-form').addEventListener('submit', (e) => {
    e.preventDefault();
    const newStage = document.getElementById('upd-stage').value;
    const newStatus = document.getElementById('upd-status').value;
    const newProgress = parseInt(document.getElementById('upd-progress').value, 10);
    const newWorker = document.getElementById('upd-worker').value;
    const notes = document.getElementById('upd-notes').value;

    order.currentStage = newStage;
    order.status = newStatus;
    order.progress = newProgress;
    order.assignedWorker = newWorker;

    // Log to history
    order.history.push({
      stage: newStage,
      date: new Date().toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }),
      user: 'Production Supervisor',
      status: newStatus,
      note: notes || `Moved to ${newStage} (${newStatus})`
    });

    DataStore.updateOrder(order);
    document.getElementById('update-stage-modal').remove();
    showToast(`Order ${order.id} stage updated to ${newStage}`, 'success');
    renderProductionTable();
  });
}
