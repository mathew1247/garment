/**
 * GARMENT TRACKER - INVENTORY JAVASCRIPT
 * Handles Raw Materials, Work in Progress, and Finished Goods tabs and inventory tracking.
 */

document.addEventListener('DOMContentLoaded', () => {
  initInventoryPage();
});

let currentInvTab = 'all';
let invStatusFilter = 'all';
let allInvCatFilter = 'all';

function initInventoryPage() {
  const urlParams = new URLSearchParams(window.location.search);
  const requestedTab = urlParams.get('tab') || 'all';

  const tabs = document.querySelectorAll('.inv-tab-btn');
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const tabName = tab.getAttribute('data-tab');
      switchInventoryTab(tabName, true);
    });
  });

  const catFilter = document.getElementById('all-inv-cat-filter');
  if (catFilter) {
    catFilter.addEventListener('change', (e) => {
      allInvCatFilter = e.target.value;
      renderAllInventory();
    });
  }

  const filterSelect = document.getElementById('inv-status-filter');
  if (filterSelect) {
    filterSelect.addEventListener('change', (e) => {
      invStatusFilter = e.target.value;
      if (currentInvTab === 'raw') renderRawMaterials();
    });
  }

  const addBtn = document.getElementById('btn-add-material');
  if (addBtn) {
    addBtn.addEventListener('click', openAddMaterialModal);
  }

  switchInventoryTab(requestedTab, false);
}

function switchInventoryTab(tabName, updateUrl = true) {
  currentInvTab = tabName;

  const tabs = document.querySelectorAll('.inv-tab-btn');
  tabs.forEach(t => {
    if (t.getAttribute('data-tab') === tabName) {
      t.classList.add('active');
    } else {
      t.classList.remove('active');
    }
  });

  document.querySelectorAll('.inv-tab-pane').forEach(pane => {
    pane.style.display = 'none';
  });

  const activePane = document.getElementById(`inv-pane-${tabName}`);
  if (activePane) activePane.style.display = 'block';

  if (tabName === 'all') {
    renderAllInventory();
  } else if (tabName === 'raw') {
    renderRawMaterials();
  } else if (tabName === 'wip') {
    renderWIP();
  } else if (tabName === 'finished') {
    renderFinishedGoods();
  }

  if (updateUrl) {
    const newUrl = tabName === 'all' ? 'inventory.html' : `inventory.html?tab=${tabName}`;
    window.history.replaceState({ tab: tabName }, '', newUrl);
  }

  if (window.updateSidebarInventoryTab) {
    window.updateSidebarInventoryTab(tabName);
  }
}

