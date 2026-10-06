/**
 * GARMENT TRACKER - PRODUCTION TRACKING SYSTEM
 * Central Data Store, State Management & Shared UI Helpers
 */

const STORAGE_KEYS = {
  ORDERS: 'garment_orders_data',
  EMPLOYEES: 'garment_employees_data',
  INVENTORY_RAW: 'garment_inventory_raw_data',
  QUALITY_CHECKS: 'garment_qc_data',
  USERS: 'garment_users_data',
  ALERTS: 'garment_alerts_data',
  SETTINGS: 'garment_settings_data'
};

// Initial Seed Data (Production ERP Standard)
const DEFAULT_ORDERS = [
  {
    id: 'ORD001',
    customer: 'ABC Fashion',
    product: 'T-Shirt',
    quantity: 500,
    currentStage: 'Stitching',
    status: 'In Progress',
    deadline: '2026-10-12',
    createdDate: '2026-09-28',
    fabricType: '100% Combed Cotton Single Jersey (180 GSM)',
    color: 'Navy Blue / Heather Grey',
    sizes: 'S: 100, M: 200, L: 150, XL: 50',
    priority: 'High',
    assignedWorker: 'Rahim Uddin (Stitching Lead)',
    progress: 60,
    notes: 'Double needle stitch on hem and sleeve cuffs. Strict color fastness requirement.',
    history: [
      { stage: 'Order Created', date: '28 Sep 2026', user: 'Admin', status: 'Completed', note: 'Order registered from ABC Fashion' },
      { stage: 'Cutting', date: '01 Oct 2026', user: 'Fatima Begum', status: 'Completed', note: '500 units cut and bundled with zero wastage' },
      { stage: 'Stitching', date: '04 Oct 2026', user: 'Rahim Uddin', status: 'In Progress', note: 'Line 2 assembled front and back panels' },
      { stage: 'Finishing', date: 'Pending', user: 'Unassigned', status: 'Pending', note: 'Awaiting sewing line completion' },
      { stage: 'Quality Check', date: 'Pending', user: 'Unassigned', status: 'Pending', note: 'Pending' },
      { stage: 'Packaging', date: 'Pending', user: 'Unassigned', status: 'Pending', note: 'Pending' },
      { stage: 'Dispatch', date: 'Pending', user: 'Unassigned', status: 'Pending', note: 'Pending' }
    ]
  },
  {
    id: 'ORD002',
    customer: 'XYZ Garments',
    product: 'Shirt',
    quantity: 800,
    currentStage: 'Finishing',
    status: 'Pending',
    deadline: '2026-10-15',
    createdDate: '2026-09-25',
    fabricType: 'Oxford Cotton Weave (120 GSM)',
    color: 'Classic White & Sky Blue',
    sizes: '38: 200, 40: 300, 42: 200, 44: 100',
    priority: 'Medium',
    assignedWorker: 'Anowar Hossain (Finishing Lead)',
    progress: 40,
    notes: 'Buttonholing and collar stiffener pressing required.',
    history: [
      { stage: 'Order Created', date: '25 Sep 2026', user: 'Admin', status: 'Completed', note: 'Order confirmed' },
      { stage: 'Cutting', date: '27 Sep 2026', user: 'Fatima Begum', status: 'Completed', note: 'Cut complete' },
      { stage: 'Stitching', date: '02 Oct 2026', user: 'Rahim Uddin', status: 'Completed', note: 'Stitching inspected and passed' },
      { stage: 'Finishing', date: '05 Oct 2026', user: 'Anowar Hossain', status: 'Pending', note: 'In queue for button pressing' },
      { stage: 'Quality Check', date: 'Pending', user: 'Unassigned', status: 'Pending', note: 'Pending' },
      { stage: 'Packaging', date: 'Pending', user: 'Unassigned', status: 'Pending', note: 'Pending' },
      { stage: 'Dispatch', date: 'Pending', user: 'Unassigned', status: 'Pending', note: 'Pending' }
    ]
  },
  {
    id: 'ORD003',
    customer: 'PQR Exports',
    product: 'Jacket',
    quantity: 300,
    currentStage: 'Quality Check',
    status: 'In Progress',
    deadline: '2026-10-10',
    createdDate: '2026-09-20',
    fabricType: 'Water-resistant Taslan Nylon with Polyester Quilted Lining',
    color: 'Charcoal Black',
    sizes: 'M: 100, L: 120, XL: 80',
    priority: 'Urgent',
    assignedWorker: 'Kamal Hassan (Senior QA)',
    progress: 80,
    notes: 'Heavy duty YKK zippers. Waterproof seam sealing test.',
    history: [
      { stage: 'Order Created', date: '20 Sep 2026', user: 'Admin', status: 'Completed', note: 'Export batch priority' },
      { stage: 'Cutting', date: '22 Sep 2026', user: 'Fatima Begum', status: 'Completed', note: 'Laser cutting complete' },
      { stage: 'Stitching', date: '28 Sep 2026', user: 'Rahim Uddin', status: 'Completed', note: 'Shell and lining joined' },
      { stage: 'Finishing', date: '03 Oct 2026', user: 'Anowar Hossain', status: 'Completed', note: 'Trimming & iron finished' },
      { stage: 'Quality Check', date: '05 Oct 2026', user: 'Kamal Hassan', status: 'In Progress', note: 'Under final AQL 2.5 inspection' },
      { stage: 'Packaging', date: 'Pending', user: 'Unassigned', status: 'Pending', note: 'Pending' },
      { stage: 'Dispatch', date: 'Pending', user: 'Unassigned', status: 'Pending', note: 'Pending' }
    ]
  },
  {
    id: 'ORD004',
    customer: 'Fashion World',
    product: 'Pants',
    quantity: 600,
    currentStage: 'Cutting',
    status: 'In Progress',
    deadline: '2026-10-18',
    createdDate: '2026-10-02',
    fabricType: 'Stretch Cotton Twill (240 GSM)',
    color: 'Khaki & Olive Green',
    sizes: '30: 100, 32: 250, 34: 150, 36: 100',
    priority: 'Medium',
    assignedWorker: 'Fatima Begum (Master Cutter)',
    progress: 70,
    notes: 'Pocket bag printing with wash instructions.',
    history: [
      { stage: 'Order Created', date: '02 Oct 2026', user: 'Admin', status: 'Completed', note: 'Order booked' },
      { stage: 'Cutting', date: '04 Oct 2026', user: 'Fatima Begum', status: 'In Progress', note: 'Spreading fabric and marker laying' },
      { stage: 'Stitching', date: 'Pending', user: 'Unassigned', status: 'Pending', note: 'Pending' },
      { stage: 'Finishing', date: 'Pending', user: 'Unassigned', status: 'Pending', note: 'Pending' },
      { stage: 'Quality Check', date: 'Pending', user: 'Unassigned', status: 'Pending', note: 'Pending' },
      { stage: 'Packaging', date: 'Pending', user: 'Unassigned', status: 'Pending', note: 'Pending' },
      { stage: 'Dispatch', date: 'Pending', user: 'Unassigned', status: 'Pending', note: 'Pending' }
    ]
  },
  {
    id: 'ORD005',
    customer: 'Style Hub',
    product: 'T-Shirt',
    quantity: 1000,
    currentStage: 'Packaging',
    status: 'In Progress',
    deadline: '2026-10-20',
    createdDate: '2026-09-18',
    fabricType: 'Organic Combed Cotton (160 GSM)',
    color: 'Pastel Mint & Pure White',
    sizes: 'XS: 100, S: 300, M: 400, L: 200',
    priority: 'Low',
    assignedWorker: 'Nasrin Akter (Packaging Lead)',
    progress: 85,
    notes: 'Individual biodegradable polybag packing with barcodes.',
    history: [
      { stage: 'Order Created', date: '18 Sep 2026', user: 'Admin', status: 'Completed', note: 'Order registered' },
      { stage: 'Cutting', date: '21 Sep 2026', user: 'Fatima Begum', status: 'Completed', note: 'Cut complete' },
      { stage: 'Stitching', date: '27 Sep 2026', user: 'Rahim Uddin', status: 'Completed', note: 'Stitching complete' },
      { stage: 'Finishing', date: '01 Oct 2026', user: 'Anowar Hossain', status: 'Completed', note: 'Pressing done' },
      { stage: 'Quality Check', date: '03 Oct 2026', user: 'Kamal Hassan', status: 'Completed', note: 'QC Passed - 0 defect rate' },
      { stage: 'Packaging', date: '05 Oct 2026', user: 'Nasrin Akter', status: 'In Progress', note: 'Polybagging and carton packing' },
      { stage: 'Dispatch', date: 'Pending', user: 'Unassigned', status: 'Pending', note: 'Pending' }
    ]
  },
  {
    id: 'ORD006',
    customer: 'Urban Vogue',
    product: 'Hoodie',
    quantity: 450,
    currentStage: 'Dispatch',
    status: 'Completed',
    deadline: '2026-10-06',
    createdDate: '2026-09-10',
    fabricType: 'Fleece Brushed Back (320 GSM)',
    color: 'Ash Melange',
    sizes: 'S: 50, M: 150, L: 150, XL: 100',
    priority: 'High',
    assignedWorker: 'Tariq Islam (Dispatch Officer)',
    progress: 100,
    notes: 'Kangaroo pocket with tonal drawstrings.',
    history: [
      { stage: 'Order Created', date: '10 Sep 2026', user: 'Admin', status: 'Completed', note: 'Complete' },
      { stage: 'Cutting', date: '14 Sep 2026', user: 'Fatima Begum', status: 'Completed', note: 'Complete' },
      { stage: 'Stitching', date: '20 Sep 2026', user: 'Rahim Uddin', status: 'Completed', note: 'Complete' },
      { stage: 'Finishing', date: '25 Sep 2026', user: 'Anowar Hossain', status: 'Completed', note: 'Complete' },
      { stage: 'Quality Check', date: '28 Sep 2026', user: 'Kamal Hassan', status: 'Completed', note: 'Passed' },
      { stage: 'Packaging', date: '01 Oct 2026', user: 'Nasrin Akter', status: 'Completed', note: 'Packed in master cartons' },
      { stage: 'Dispatch', date: '04 Oct 2026', user: 'Tariq Islam', status: 'Completed', note: 'Dispatched via Air Freight' }
    ]
  },
  {
    id: 'ORD007',
    customer: 'Elite Corp Uniforms',
    product: 'Uniform',
    quantity: 1200,
    currentStage: 'Quality Check',
    status: 'Delayed',
    deadline: '2026-10-04',
    createdDate: '2026-09-12',
    fabricType: 'Poly-Viscose Anti-wrinkle Fabric',
    color: 'Corporate Navy',
    sizes: 'Standard Corporate Spec Set',
    priority: 'Urgent',
    assignedWorker: 'Kamal Hassan (Senior QA)',
    progress: 75,
    notes: 'Embroidered corporate chest emblem on each garment.',
    history: [
      { stage: 'Order Created', date: '12 Sep 2026', user: 'Admin', status: 'Completed', note: 'Order registered' },
      { stage: 'Cutting', date: '16 Sep 2026', user: 'Fatima Begum', status: 'Completed', note: 'Cut complete' },
      { stage: 'Stitching', date: '24 Sep 2026', user: 'Rahim Uddin', status: 'Completed', note: 'Embroidered and sewn' },
      { stage: 'Finishing', date: '30 Sep 2026', user: 'Anowar Hossain', status: 'Completed', note: 'Finishing finished' },
      { stage: 'Quality Check', date: '03 Oct 2026', user: 'Kamal Hassan', status: 'Delayed', note: 'Minor alignment defect flagged on badges - rework requested' },
      { stage: 'Packaging', date: 'Pending', user: 'Unassigned', status: 'Pending', note: 'Pending' },
      { stage: 'Dispatch', date: 'Pending', user: 'Unassigned', status: 'Pending', note: 'Pending' }
    ]
  }
];

