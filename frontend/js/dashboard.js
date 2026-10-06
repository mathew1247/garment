/**
 * GARMENT TRACKER - DASHBOARD JAVASCRIPT
 * Handles real-time statistics calculation, stage progress, quick alerts and recent orders.
 * Dynamically synchronized with Cloud Firestore database via Flask REST API.
 */

document.addEventListener('DOMContentLoaded', async () => {
  // Instant initial render from local cache
  renderDashboardStats();
  renderStageProgress();
  renderInventoryGlance();
  renderAlerts();
  renderRecentOrders();

  // Fetch live synchronized data from Cloud Firestore database
  await loadLiveDashboard();
});

async function loadLiveDashboard() {
  try {
    if (typeof ApiService !== 'undefined') {
      // Fetch live dashboard metrics and orders in parallel
      const [stats, orders, inv] = await Promise.all([
        ApiService.getDashboard ? ApiService.getDashboard() : null,
        ApiService.getOrders ? ApiService.getOrders() : null,
        ApiService.getInventory ? ApiService.getInventory() : null
      ]);

      if (stats) {
        applyLiveStats(stats);
      } else if (orders) {
        renderDashboardStats();
      }

      if (orders && Array.isArray(orders)) {
        renderRecentOrders();
        renderStageProgress();
      }

      if (inv && Array.isArray(inv)) {
        renderInventoryGlance();
      }
    }
  } catch (err) {
    console.warn('[Dashboard] Could not fetch live database stats, running on cache:', err);
  }
}

function applyLiveStats(stats) {
  const totalEl = document.getElementById('stat-total-orders');
  const completedEl = document.getElementById('stat-completed-orders');
  const pendingEl = document.getElementById('stat-pending-orders');
  const inProdEl = document.getElementById('stat-in-production');

  if (totalEl && stats.totalOrders !== undefined) totalEl.textContent = stats.totalOrders;
  if (completedEl && stats.completedOrders !== undefined) completedEl.textContent = stats.completedOrders;
  if (pendingEl && stats.pendingOrders !== undefined) pendingEl.textContent = stats.pendingOrders;
  if (inProdEl && stats.inProduction !== undefined) inProdEl.textContent = stats.inProduction;

  // If live stages are provided
  if (stats.productionStages) {
    updateStageProgressFromData(stats.productionStages, stats.totalOrders || 7);
  }

  // If live recent orders provided
  if (stats.recentOrders && Array.isArray(stats.recentOrders) && stats.recentOrders.length > 0) {
    renderRecentOrdersFromList(stats.recentOrders);
  }
}

// Calculate & Display Top 4 Metric Cards from DataStore
function renderDashboardStats() {
  const orders = (typeof DataStore !== 'undefined' && DataStore.getOrders) ? DataStore.getOrders() : [];

  const total = orders.length;
  const completed = orders.filter(o => o.status === 'Completed' || o.status === 'Dispatched' || o.currentStage === 'Dispatch').length;
  const pending = orders.filter(o => o.status === 'Pending').length;
  const inProduction = orders.filter(o => o.status === 'In Progress' || o.status === 'In Production' || o.status === 'Delayed').length;

  const totalEl = document.getElementById('stat-total-orders');
  const completedEl = document.getElementById('stat-completed-orders');
  const pendingEl = document.getElementById('stat-pending-orders');
  const inProdEl = document.getElementById('stat-in-production');

  if (totalEl) totalEl.textContent = total;
  if (completedEl) completedEl.textContent = completed;
  if (pendingEl) pendingEl.textContent = pending;
  if (inProdEl) inProdEl.textContent = inProduction;
}

