/* ─────────────────────────────────────────────
   api.js  –  Shared utilities for Online Bookstore
   ──────────────────────────────────────────────*/

const API_BASE = 'http://localhost:5000/api';

/* ── Token helpers ── */
const Auth = {
  getToken()  { return localStorage.getItem('bookstore_token'); },
  setToken(t) { localStorage.setItem('bookstore_token', t); },
  removeToken(){ localStorage.removeItem('bookstore_token'); localStorage.removeItem('bookstore_user'); },
  getUser()   { try { return JSON.parse(localStorage.getItem('bookstore_user')); } catch { return null; } },
  setUser(u)  { localStorage.setItem('bookstore_user', JSON.stringify(u)); },
  isLoggedIn(){ return !!this.getToken(); },
};

/* ── API wrapper ── */
async function apiFetch(path, options = {}) {
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
  const token = Auth.getToken();
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    const msg = data.message || data.error || `HTTP ${res.status}`;
    throw new Error(msg);
  }
  return data;
}

/* ── Toast notifications ── */
function showToast(message, type = 'info', duration = 3500) {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }
  const icons = {
    success: '<i class="fa-solid fa-circle-check"></i>',
    error:   '<i class="fa-solid fa-circle-xmark"></i>',
    info:    '<i class="fa-solid fa-circle-info"></i>',
    warning: '<i class="fa-solid fa-triangle-exclamation"></i>'
  };
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `<span>${icons[type] || icons.info}</span><span>${message}</span>`;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.animation = 'slideOut 0.3s ease forwards';
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

/* ── Cart badge updater ── */
async function updateCartBadge() {
  if (!Auth.isLoggedIn()) return;
  try {
    const data = await apiFetch('/cart');
    const count = (data.items || []).reduce((sum, i) => sum + (i.quantity || 1), 0);
    document.querySelectorAll('.cart-count').forEach(el => {
      el.textContent = count;
      el.style.display = count > 0 ? 'flex' : 'none';
    });
  } catch {}
}

/* ── Navbar injection ── */
function renderNav(activePage = '') {
  const user = Auth.getUser();
  const isLoggedIn = Auth.isLoggedIn();

  document.body.insertAdjacentHTML('afterbegin', `
    <div id="toast-container"></div>
    <nav class="navbar">
      <a href="index.html" class="nav-brand">
        <div class="brand-icon"><i class="fa-solid fa-book-open"></i></div>
        <span class="brand-name">PageTurn</span>
      </a>

      <div class="nav-search">
        <span class="search-icon"><i class="fa-solid fa-magnifying-glass"></i></span>
        <input type="text" id="global-search" placeholder="Search books, authors…" autocomplete="off">
      </div>

      <div class="nav-links">
        <a href="index.html" class="nav-link ${activePage==='home'?'active':''}"><i class="fa-solid fa-house"></i> Home</a>
        <a href="catalog.html" class="nav-link ${activePage==='catalog'?'active':''}"><i class="fa-solid fa-book"></i> Books</a>
        ${isLoggedIn ? `
          <a href="cart.html" class="nav-link cart-badge ${activePage==='cart'?'active':''}">
            <i class="fa-solid fa-cart-shopping"></i> Cart
            <span class="badge cart-count" style="display:none">0</span>
          </a>
          <a href="orders.html" class="nav-link ${activePage==='orders'?'active':''}"><i class="fa-solid fa-box"></i> Orders</a>
          <span class="nav-link" style="color:var(--gray-600);cursor:default"><i class="fa-solid fa-user"></i> ${user?.name || 'User'}</span>
          <button class="btn btn-secondary btn-sm" onclick="logout()"><i class="fa-solid fa-right-from-bracket"></i> Logout</button>
        ` : `
          <a href="login.html" class="btn btn-outline btn-sm"><i class="fa-solid fa-right-to-bracket"></i> Login</a>
          <a href="register.html" class="btn btn-primary btn-sm"><i class="fa-solid fa-user-plus"></i> Sign Up</a>
        `}
      </div>
    </nav>
  `);

  /* global search redirect */
  const searchInput = document.getElementById('global-search');
  if (searchInput) {
    searchInput.addEventListener('keydown', e => {
      if (e.key === 'Enter' && searchInput.value.trim()) {
        window.location.href = `catalog.html?search=${encodeURIComponent(searchInput.value.trim())}`;
      }
    });
  }

  updateCartBadge();
}

function logout() {
  Auth.removeToken();
  showToast('Logged out successfully', 'success');
  setTimeout(() => window.location.href = 'index.html', 700);
}

/* ── Guard: redirect to login if not authenticated ── */
function requireAuth() {
  if (!Auth.isLoggedIn()) {
    window.location.href = `login.html?next=${encodeURIComponent(window.location.pathname)}`;
    return false;
  }
  return true;
}

/* ── Helpers ── */
function formatPrice(p) { return `$${parseFloat(p).toFixed(2)}`; }
function formatDate(d)  { return new Date(d).toLocaleDateString('en-US', { year:'numeric', month:'short', day:'numeric' }); }

function bookCoverColors(seed) {
  const palettes = [
    ['#1a3a6b','#2563b0'], ['#065A82','#1C7293'],
    ['#28344E','#3b82d4'], ['#1e4d8c','#3b82d4'],
    ['#0a1628','#1a3a6b'], ['#0d2045','#2563b0'],
  ];
  const i = Math.abs(seed || 0) % palettes.length;
  return `linear-gradient(135deg, ${palettes[i][0]}, ${palettes[i][1]})`;
}

function categoryIcon(category) {
  const map = {
    fiction:'fa-book-open', 'science fiction':'fa-rocket', romance:'fa-heart',
    mystery:'fa-magnifying-glass', biography:'fa-user', history:'fa-landmark',
    science:'fa-flask', technology:'fa-laptop-code', children:'fa-child',
    fantasy:'fa-hat-wizard', horror:'fa-ghost', poetry:'fa-feather',
    cooking:'fa-utensils', travel:'fa-plane', business:'fa-briefcase',
    self_help:'fa-seedling', 'self-help':'fa-seedling',
  };
  const key = (category||'').toLowerCase();
  return map[key] || map[Object.keys(map).find(k => key.includes(k))] || 'fa-book';
}

function categoryIconHtml(category) {
  return `<i class="fa-solid ${categoryIcon(category)}"></i>`;
}