const DEFAULT_INVENTORY = [
  { id: 'MAT001', name: 'Fabric', category: 'Raw Material', quantity: 2500, unit: 'm', supplier: 'Textile Mills Ltd', status: 'In Stock', threshold: 1000, location: 'Rack A-12' },
  { id: 'MAT002', name: 'Thread', category: 'Accessories', quantity: 15000, unit: 'pcs', supplier: 'Coats & Clark Corp', status: 'In Stock', threshold: 5000, location: 'Bin B-04' },
  { id: 'MAT003', name: 'Buttons', category: 'Trims', quantity: 3200, unit: 'pcs', supplier: 'Fastener Tech Co', status: 'Low Stock', threshold: 4000, location: 'Bin C-09' },
  { id: 'MAT004', name: 'Labels', category: 'Trims', quantity: 5000, unit: 'pcs', supplier: 'Global Woven Label Ltd', status: 'In Stock', threshold: 2000, location: 'Shelf D-01' },
  { id: 'MAT005', name: 'Packaging Materials', category: 'Packaging', quantity: 1200, unit: 'boxes', supplier: 'EcoPack Solutions', status: 'In Stock', threshold: 500, location: 'Warehouse Bay 2' },
  { id: 'MAT006', name: 'Zippers (YKK 18cm)', category: 'Trims', quantity: 150, unit: 'pcs', supplier: 'YKK Fasteners Ltd', status: 'Out of Stock', threshold: 500, location: 'Bin C-15' },
  { id: 'MAT007', name: 'Elastic Waistband Tape', category: 'Trims', quantity: 800, unit: 'm', supplier: 'Apex Elastic Industries', status: 'Low Stock', threshold: 1000, location: 'Rack B-08' }
];