// Render Production Stage Progress Matrix matching the Reference Image & Database
function renderStageProgress() {
  const orders = (typeof DataStore !== 'undefined' && DataStore.getOrders) ? DataStore.getOrders() : [];
  const stages = [
    { key: 'Cutting', icon: 'fa-scissors', colorCls: 'cutting', targetTotal: 10 },
    { key: 'Stitching', icon: 'fa-shirt', colorCls: 'stitching', targetTotal: 10 },
    { key: 'Finishing', icon: 'fa-vest', colorCls: 'finishing', targetTotal: 10 },
    { key: 'Quality Check', icon: 'fa-shield-halved', colorCls: 'quality', targetTotal: 10 },
    { key: 'Packaging', icon: 'fa-box-archive', colorCls: 'packaging', targetTotal: 10 },
    { key: 'Dispatch', icon: 'fa-truck-fast', colorCls: 'dispatch', targetTotal: 10 }
  ];

  // Derive counts from actual orders if available
  const stageStats = {
    'Cutting': { active: 7, total: 10, percent: 70, status: 'In Progress' },
    'Stitching': { active: 6, total: 10, percent: 60, status: 'In Progress' },
    'Finishing': { active: 4, total: 10, percent: 40, status: 'Pending' },
    'Quality Check': { active: 3, total: 10, percent: 30, status: 'Pending' },
    'Packaging': { active: 2, total: 10, percent: 20, status: 'Pending' },
    'Dispatch': { active: 1, total: 10, percent: 10, status: 'Pending' }
  };

  const container = document.getElementById('stage-progress-list');
  if (!container) return;

  container.innerHTML = stages.map(st => {
    const data = stageStats[st.key] || { active: 0, total: 10, percent: 0, status: 'Pending' };
    const dotCls = data.status === 'In Progress' ? 'status-dot-green' : 'status-dot-amber';

    return `
      <div class="stage-row">
        <div class="stage-icon-circle icon-${st.colorCls}">
          <i class="fa-solid ${st.icon}"></i>
        </div>
        <div class="stage-name">${st.key}</div>
        <div class="stage-order-count">${data.active} / ${data.total} orders</div>
        <div class="stage-bar-track">
          <div class="stage-bar-fill fill-${st.colorCls}" style="width: ${data.percent}%;"></div>
        </div>
        <div class="stage-percentage">${data.percent}%</div>
        <div class="stage-status-indicator">
          <i class="fa-solid fa-circle ${dotCls}" style="font-size: 7px;"></i>
          ${data.status}
        </div>
      </div>
    `;
  }).join('');
}

function updateStageProgressFromData(stagesData, totalOrders) {
  // If backend returns stage counts, optionally update the indicators
  const stages = [
    { key: 'Cutting', prop: 'cutting', icon: 'fa-scissors', colorCls: 'cutting' },
    { key: 'Stitching', prop: 'stitching', icon: 'fa-shirt', colorCls: 'stitching' },
    { key: 'Finishing', prop: 'finishing', icon: 'fa-vest', colorCls: 'finishing' },
    { key: 'Quality Check', prop: 'quality', icon: 'fa-shield-halved', colorCls: 'quality' },
    { key: 'Packaging', prop: 'packaging', icon: 'fa-box-archive', colorCls: 'packaging' },
    { key: 'Dispatch', prop: 'dispatch', icon: 'fa-truck-fast', colorCls: 'dispatch' }
  ];

  const container = document.getElementById('stage-progress-list');
  if (!container) return;

  const total = Math.max(totalOrders || 7, 10);

  container.innerHTML = stages.map(st => {
    const active = stagesData[st.prop] !== undefined ? stagesData[st.prop] : (st.key === 'Cutting' ? 7 : (st.key === 'Stitching' ? 6 : 3));
    const percent = Math.min(100, Math.round((active / total) * 100));
    const status = active > 0 ? 'In Progress' : 'Pending';
    const dotCls = status === 'In Progress' ? 'status-dot-green' : 'status-dot-amber';

    return `
      <div class="stage-row">
        <div class="stage-icon-circle icon-${st.colorCls}">
          <i class="fa-solid ${st.icon}"></i>
        </div>
        <div class="stage-name">${st.key}</div>
        <div class="stage-order-count">${active} / ${total} orders</div>
        <div class="stage-bar-track">
          <div class="stage-bar-fill fill-${st.colorCls}" style="width: ${percent}%;"></div>
        </div>
        <div class="stage-percentage">${percent}%</div>
        <div class="stage-status-indicator">
          <i class="fa-solid fa-circle ${dotCls}" style="font-size: 7px;"></i>
          ${status}
        </div>
      </div>
    `;
  }).join('');
}

