// dashboard.js

const token = localStorage.getItem('token');
if (!token) {
  window.location.href = '/static/login.html';
}

const API = '/todo';
let todos = [];
let activeFilter = 'all';
let editingId = null;

// ── API helpers ──────────────────────────────────────────────────────────────
const getHeaders = () => ({
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${localStorage.getItem('token')}`
});

const handleResponse = async (r) => {
  if (r.status === 401) {
    localStorage.removeItem('token');
    window.location.href = '/static/login.html';
    return;
  }
  return r.json();
};

const api = {
  getAll:  ()         => fetch(API, { headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` } }).then(handleResponse),
  post:    (body)     => fetch(API, { method: 'POST', headers: getHeaders(), body: JSON.stringify(body) }).then(handleResponse),
  patch:   (id, body) => fetch(`${API}/${id}`, { method: 'PATCH', headers: getHeaders(), body: JSON.stringify(body) }).then(handleResponse),
  put:     (id, body) => fetch(`${API}/${id}`, { method: 'PUT', headers: getHeaders(), body: JSON.stringify(body) }).then(handleResponse),
  delete:  (id)       => fetch(`${API}/${id}`, { method: 'DELETE', headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` } }).then(r => {
    if (r.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/static/login.html';
    }
  }),
};

// ── Toast ─────────────────────────────────────────────────────────────────────
let toastTimer;
function toast(msg) {
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => el.classList.remove('show'), 2200);
}

// ── Escape HTML ───────────────────────────────────────────────────────────────
function escHtml(s) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

// ── Render ────────────────────────────────────────────────────────────────────
function render() {
  const list  = document.getElementById('todo-list');
  const empty = document.getElementById('empty');
  const badge = document.getElementById('count-badge');

  let visible = todos;
  if (activeFilter === 'pending') visible = todos.filter(t => !t.completed);
  if (activeFilter === 'done')    visible = todos.filter(t => t.completed);

  badge.textContent = `${todos.length} task${todos.length !== 1 ? 's' : ''}`;
  list.innerHTML = '';

  if (visible.length === 0) {
    empty.style.display = 'flex';
    return;
  }
  empty.style.display = 'none';

  visible.forEach(t => {
    const card = document.createElement('div');
    card.className = `todo-card${t.completed ? ' done' : ''}`;
    card.dataset.priority = t.priority;
    card.dataset.id = t.id;

    card.innerHTML = `
      <div class="todo-check" data-id="${t.id}" title="Toggle done"></div>
      <div class="todo-content">
        <div class="todo-title">${escHtml(t.title)}</div>
        ${t.description ? `<div class="todo-desc">${escHtml(t.description)}</div>` : ''}
        <div class="todo-meta">
          <span class="priority-tag ${t.priority}">${t.priority}</span>
          <span class="todo-id">#${t.id}</span>
        </div>
      </div>
      <div class="todo-actions">
        <button class="action-btn edit-btn" data-id="${t.id}" title="Edit">✎</button>
        <button class="action-btn del"      data-id="${t.id}" title="Delete">✕</button>
      </div>
    `;
    list.appendChild(card);
  });
}

// ── Load ──────────────────────────────────────────────────────────────────────
async function load() {
  todos = await api.getAll();
  render();
}

// ── Add task (POST) ───────────────────────────────────────────────────────────
document.getElementById('btn-add').addEventListener('click', async () => {
  const title = document.getElementById('inp-title').value.trim();
  if (!title) { toast('Title is required.'); return; }

  const body = {
    title,
    description: document.getElementById('inp-desc').value.trim(),
    priority:    document.getElementById('inp-priority').value,
  };

  const created = await api.post(body);
  if (created.detail) { toast(created.detail); return; }

  todos.unshift(created);
  render();
  document.getElementById('inp-title').value    = '';
  document.getElementById('inp-desc').value     = '';
  document.getElementById('inp-priority').value = 'medium';
  toast('Task added.');
});

// ── List interactions ─────────────────────────────────────────────────────────
document.getElementById('todo-list').addEventListener('click', async e => {
  // Toggle done (PATCH)
  if (e.target.classList.contains('todo-check')) {
    const id   = +e.target.dataset.id;
    const todo = todos.find(t => t.id === id);
    const updated = await api.patch(id, { completed: !todo.completed });
    if (updated.detail) { toast(updated.detail); return; }
    Object.assign(todo, updated);
    render();
    toast(updated.completed ? 'Marked done.' : 'Marked pending.');
    return;
  }

  // Open edit
  if (e.target.classList.contains('edit-btn')) {
    openEdit(+e.target.dataset.id);
    return;
  }

  // Delete (DELETE)
  if (e.target.classList.contains('del')) {
    const id = +e.target.dataset.id;
    await api.delete(id);
    todos = todos.filter(t => t.id !== id);
    if (editingId === id) closeEdit();
    render();
    toast('Task deleted.');
  }
});

// ── Edit (PUT) ────────────────────────────────────────────────────────────────
function openEdit(id) {
  const todo = todos.find(t => t.id === id);
  if (!todo) return;
  editingId = id;
  document.getElementById('edit-title').value    = todo.title;
  document.getElementById('edit-desc').value     = todo.description || '';
  document.getElementById('edit-priority').value = todo.priority;
  document.getElementById('edit-panel').classList.add('open');
}

function closeEdit() {
  editingId = null;
  document.getElementById('edit-panel').classList.remove('open');
}

document.getElementById('btn-cancel-edit').addEventListener('click', closeEdit);

document.getElementById('btn-save-edit').addEventListener('click', async () => {
  if (!editingId) return;
  const todo = todos.find(t => t.id === editingId);
  const body = {
    title:       document.getElementById('edit-title').value.trim(),
    description: document.getElementById('edit-desc').value.trim(),
    completed:   todo.completed,
    priority:    document.getElementById('edit-priority').value,
  };
  if (!body.title) { toast('Title is required.'); return; }

  const updated = await api.put(editingId, body);
  if (updated.detail) { toast(updated.detail); return; }
  Object.assign(todo, updated);
  render();
  closeEdit();
  toast('Task updated.');
});

// ── Filters ───────────────────────────────────────────────────────────────────
document.querySelectorAll('.filter-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    activeFilter = btn.dataset.filter;
    render();
  });
});

// ── Logout ────────────────────────────────────────────────────────────────────
document.getElementById('btn-logout').addEventListener('click', () => {
  localStorage.removeItem('token');
  window.location.href = '/static/login.html';
});

// ── Enter key on title ────────────────────────────────────────────────────────
document.getElementById('inp-title').addEventListener('keydown', e => {
  if (e.key === 'Enter') document.getElementById('btn-add').click();
});

load();