const DEFAULT_EMPLOYEES = [
  { id: 'EMP101', name: 'Rahim Uddin', department: 'Production', role: 'Stitching Lead', assignedOrders: 4, currentTask: 'ORD001 Collar Stitching', performance: 98, status: 'Working', efficiency: '96%', qualityScore: '99%' },
  { id: 'EMP102', name: 'Fatima Begum', department: 'Cutting', role: 'Master Cutter', assignedOrders: 3, currentTask: 'ORD004 Pattern Cutting', performance: 95, status: 'Working', efficiency: '94%', qualityScore: '97%' },
  { id: 'EMP103', name: 'Kamal Hassan', department: 'Quality Control', role: 'Senior QA Inspector', assignedOrders: 2, currentTask: 'ORD003 Defect Analysis', performance: 92, status: 'Working', efficiency: '92%', qualityScore: '94%' },
  { id: 'EMP104', name: 'Anowar Hossain', department: 'Finishing', role: 'Iron & Press Specialist', assignedOrders: 3, currentTask: 'ORD002 Steam Pressing', performance: 89, status: 'Working', efficiency: '88%', qualityScore: '91%' },
  { id: 'EMP105', name: 'Nasrin Akter', department: 'Packaging', role: 'Packing Supervisor', assignedOrders: 2, currentTask: 'ORD005 Final Box Packing', performance: 96, status: 'Working', efficiency: '95%', qualityScore: '98%' },
  { id: 'EMP106', name: 'Tariq Islam', department: 'Logistics', role: 'Dispatch Officer', assignedOrders: 1, currentTask: 'ORD006 Export Documentation', performance: 94, status: 'Available', efficiency: '93%', qualityScore: '95%' },
  { id: 'EMP107', name: 'Salma Khatun', department: 'Production', role: 'Overlock Machine Operator', assignedOrders: 0, currentTask: 'None', performance: 91, status: 'On Leave', efficiency: '90%', qualityScore: '92%' }
];