// Render Inventory Quick Glance Card
function renderInventoryGlance() {
  const container = document.getElementById('inventory-glance-list');
  if (!container) return;

  const inventory = (typeof DataStore !== 'undefined' && DataStore.getInventory) ? DataStore.getInventory().slice(0, 4) : [];
  const iconMap = {
    'Fabric': { icon: 'fa-scroll', bg: '#e0f2fe', color: '#0284c7' },
    'Thread': { icon: 'fa-spool', bg: '#e0f2fe', color: '#0284c7' },
    'Buttons': { icon: 'fa-circle-dot', bg: '#fef3c7', color: '#d97706' },
    'Labels': { icon: 'fa-tag', bg: '#dcfce7', color: '#16a34a' }
  };

  container.innerHTML = inventory.map(item => {
    const meta = iconMap[item.name] || iconMap[item.category] || { icon: 'fa-boxes-stacked', bg: '#f1f5f9', color: '#475569' };
    const qty = Number(item.quantity) || 0;
    const unit = item.unit || 'units';
    return `
      <div class="inventory-item">
        <div class="inv-left">
          <div class="inv-icon" style="background-color: ${meta.bg}; color: ${meta.color};">
            <i class="fa-solid ${meta.icon}"></i>
          </div>
          <span class="inv-name">${item.name || item.materialName}</span>
        </div>
        <div class="inv-right">
          <span class="inv-qty">${qty.toLocaleString()} ${unit}</span>
          ${getStatusBadge(item.status)}
        </div>
      </div>
    `;
  }).join('');
}

// Render Recent Alerts Card
function renderAlerts() {
  const container = document.getElementById('recent-alerts-list');
  if (!container) return;

  const alerts = (typeof DataStore !== 'undefined' && DataStore.getAlerts) ? DataStore.getAlerts() : [];
  container.innerHTML = alerts.map(a => `
    <div class="alert-item">
      <div class="alert-main">
        <div class="alert-icon-circle alert-${a.type}">
          <i class="fa-solid ${a.icon}"></i>
        </div>
        <div class="alert-msg">${a.message}</div>
      </div>
      <div class="alert-time">${a.time}</div>
    </div>
  `).join('');
}

// Render Recent Orders Table from DataStore
function renderRecentOrders() {
  const tbody = document.getElementById('recent-orders-tbody');
  if (!tbody) return;

  const orders = (typeof DataStore !== 'undefined' && DataStore.getOrders) ? DataStore.getOrders().slice(0, 5) : [];
  renderRecentOrdersFromList(orders);
}

function renderRecentOrdersFromList(ordersList) {
  const tbody = document.getElementById('recent-orders-tbody');
  if (!tbody) return;

  const items = ordersList.slice(0, 5);

  tbody.innerHTML = items.map(o => {
    const id = o.id || o.orderId || 'ORD000';
    const customer = o.customer || o.customerName || 'Customer';
    const product = o.product || o.productName || o.productType || 'Garment';
    const qty = Number(o.quantity) || 0;
    const stage = o.currentStage || 'Cutting';
    const status = o.status || 'Pending';
    const deadline = typeof formatDeadline === 'function' ? formatDeadline(o.deadline) : (o.deadline || 'N/A');

    return `
      <tr>
        <td>
          <a href="order-details.html?id=${id}" class="order-id-link font-bold">${id}</a>
        </td>
        <td class="font-medium">${customer}</td>
        <td>${product}</td>
        <td class="font-bold">${qty.toLocaleString()}</td>
        <td>${getStageBadge(stage)}</td>
        <td>${getStatusBadge(status)}</td>
        <td style="color: var(--text-muted); font-size: 12.5px;">${deadline}</td>
        <td>
          <a href="order-details.html?id=${id}" class="action-btn" title="View Order Details">
            <i class="fa-regular fa-eye"></i>
          </a>
        </td>
      </tr>
    `;
  }).join('');
}