function renderAllInventory() {
  const tbody = document.getElementById('all-inventory-tbody');
  const inventory = DataStore.getInventory();
  const orders = DataStore.getOrders();

  const wipOrders = orders.filter(o => ['Cutting', 'Stitching', 'Finishing'].includes(o.currentStage));
  const finishedOrders = orders.filter(o => ['Packaging', 'Dispatch'].includes(o.currentStage) || o.status === 'Completed');

  // Update Summary KPI Cards
  const rawCountEl = document.getElementById('kpi-raw-count');
  const rawUnitsEl = document.getElementById('kpi-raw-units');
  const wipCountEl = document.getElementById('kpi-wip-count');
  const finishedCountEl = document.getElementById('kpi-finished-count');
  const lowCountEl = document.getElementById('kpi-low-count');

  const totalRawUnits = inventory.reduce((acc, curr) => acc + (Number(curr.quantity) || 0), 0);
  const lowStockItems = inventory.filter(i => i.status === 'Low Stock' || i.status === 'Out of Stock');

  if (rawCountEl) rawCountEl.textContent = `${inventory.length} Items`;
  if (rawUnitsEl) rawUnitsEl.textContent = totalRawUnits.toLocaleString();
  if (wipCountEl) wipCountEl.textContent = `${wipOrders.length} Batches`;
  if (finishedCountEl) finishedCountEl.textContent = `${finishedOrders.length} Batches`;
  if (lowCountEl) lowCountEl.textContent = `${lowStockItems.length} Items`;

  if (!tbody) return;

  // Build Unified Rows
  let masterRows = [];

  // 1. Raw Materials
  if (allInvCatFilter === 'all' || allInvCatFilter === 'Raw Materials') {
    inventory.forEach(item => {
      masterRows.push(`
        <tr>
          <td class="font-bold">${item.id}</td>
          <td class="font-bold" style="color:var(--text-dark);">${item.name}</td>
          <td><span class="badge" style="background:#fff0eb; color:var(--primary-color); font-weight:700;">Raw Material</span></td>
          <td class="font-bold">${Number(item.quantity).toLocaleString()} ${item.unit}</td>
          <td><i class="fa-solid fa-warehouse" style="color:var(--text-light); margin-right:6px;"></i>${item.location || 'Warehouse Floor 1'}</td>
          <td>${getStatusBadge(item.status)}</td>
          <td>
            <button class="btn btn-secondary btn-sm" onclick="adjustStockPrompt('${item.id}')">
              <i class="fa-solid fa-plus-minus"></i> Adjust
            </button>
          </td>
        </tr>
      `);
    });
  }

  // 2. Work in Progress
  if (allInvCatFilter === 'all' || allInvCatFilter === 'WIP') {
    wipOrders.forEach(o => {
      masterRows.push(`
        <tr>
          <td><a href="order-details.html?id=${o.id}" class="order-id-link font-bold">${o.id}</a></td>
          <td class="font-bold" style="color:var(--text-dark);">${o.product}</td>
          <td><span class="badge" style="background:#e0f2fe; color:#0284c7; font-weight:700;">WIP (${o.currentStage})</span></td>
          <td class="font-bold">${Number(o.quantity).toLocaleString()} pcs</td>
          <td><i class="fa-solid fa-industry" style="color:var(--text-light); margin-right:6px;"></i>Production Floor</td>
          <td>${getStatusBadge(o.status)}</td>
          <td>
            <a href="order-details.html?id=${o.id}" class="btn btn-secondary btn-sm">
              <i class="fa-regular fa-eye"></i> View
            </a>
          </td>
        </tr>
      `);
    });
  }

  // 3. Finished Goods
  if (allInvCatFilter === 'all' || allInvCatFilter === 'Finished') {
    finishedOrders.forEach(o => {
      masterRows.push(`
        <tr>
          <td><a href="order-details.html?id=${o.id}" class="order-id-link font-bold">${o.id}</a></td>
          <td class="font-bold" style="color:var(--text-dark);">${o.product}</td>
          <td><span class="badge" style="background:#d1fae5; color:#059669; font-weight:700;">Finished Goods</span></td>
          <td class="font-bold">${Number(o.quantity).toLocaleString()} pcs</td>
          <td><i class="fa-solid fa-boxes-stacked" style="color:var(--text-light); margin-right:6px;"></i>Warehouse Bay B-4</td>
          <td>${getStatusBadge('In Stock')}</td>
          <td>
            <a href="order-details.html?id=${o.id}" class="btn btn-secondary btn-sm">
              <i class="fa-regular fa-eye"></i> View
            </a>
          </td>
        </tr>
      `);
    });
  }

  tbody.innerHTML = masterRows.join('');
}

function renderRawMaterials() {
  const tbody = document.getElementById('raw-materials-tbody');
  if (!tbody) return;

  const inventory = DataStore.getInventory();
  const filtered = inventory.filter(item => {
    return invStatusFilter === 'all' || item.status === invStatusFilter;
  });

  tbody.innerHTML = filtered.map(item => `
    <tr>
      <td class="font-bold">${item.id}</td>
      <td class="font-bold" style="color:var(--text-dark);">${item.name}</td>
      <td><span class="badge" style="background:#f8fafc; color:var(--text-muted);">${item.category}</span></td>
      <td class="font-bold">${item.quantity.toLocaleString()} ${item.unit}</td>
      <td>${item.unit}</td>
      <td class="font-medium">${item.supplier}</td>
      <td>${getStatusBadge(item.status)}</td>
      <td>
        <button class="btn btn-secondary btn-sm" onclick="adjustStockPrompt('${item.id}')">
          <i class="fa-solid fa-plus-minus"></i> Adjust Stock
        </button>
      </td>
    </tr>
  `).join('');
}

function renderWIP() {
  const tbody = document.getElementById('wip-tbody');
  if (!tbody) return;

  const orders = DataStore.getOrders();
  // WIP: orders currently in Cutting, Stitching, Finishing
  const wipOrders = orders.filter(o => ['Cutting', 'Stitching', 'Finishing'].includes(o.currentStage));

  tbody.innerHTML = wipOrders.map(o => `
    <tr>
      <td><a href="order-details.html?id=${o.id}" class="order-id-link font-bold">${o.id}</a></td>
      <td class="font-medium">${o.product}</td>
      <td class="font-bold">${o.quantity.toLocaleString()}</td>
      <td>${getStageBadge(o.currentStage)}</td>
      <td style="min-width: 140px;">
        <div style="font-size:11.5px; font-weight:700; margin-bottom:4px;">${o.progress}%</div>
        <div style="height:6px; background:#e2e8f0; border-radius:9999px; overflow:hidden;">
          <div style="width:${o.progress}%; height:100%; background:var(--primary-color);"></div>
        </div>
      </td>
      <td>${getStatusBadge(o.status)}</td>
    </tr>
  `).join('');
}