const DEFAULT_QC_CHECKS = [
  { id: 'QC-101', orderId: 'ORD003', product: 'Jacket', quantity: 300, inspector: 'Kamal Hassan', inspectionDate: '2026-10-05', defectType: 'Loose Seam Threads', defectQty: 4, result: 'Passed', remarks: 'Trimmed minor loose threads on cuff, ready for packing.' },
  { id: 'QC-102', orderId: 'ORD007', product: 'Uniform', quantity: 1200, inspector: 'Kamal Hassan', inspectionDate: '2026-10-04', defectType: 'Emblem Misalignment', defectQty: 18, result: 'Failed', remarks: 'Requires Rework: 18 chest emblems tilted > 3mm.' },
  { id: 'QC-103', orderId: 'ORD005', product: 'T-Shirt', quantity: 1000, inspector: 'Kamal Hassan', inspectionDate: '2026-10-03', defectType: 'None', defectQty: 0, result: 'Passed', remarks: 'Ready for Packaging: zero defects observed in 80 sampled units.' },
  { id: 'QC-104', orderId: 'ORD001', product: 'T-Shirt', quantity: 500, inspector: 'Kamal Hassan', inspectionDate: '2026-10-05', defectType: 'Pending Inspection', defectQty: 0, result: 'Pending', remarks: 'Stitching in progress; preliminary sample check scheduled.' }
];

