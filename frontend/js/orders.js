/**
 * GARMENT TRACKER - ORDERS MANAGEMENT JAVASCRIPT
 * Handles orders table filtering, live search, deletion, and status changes.
 */

document.addEventListener('DOMContentLoaded', () => {
  initOrdersPage();
});

let currentFilters = {
  search: '',
  status: 'all',
  customer: 'all',
  product: 'all'
};

async function initOrdersPage() {
  // Check URL parameters for search query
  const urlParams = new URLSearchParams(window.location.search);
  const searchParam = urlParams.get('search');
  if (searchParam) {
    currentFilters.search = searchParam;
    const searchInput = document.getElementById('orders-search-input');
    if (searchInput) searchInput.value = searchParam;
  }

  // Bind filter events
  const searchInput = document.getElementById('orders-search-input');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      currentFilters.search = e.target.value.toLowerCase().trim();
      renderOrdersTable();
    });
  }

  const statusFilter = document.getElementById('filter-status');
  if (statusFilter) {
    statusFilter.addEventListener('change', (e) => {
      currentFilters.status = e.target.value;
      renderOrdersTable();
    });
  }

  const customerFilter = document.getElementById('filter-customer');
  if (customerFilter) {
    populateCustomerDropdown(customerFilter);
    customerFilter.addEventListener('change', (e) => {
      currentFilters.customer = e.target.value;
      renderOrdersTable();
    });
  }

  const productFilter = document.getElementById('filter-product');
  if (productFilter) {
    productFilter.addEventListener('change', (e) => {
      currentFilters.product = e.target.value;
      renderOrdersTable();
    });
  }

  // Initial fast render from local store
  renderOrdersTable();

  // Fetch live orders from real Cloud Firestore database
  await loadLiveOrders();
}

async function loadLiveOrders() {
  try {
    if (typeof ApiService !== 'undefined' && ApiService.getOrders) {
      const liveOrders = await ApiService.getOrders();
      if (liveOrders && Array.isArray(liveOrders)) {
        const customerFilter = document.getElementById('filter-customer');
        if (customerFilter) {
          populateCustomerDropdown(customerFilter);
        }
        renderOrdersTable();
      }
    }
  } catch (err) {
    console.warn('Failed loading live orders from database, keeping cache:', err);
  }
}

function populateCustomerDropdown(selectEl) {
  const orders = DataStore.getOrders();
  const customers = Array.from(new Set(orders.map(o => o.customer || o.customerName || 'Customer')));
  // Reset options to 'All Customers'
  selectEl.innerHTML = '<option value="all">All Customers</option>';
  customers.forEach(cust => {
    if (!cust) return;
    const opt = document.createElement('option');
    opt.value = cust;
    opt.textContent = cust;
    selectEl.appendChild(opt);
  });
}

function renderOrdersTable() {
  const tbody = document.getElementById('orders-table-tbody');
  const countEl = document.getElementById('orders-count-badge');
  const emptyState = document.getElementById('orders-empty-state');
  if (!tbody) return;

  const orders = DataStore.getOrders();

  const filtered = orders.filter(order => {
    const id = String(order.id || order.orderId || '').toLowerCase();
    const cust = String(order.customer || order.customerName || '').toLowerCase();
    const prod = String(order.product || order.productName || order.productType || '').toLowerCase();
    const status = String(order.status || 'Pending');

    const matchesSearch = !currentFilters.search ||
      id.includes(currentFilters.search) ||
      cust.includes(currentFilters.search) ||
      prod.includes(currentFilters.search);

    const matchesStatus = currentFilters.status === 'all' || status.toLowerCase() === currentFilters.status.toLowerCase();
    const matchesCustomer = currentFilters.customer === 'all' || cust.toLowerCase() === currentFilters.customer.toLowerCase();
    const matchesProduct = currentFilters.product === 'all' || prod.toLowerCase() === currentFilters.product.toLowerCase();

    return matchesSearch && matchesStatus && matchesCustomer && matchesProduct;
  });

  if (countEl) countEl.textContent = `${filtered.length} Orders`;

  if (filtered.length === 0) {
    tbody.innerHTML = '';
    if (emptyState) emptyState.style.display = 'block';
    return;
  }

  if (emptyState) emptyState.style.display = 'none';

  tbody.innerHTML = filtered.map(o => {
    const orderId = o.id || o.orderId || 'ORD000';
    const customer = o.customer || o.customerName || 'Customer';
    const product = o.product || o.productName || o.productType || 'Garment';
    const qty = Number(o.quantity) || 0;
    const stage = o.currentStage || 'Cutting';
    const status = o.status || 'Pending';
    const formattedDeadline = typeof formatDeadline === 'function' ? formatDeadline(o.deadline) : (o.deadline || 'N/A');

    return `
      <tr>
        <td>
          <a href="order-details.html?id=${orderId}" class="order-id-link font-bold">${orderId}</a>
        </td>
        <td class="font-medium">${customer}</td>
        <td>
          <span style="display:inline-flex; align-items:center; gap:6px;">
            <i class="fa-solid fa-shirt" style="color:var(--text-light); font-size:12px;"></i>
            ${product}
          </span>
        </td>
        <td class="font-bold">${qty.toLocaleString()}</td>
        <td style="color: var(--text-muted); font-size: 12.5px;">${formattedDeadline}</td>
        <td>${getStageBadge(stage)}</td>
        <td>${getStatusBadge(status)}</td>
        <td>
          <div class="table-actions">
            <a href="order-details.html?id=${orderId}" class="action-btn" title="View Order">
              <i class="fa-regular fa-eye"></i>
            </a>
            <button class="action-btn" title="Edit Order" onclick="openEditOrderModal('${orderId}')">
              <i class="fa-regular fa-pen-to-square"></i>
            </button>
            <button class="action-btn btn-delete" title="Delete Order" onclick="handleDeleteOrder('${orderId}')">
              <i class="fa-regular fa-trash-can"></i>
            </button>
          </div>
        </td>
      </tr>
    `;
  }).join('');
}

