/**
 * GARMENT TRACKER - API SERVICE & CLOUD FIRESTORE INTEGRATION
 * Facilitates live communication between the frontend and Python Flask REST API / Firestore.
 */
// Dynamically determine backend URL (uses localhost for Live Server, or relative /api when hosted on Render)
const API_BASE_URL = (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') && (window.location.port === '5500' || window.location.port === '8080' || window.location.port === '3000')
  ? 'http://127.0.0.1:5000/api'
  : `${window.location.origin}/api`;

function normalizeOrder(o) {
  if (!o) return null;
  return {
    id: o.orderId || o.id || 'ORD000',
    orderId: o.orderId || o.id || 'ORD000',
    customer: o.customerName || o.customer || 'Customer',
    customerName: o.customerName || o.customer || 'Customer',
    customerContact: o.customerContact || '',
    product: o.productName || o.productType || o.product || 'Garment',
    productName: o.productName || o.productType || o.product || 'Garment',
    productType: o.productType || o.productName || o.product || 'Garment',
    quantity: Number(o.quantity) || 0,
    deadline: o.deadline || '',
    currentStage: o.currentStage || 'Cutting',
    status: o.status || 'Pending',
    progress: o.progress !== undefined ? Number(o.progress) : (o.status === 'Completed' ? 100 : (o.currentStage === 'Stitching' ? 60 : 35)),
    priority: o.priority || 'Medium',
    fabricType: o.fabricType || '',
    color: o.color || '',
    sizes: Array.isArray(o.sizes) ? o.sizes.join(', ') : (o.sizes || ''),
    notes: o.notes || o.specifications || '',
    history: Array.isArray(o.history) ? o.history : []
  };
}

function normalizeInventoryItem(m) {
  if (!m) return null;
  const qty = Number(m.quantity) || 0;
  return {
    id: m.materialId || m.id || 'MAT000',
    materialId: m.materialId || m.id || 'MAT000',
    name: m.materialName || m.name || 'Material',
    materialName: m.materialName || m.name || 'Material',
    category: m.category || 'Raw Material',
    quantity: qty,
    unit: m.unit || 'units',
    supplier: m.supplier || 'Supplier',
    status: m.status || (qty > 500 ? 'In Stock' : (qty > 0 ? 'Low Stock' : 'Out of Stock')),
    location: m.location || 'Warehouse Floor 1',
    threshold: m.minimumStock || m.threshold || 500
  };
}

const ApiService = {
  token: localStorage.getItem('garment_jwt_token') || '',

  async login(email = 'admin@garment.com', password = 'Admin@123') {
    try {
      const res = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      const json = await res.json();
      if (res.ok && json.success) {
        if (json.data && json.data.token) {
          this.token = json.data.token;
          localStorage.setItem('garment_jwt_token', this.token);
          if (json.data.user) {
            localStorage.setItem('garment_current_user', JSON.stringify(json.data.user));
            localStorage.setItem('currentUser', JSON.stringify(json.data.user));
          }
        }
        return { success: true, data: json.data, user: json.data?.user, message: json.message };
      }
      return { success: false, message: json.message || 'Invalid credentials' };
    } catch (e) {
      console.warn('Backend login connection unavailable:', e.message);
      return { success: false, message: 'Server connection error: ' + e.message };
    }
  },

  async register(userData) {
    try {
      const res = await fetch(`${API_BASE_URL}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData)
      });
      const json = await res.json();
      if (res.ok && json.success) {
        if (json.data && json.data.token) {
          this.token = json.data.token;
          localStorage.setItem('garment_jwt_token', this.token);
          if (json.data.user) {
            localStorage.setItem('garment_current_user', JSON.stringify(json.data.user));
            localStorage.setItem('currentUser', JSON.stringify(json.data.user));
          }
        }
        return { success: true, data: json.data, user: json.data?.user, message: json.message };
      }
      return { success: false, message: json.message || 'Registration failed' };
    } catch (e) {
      return { success: false, message: 'Server connection error: ' + e.message };
    }
  },

  async updateProfile(profileData) {
    try {
      const res = await this.request('/auth/profile', {
        method: 'PUT',
        body: JSON.stringify(profileData)
      });
      if (res && res.ok) {
        const json = await res.json();
        if (json.data) {
          const updated = json.data;
          const current = JSON.parse(localStorage.getItem('currentUser') || '{}');
          const merged = { ...current, ...updated };
          localStorage.setItem('currentUser', JSON.stringify(merged));
          localStorage.setItem('garment_current_user', JSON.stringify(merged));
          if (typeof syncGlobalUserUI === 'function') {
            syncGlobalUserUI();
          }
          return { success: true, data: merged, message: json.message };
        }
      }
    } catch (e) {
      console.warn('API updateProfile network issue, updating locally:', e);
    }
    // Fallback: save locally
    const current = JSON.parse(localStorage.getItem('currentUser') || '{}');
    const merged = { ...current, ...profileData };
    localStorage.setItem('currentUser', JSON.stringify(merged));
    localStorage.setItem('garment_current_user', JSON.stringify(merged));
    if (typeof syncGlobalUserUI === 'function') {
      syncGlobalUserUI();
    }
    return { success: true, data: merged, message: 'Profile updated' };
  },

  async request(endpoint, options = {}) {
    if (!this.token) {
      await this.login();
    }

    const headers = {
      'Content-Type': 'application/json',
      ...(options.headers || {})
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    try {
      let res = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers
      });

      // Token refresh on 401
      if (res.status === 401) {
        const freshToken = await this.login();
        if (freshToken) {
          headers['Authorization'] = `Bearer ${freshToken}`;
          res = await fetch(`${API_BASE_URL}${endpoint}`, {
            ...options,
            headers
          });
        }
      }

      if (res.ok) {
        return await res.json();
      }
    } catch (err) {
      console.warn(`ApiService fetch failed for ${endpoint}:`, err.message);
    }
    return null;
  },

  // LIVE ORDERS
  async getOrders() {
    const res = await this.request('/orders');
    if (res && res.data && Array.isArray(res.data)) {
      const normalized = res.data.map(normalizeOrder);
      if (typeof DataStore !== 'undefined') {
        DataStore.saveOrders(normalized);
      }
      return normalized;
    }
    return null;
  },

  async getOrderById(orderId) {
    const res = await this.request(`/orders/${orderId}`);
    if (res && res.data) {
      return normalizeOrder(res.data);
    }
    return null;
  },

  async createOrder(orderData) {
    const payload = {
      orderId: orderData.id || orderData.orderId,
      customerName: orderData.customer || orderData.customerName,
      customerContact: orderData.customerContact || '',
      productName: orderData.product || orderData.productName,
      productType: orderData.productType || orderData.product || 'T-Shirt',
      quantity: Number(orderData.quantity) || 0,
      deadline: orderData.deadline,
      priority: orderData.priority || 'Medium',
      fabricType: orderData.fabricType || '',
      color: orderData.color || '',
      sizes: Array.isArray(orderData.sizes) ? orderData.sizes : (orderData.sizes ? [orderData.sizes] : ['M', 'L']),
      specifications: orderData.notes || orderData.specifications || '',
      status: orderData.status || 'In Production'
    };

    const res = await this.request('/orders', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
    // Refresh local cache with live data
    await this.getOrders();
    return res;
  },

  async updateOrder(orderId, updateData) {
    const res = await this.request(`/orders/${orderId}`, {
      method: 'PUT',
      body: JSON.stringify(updateData)
    });
    await this.getOrders();
    return res;
  },

  async deleteOrder(orderId) {
    const res = await this.request(`/orders/${orderId}`, {
      method: 'DELETE'
    });
    await this.getOrders();
    return res;
  },

  // LIVE DASHBOARD METRICS
  async getDashboard() {
    const res = await this.request('/dashboard');
    return res && res.data ? res.data : null;
  },

  // LIVE INVENTORY
  async getInventory() {
    const res = await this.request('/inventory');
    if (res && res.data && Array.isArray(res.data)) {
      const normalized = res.data.map(normalizeInventoryItem);
      if (typeof DataStore !== 'undefined') {
        DataStore.saveInventory(normalized);
      }
      return normalized;
    }
    return null;
  },

  // LIVE EMPLOYEES
  async getEmployees() {
    const res = await this.request('/employees');
    return res && res.data ? res.data : null;
  },

  // LIVE PRODUCTION STAGES
  async getProductionStages(orderId = null) {
    const endpoint = orderId ? `/production/${orderId}` : '/production';
    const res = await this.request(endpoint);
    return res && res.data ? res.data : null;
  }
};