const DEFAULT_USERS = [
  { id: 'USR001', name: 'Admin User', username: 'admin', role: 'Administrator', status: 'Active', lastLogin: 'Today, 10:45 AM' },
  { id: 'USR002', name: 'Production Manager', username: 'prod_mgr', role: 'Manager', status: 'Active', lastLogin: 'Yesterday, 04:30 PM' },
  { id: 'USR003', name: 'Kamal Hassan', username: 'kamal_qa', role: 'Staff', status: 'Active', lastLogin: '03 Oct 2026' },
  { id: 'USR004', name: 'Nasrin Akter', username: 'nasrin_pack', role: 'Staff', status: 'Active', lastLogin: '01 Oct 2026' },
  { id: 'USR005', name: 'Former Operator', username: 'operator_old', role: 'Staff', status: 'Inactive', lastLogin: '15 Sep 2026' }
];

const DEFAULT_ALERTS = [
  { id: 1, type: 'danger', message: 'Thread stock is running low', time: '2 hours ago', icon: 'fa-circle-exclamation' },
  { id: 2, type: 'warning', message: 'Order ORD004 delayed (Finishing)', time: '4 hours ago', icon: 'fa-triangle-exclamation' },
  { id: 3, type: 'info', message: 'Quality check pending for ORD007', time: '6 hours ago', icon: 'fa-circle-info' }
];

// Initialize Data Store in localStorage
function initDataStore() {
  if (!localStorage.getItem(STORAGE_KEYS.ORDERS)) {
    localStorage.setItem(STORAGE_KEYS.ORDERS, JSON.stringify(DEFAULT_ORDERS));
  }
  if (!localStorage.getItem(STORAGE_KEYS.INVENTORY_RAW)) {
    localStorage.setItem(STORAGE_KEYS.INVENTORY_RAW, JSON.stringify(DEFAULT_INVENTORY));
  }
  if (!localStorage.getItem(STORAGE_KEYS.EMPLOYEES)) {
    localStorage.setItem(STORAGE_KEYS.EMPLOYEES, JSON.stringify(DEFAULT_EMPLOYEES));
  }
  if (!localStorage.getItem(STORAGE_KEYS.QUALITY_CHECKS)) {
    localStorage.setItem(STORAGE_KEYS.QUALITY_CHECKS, JSON.stringify(DEFAULT_QC_CHECKS));
  }
  if (!localStorage.getItem(STORAGE_KEYS.USERS)) {
    localStorage.setItem(STORAGE_KEYS.USERS, JSON.stringify(DEFAULT_USERS));
  }
  if (!localStorage.getItem(STORAGE_KEYS.ALERTS)) {
    localStorage.setItem(STORAGE_KEYS.ALERTS, JSON.stringify(DEFAULT_ALERTS));
  }
}