function handleDeleteOrder(orderId) {
  showConfirmDialog('Delete Order', `Are you sure you want to delete order <strong>${orderId}</strong>? This action cannot be undone.`, async () => {
    if (typeof ApiService !== 'undefined' && ApiService.deleteOrder) {
      await ApiService.deleteOrder(orderId);
    }
    DataStore.deleteOrder(orderId);
    showToast(`Order ${orderId} deleted successfully`, 'success');
    renderOrdersTable();
  });
}

function openEditOrderModal(orderId) {
  const order = DataStore.getOrderById(orderId);
  if (!order) return;

  const existingModal = document.getElementById('edit-order-modal');
  if (existingModal) existingModal.remove();

  const modalHtml = `
    <div id="edit-order-modal" class="modal-overlay active">
      <div class="modal-container">
        <div class="modal-header">
          <h3 class="modal-title">Edit Order ${order.id}</h3>
          <button class="modal-close-btn" onclick="document.getElementById('edit-order-modal').remove()"><i class="fa-solid fa-xmark"></i></button>
        </div>
        <div class="modal-body">
          <form id="edit-order-form">
            <div class="form-grid">
              <div class="form-group">
                <label class="form-label">Customer Name</label>
                <input type="text" class="form-control" id="edit-order-customer" value="${order.customer}" required>
              </div>
              <div class="form-group">
                <label class="form-label">Product Type</label>
                <select class="form-control" id="edit-order-product">
                  <option value="T-Shirt" ${order.product === 'T-Shirt' ? 'selected' : ''}>T-Shirt</option>
                  <option value="Shirt" ${order.product === 'Shirt' ? 'selected' : ''}>Shirt</option>
                  <option value="Jacket" ${order.product === 'Jacket' ? 'selected' : ''}>Jacket</option>
                  <option value="Pants" ${order.product === 'Pants' ? 'selected' : ''}>Pants</option>
                  <option value="Hoodie" ${order.product === 'Hoodie' ? 'selected' : ''}>Hoodie</option>
                  <option value="Uniform" ${order.product === 'Uniform' ? 'selected' : ''}>Uniform</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">Quantity</label>
                <input type="number" class="form-control" id="edit-order-qty" value="${order.quantity}" required>
              </div>
              <div class="form-group">
                <label class="form-label">Deadline</label>
                <input type="date" class="form-control" id="edit-order-deadline" value="${order.deadline}" required>
              </div>
              <div class="form-group">
                <label class="form-label">Production Stage</label>
                <select class="form-control" id="edit-order-stage">
                  <option value="Cutting" ${order.currentStage === 'Cutting' ? 'selected' : ''}>Cutting</option>
                  <option value="Stitching" ${order.currentStage === 'Stitching' ? 'selected' : ''}>Stitching</option>
                  <option value="Finishing" ${order.currentStage === 'Finishing' ? 'selected' : ''}>Finishing</option>
                  <option value="Quality Check" ${order.currentStage === 'Quality Check' ? 'selected' : ''}>Quality Check</option>
                  <option value="Packaging" ${order.currentStage === 'Packaging' ? 'selected' : ''}>Packaging</option>
                  <option value="Dispatch" ${order.currentStage === 'Dispatch' ? 'selected' : ''}>Dispatch</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">Status</label>
                <select class="form-control" id="edit-order-status">
                  <option value="Pending" ${order.status === 'Pending' ? 'selected' : ''}>Pending</option>
                  <option value="In Progress" ${order.status === 'In Progress' ? 'selected' : ''}>In Progress</option>
                  <option value="Completed" ${order.status === 'Completed' ? 'selected' : ''}>Completed</option>
                  <option value="Delayed" ${order.status === 'Delayed' ? 'selected' : ''}>Delayed</option>
                </select>
              </div>
            </div>
            <div class="modal-footer" style="margin: 0 -24px -24px -24px;">
              <button type="button" class="btn btn-secondary btn-sm" onclick="document.getElementById('edit-order-modal').remove()">Cancel</button>
              <button type="submit" class="btn btn-primary btn-sm">Save Changes</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  `;

  document.body.insertAdjacentHTML('beforeend', modalHtml);

  document.getElementById('edit-order-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    order.customer = document.getElementById('edit-order-customer').value;
    order.customerName = order.customer;
    order.product = document.getElementById('edit-order-product').value;
    order.productName = order.product;
    order.quantity = parseInt(document.getElementById('edit-order-qty').value, 10);
    order.deadline = document.getElementById('edit-order-deadline').value;
    order.currentStage = document.getElementById('edit-order-stage').value;
    order.status = document.getElementById('edit-order-status').value;

    if (typeof ApiService !== 'undefined' && ApiService.updateOrder) {
      try {
        await ApiService.updateOrder(order.id, {
          customerName: order.customer,
          productName: order.product,
          quantity: order.quantity,
          deadline: order.deadline,
          currentStage: order.currentStage,
          status: order.status
        });
      } catch (err) {
        console.warn('Backend update failed, updating local state:', err);
      }
    }

    DataStore.updateOrder(order);
    document.getElementById('edit-order-modal').remove();
    showToast(`Order ${order.id} updated successfully`, 'success');
    renderOrdersTable();
  });
}