function renderFinishedGoods() {
  const tbody = document.getElementById('finished-goods-tbody');
  if (!tbody) return;

  const orders = DataStore.getOrders();
  // Finished goods: orders in Packaging, Dispatch or Completed
  const finished = orders.filter(o => ['Packaging', 'Dispatch'].includes(o.currentStage) || o.status === 'Completed');

  tbody.innerHTML = finished.map(o => `
    <tr>
      <td><a href="order-details.html?id=${o.id}" class="order-id-link font-bold">${o.id}</a></td>
      <td class="font-medium">${o.product}</td>
      <td class="font-bold">${o.quantity.toLocaleString()}</td>
      <td style="font-size:12.5px; color:var(--text-muted);">${formatDeadline(o.deadline)}</td>
      <td class="font-medium"><i class="fa-solid fa-warehouse" style="color:var(--text-light); margin-right:6px;"></i>Warehouse Bay B-4</td>
      <td>${getStatusBadge(o.status === 'Completed' ? 'Completed' : 'In Stock')}</td>
    </tr>
  `).join('');
}

function adjustStockPrompt(matId) {
  const inventory = DataStore.getInventory();
  const item = inventory.find(i => i.id === matId);
  if (!item) return;

  const newQtyStr = prompt(`Update stock count for ${item.name} (${item.unit}):`, item.quantity);
  if (newQtyStr !== null && !isNaN(newQtyStr)) {
    const qty = parseInt(newQtyStr, 10);
    item.quantity = qty;
    if (qty === 0) item.status = 'Out of Stock';
    else if (qty < (item.threshold || 1000)) item.status = 'Low Stock';
    else item.status = 'In Stock';

    DataStore.saveInventory(inventory);
    showToast(`${item.name} stock updated to ${qty} ${item.unit}`, 'success');
    renderRawMaterials();
  }
}

function openAddMaterialModal() {
  const existing = document.getElementById('add-material-modal');
  if (existing) existing.remove();

  const nextId = 'MAT' + String(DataStore.getInventory().length + 1).padStart(3, '0');

  const modalHtml = `
    <div id="add-material-modal" class="modal-overlay active">
      <div class="modal-container">
        <div class="modal-header">
          <h3 class="modal-title">Add Raw Material / Accessory</h3>
          <button class="modal-close-btn" onclick="document.getElementById('add-material-modal').remove()"><i class="fa-solid fa-xmark"></i></button>
        </div>
        <div class="modal-body">
          <form id="new-material-form">
            <div class="form-grid">
              <div class="form-group">
                <label class="form-label">Material ID</label>
                <input type="text" class="form-control" id="new-mat-id" value="${nextId}" readonly>
              </div>
              <div class="form-group">
                <label class="form-label">Material Name <span class="required">*</span></label>
                <input type="text" class="form-control" id="new-mat-name" placeholder="e.g. Cotton Spandex Jersey" required>
              </div>
              <div class="form-group">
                <label class="form-label">Category</label>
                <select class="form-control" id="new-mat-category">
                  <option value="Raw Material">Raw Material</option>
                  <option value="Accessories">Accessories</option>
                  <option value="Trims">Trims</option>
                  <option value="Packaging">Packaging</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">Initial Quantity <span class="required">*</span></label>
                <input type="number" class="form-control" id="new-mat-qty" value="1000" required>
              </div>
              <div class="form-group">
                <label class="form-label">Unit of Measure</label>
                <select class="form-control" id="new-mat-unit">
                  <option value="m">Meters (m)</option>
                  <option value="pcs">Pieces (pcs)</option>
                  <option value="kg">Kilograms (kg)</option>
                  <option value="boxes">Boxes</option>
                  <option value="spools">Spools</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">Supplier Name</label>
                <input type="text" class="form-control" id="new-mat-supplier" placeholder="e.g. Acme Fabric Mills" required>
              </div>
            </div>
            <div class="modal-footer" style="margin: 0 -24px -24px -24px;">
              <button type="button" class="btn btn-secondary btn-sm" onclick="document.getElementById('add-material-modal').remove()">Cancel</button>
              <button type="submit" class="btn btn-primary btn-sm">Save Material</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  `;

  document.body.insertAdjacentHTML('beforeend', modalHtml);

  document.getElementById('new-material-form').addEventListener('submit', (e) => {
    e.preventDefault();
    const qty = parseInt(document.getElementById('new-mat-qty').value, 10);
    const item = {
      id: document.getElementById('new-mat-id').value,
      name: document.getElementById('new-mat-name').value,
      category: document.getElementById('new-mat-category').value,
      quantity: qty,
      unit: document.getElementById('new-mat-unit').value,
      supplier: document.getElementById('new-mat-supplier').value,
      status: qty > 500 ? 'In Stock' : (qty > 0 ? 'Low Stock' : 'Out of Stock'),
      threshold: 500,
      location: 'Warehouse Floor 1'
    };

    const inv = DataStore.getInventory();
    inv.push(item);
    DataStore.saveInventory(inv);

    document.getElementById('add-material-modal').remove();
    showToast(`Material ${item.name} added to inventory`, 'success');
    renderRawMaterials();
  });
}