// Data Access Helpers
const DataStore = {
  getOrders() {
    return JSON.parse(localStorage.getItem(STORAGE_KEYS.ORDERS) || '[]');
  },
  saveOrders(orders) {
    localStorage.setItem(STORAGE_KEYS.ORDERS, JSON.stringify(orders));
  },
  getOrderById(id) {
    const orders = this.getOrders();
    return orders.find(o => o.id === id);
  },
  addOrder(order) {
    const orders = this.getOrders();
    orders.unshift(order);
    this.saveOrders(orders);
    return order;
  },
  updateOrder(updatedOrder) {
    const orders = this.getOrders();
    const index = orders.findIndex(o => o.id === updatedOrder.id);
    if (index !== -1) {
      orders[index] = updatedOrder;
      this.saveOrders(orders);
      return true;
    }
    return false;
  },
  deleteOrder(id) {
    let orders = this.getOrders();
    orders = orders.filter(o => o.id !== id);
    this.saveOrders(orders);
  },

  getEmployees() {
    return JSON.parse(localStorage.getItem(STORAGE_KEYS.EMPLOYEES) || '[]');
  },
  saveEmployees(employees) {
    localStorage.setItem(STORAGE_KEYS.EMPLOYEES, JSON.stringify(employees));
  },
  addEmployee(emp) {
    const list = this.getEmployees();
    list.unshift(emp);
    this.saveEmployees(list);
  },

  getInventory() {
    return JSON.parse(localStorage.getItem(STORAGE_KEYS.INVENTORY_RAW) || '[]');
  },
  saveInventory(inv) {
    localStorage.setItem(STORAGE_KEYS.INVENTORY_RAW, JSON.stringify(inv));
  },

  getQualityChecks() {
    return JSON.parse(localStorage.getItem(STORAGE_KEYS.QUALITY_CHECKS) || '[]');
  },
  saveQualityChecks(qc) {
    localStorage.setItem(STORAGE_KEYS.QUALITY_CHECKS, JSON.stringify(qc));
  },
  addQualityCheck(item) {
    const list = this.getQualityChecks();
    list.unshift(item);
    this.saveQualityChecks(list);
  },

  getUsers() {
    return JSON.parse(localStorage.getItem(STORAGE_KEYS.USERS) || '[]');
  },
  saveUsers(users) {
    localStorage.setItem(STORAGE_KEYS.USERS, JSON.stringify(users));
  },

  getAlerts() {
    return JSON.parse(localStorage.getItem(STORAGE_KEYS.ALERTS) || '[]');
  }
};

// UI Helpers: Toast Notifications
function showToast(message, type = 'success') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;

  let iconClass = 'fa-circle-check';
  if (type === 'error') iconClass = 'fa-circle-xmark';
  if (type === 'warning') iconClass = 'fa-triangle-exclamation';
  if (type === 'info') iconClass = 'fa-circle-info';

  toast.innerHTML = `
    <i class="fa-solid ${iconClass}" style="color: var(--${type === 'error' ? 'danger' : type}-color); font-size: 18px;"></i>
    <div style="flex:1; font-weight:600; font-size:13px; color: var(--text-dark);">${message}</div>
    <button style="color:var(--text-light); padding:2px; font-size:12px;" onclick="this.parentElement.remove()"><i class="fa-solid fa-xmark"></i></button>
  `;

  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// Reusable Confirmation Dialog
function showConfirmDialog(title, message, onConfirm) {
  const existing = document.getElementById('global-confirm-modal');
  if (existing) existing.remove();

  const modalHtml = `
    <div id="global-confirm-modal" class="modal-overlay active">
      <div class="modal-container" style="max-width: 420px;">
        <div class="modal-header">
          <h3 class="modal-title">${title}</h3>
          <button class="modal-close-btn" onclick="document.getElementById('global-confirm-modal').remove()"><i class="fa-solid fa-xmark"></i></button>
        </div>
        <div class="modal-body">
          <p style="color: var(--text-body); font-size: 13.5px; line-height: 1.5;">${message}</p>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary btn-sm" onclick="document.getElementById('global-confirm-modal').remove()">Cancel</button>
          <button id="confirm-dialog-yes" class="btn btn-danger btn-sm">Confirm</button>
        </div>
      </div>
    </div>
  `;
  document.body.insertAdjacentHTML('beforeend', modalHtml);
  document.getElementById('confirm-dialog-yes').addEventListener('click', () => {
    document.getElementById('global-confirm-modal').remove();
    if (typeof onConfirm === 'function') onConfirm();
  });
}

// Stage & Status Badge Renderers
function getStageBadge(stage) {
  const stageClassMap = {
    'Cutting': 'stage-cutting',
    'Stitching': 'stage-stitching',
    'Finishing': 'stage-finishing',
    'Quality Check': 'stage-quality',
    'Packaging': 'stage-packaging',
    'Dispatch': 'stage-dispatch'
  };
  const cls = stageClassMap[stage] || 'stage-cutting';
  return `<span class="stage-badge ${cls}">${stage}</span>`;
}

function getStatusBadge(status) {
  const statusMap = {
    'In Progress': 'badge-in-progress',
    'Completed': 'badge-completed',
    'Pending': 'badge-pending',
    'Delayed': 'badge-delayed',
    'Failed': 'badge-failed',
    'Passed': 'badge-completed',
    'In Stock': 'badge-in-stock',
    'Low Stock': 'badge-low-stock',
    'Out of Stock': 'badge-out-of-stock',
    'Working': 'badge-in-progress',
    'Available': 'badge-completed',
    'On Leave': 'badge-pending',
    'Active': 'badge-completed',
    'Inactive': 'badge-delayed'
  };
  const cls = statusMap[status] || 'badge-pending';
  return `<span class="badge ${cls}"><span class="badge-dot"></span>${status}</span>`;
}

function formatDeadline(deadlineStr) {
  if (!deadlineStr) return 'N/A';
  const parts = String(deadlineStr).split('-');
  if (parts.length === 3) {
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const month = months[parseInt(parts[1], 10) - 1] || parts[1];
    return `${parts[2]} ${month} ${parts[0]}`;
  }
  return String(deadlineStr);
}

// Global Layout & Event Binding Initialization
document.addEventListener('DOMContentLoaded', () => {
  initDataStore();

  // Highlight Current Navigation Link
  let currentFile = window.location.pathname.split('/').pop() || 'dashboard.html';
  currentFile = currentFile.split('?')[0].split('#')[0];
  if (!currentFile || currentFile === '') currentFile = 'dashboard.html';

  const currentTab = new URLSearchParams(window.location.search).get('tab') || 'all';

  window.updateSidebarInventoryTab = function(activeTab) {
    document.querySelectorAll('.sidebar-nav .nav-link').forEach(link => {
      const href = link.getAttribute('href');
      if (!href) return;
      const cleanHref = href.split('?')[0].split('#')[0];
      if (cleanHref === 'inventory.html') {
        link.classList.remove('active');
        if (activeTab === 'all' || !activeTab) {
          if (href === 'inventory.html' || href.endsWith('/inventory.html')) {
            link.classList.add('active');
          }
        } else {
          if (href.includes(`?tab=${activeTab}`)) {
            link.classList.add('active');
          }
        }
      }
    });
  };

  document.querySelectorAll('.sidebar-nav .nav-link').forEach(link => {
    const span = link.querySelector('span');
    if (span && !link.getAttribute('data-title')) {
      link.setAttribute('data-title', span.textContent.trim());
    }
    const href = link.getAttribute('href');
    if (!href) return;

    let isActive = false;
    if (currentFile === 'inventory.html') {
      if (href.includes('?tab=')) {
        const linkTab = new URLSearchParams(href.split('?')[1] || '').get('tab');
        if (currentTab === linkTab) {
          isActive = true;
        }
      } else {
        const cleanHref = href.split('?')[0].split('#')[0];
        if (cleanHref === 'inventory.html' && (currentTab === 'all' || !currentTab)) {
          isActive = true;
        }
      }
    } else {
      const cleanHref = href.split('?')[0].split('#')[0];
      if (cleanHref === currentFile) {
        isActive = true;
      }
    }

    if (isActive) {
      link.classList.add('active');
    } else {
      link.classList.remove('active');
    }
  });

  // Mobile Menu Drawer Handler
  const mobileToggle = document.getElementById('mobile-menu-toggle');
  const sidebar = document.querySelector('.sidebar');
  let backdrop = document.querySelector('.sidebar-backdrop');

  if (!backdrop) {
    backdrop = document.createElement('div');
    backdrop.className = 'sidebar-backdrop';
    document.body.appendChild(backdrop);
  }

  if (mobileToggle && sidebar) {
    mobileToggle.addEventListener('click', () => {
      sidebar.classList.toggle('show');
      backdrop.classList.toggle('show');
    });
  }

  backdrop.addEventListener('click', () => {
    if (sidebar) sidebar.classList.remove('show');
    backdrop.classList.remove('show');
  });

  // User Profile Dropdown in Top Header
  const userBtn = document.getElementById('header-user-btn');
  const userMenu = document.getElementById('user-dropdown-menu');
  if (userBtn && userMenu) {
    userBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      userMenu.classList.toggle('show');
    });

    document.addEventListener('click', (e) => {
      if (!userMenu.contains(e.target) && !userBtn.contains(e.target)) {
        userMenu.classList.remove('show');
      }
    });
  }

  // Global Header Search Listener
  const globalSearch = document.getElementById('global-search-input');
  if (globalSearch) {
    globalSearch.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        const query = globalSearch.value.trim();
        if (query) {
          window.location.href = `orders.html?search=${encodeURIComponent(query)}`;
        }
      }
    });
  }

  // Quick Action: Logout Handler
  document.querySelectorAll('.logout-trigger').forEach(el => {
    el.addEventListener('click', (e) => {
      e.preventDefault();
      localStorage.removeItem('currentUser');
      localStorage.removeItem('garment_current_user');
      localStorage.removeItem('garment_jwt_token');
      showToast('Logged out successfully', 'info');
      setTimeout(() => {
        window.location.href = 'login.html';
      }, 500);
    });
  });

  // Dynamically synchronize logged-in user profile in header and sidebar
  syncGlobalUserUI();
});

// ========================================================
// GLOBAL USER PROFILE STATE MANAGEMENT
// ========================================================
function getActiveUser() {
  try {
    const raw = localStorage.getItem('garment_current_user') || localStorage.getItem('currentUser');
    if (raw) {
      const parsed = JSON.parse(raw);
      if (parsed && (parsed.name || parsed.username || parsed.email)) {
        return parsed;
      }
    }
  } catch (e) {
    console.warn('Error reading active user from storage:', e);
  }
  return {
    name: 'Admin User',
    username: 'admin',
    role: 'Administrator',
    email: 'admin@garment.com'
  };
}

function syncGlobalUserUI() {
  const user = getActiveUser();
  const displayName = user.name || user.username || (user.email ? user.email.split('@')[0] : 'Admin User');
  const roleName = user.role || 'Administrator';

  // 1. Top Header User Info Dropdown
  document.querySelectorAll('.header-user-info .name').forEach(el => {
    el.textContent = displayName;
  });
  document.querySelectorAll('.header-user-info .role').forEach(el => {
    el.textContent = roleName;
  });

  // 2. Sidebar Footer Profile Summary
  document.querySelectorAll('.user-profile-summary .user-meta-name').forEach(el => {
    el.textContent = displayName;
  });
  document.querySelectorAll('.user-profile-summary .user-meta-role').forEach(el => {
    el.textContent = roleName;
  });

  // 3. User Avatars tooltip / alt
  document.querySelectorAll('.user-avatar-wrap img, .header-user-btn img').forEach(img => {
    img.alt = displayName;
    img.title = `${displayName} (${roleName})`;
  });

  // 4. Any elements with data attributes
  document.querySelectorAll('[data-user-name]').forEach(el => el.textContent = displayName);
  document.querySelectorAll('[data-user-role]').forEach(el => el.textContent = roleName);
}

// Make accessible globally
window.getActiveUser = getActiveUser;
window.syncGlobalUserUI = syncGlobalUserUI;

// Run immediate sync on script execution if DOM elements already exist
if (document.readyState === 'interactive' || document.readyState === 'complete') {
  syncGlobalUserUI();
} else {
  document.addEventListener('DOMContentLoaded', syncGlobalUserUI);
}
window.addEventListener('storage', (e) => {
  if (e.key === 'garment_current_user' || e.key === 'currentUser') {
    syncGlobalUserUI();
  }
});
