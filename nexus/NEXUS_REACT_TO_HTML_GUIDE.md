# React → HTML/CSS/JS Conversion Guide
> NEXUS PY NAS — Draft Migration Reference

This guide is your **pattern book** for reading a React `.tsx` component
and rewriting it as plain HTML, CSS, and JavaScript. Follow it whenever
you open a file from `draft/app-react/` and need to port it to `app/`.

---

## The Core Mental Model

React and plain HTML/CSS/JS do the exact same job — they just express
it differently. Every React concept has a direct plain equivalent.
Once you see the pattern once, you can apply it to any component.

```
React Concept          Plain Equivalent
─────────────────────  ──────────────────────────────────
.tsx file              Split into HTML + CSS + JS sections
JSX (<div>)            Normal HTML tags in index.html
className="x"          class="x" in HTML
props                  function parameters in JS
useState               a plain JS variable + update logic
useEffect              fetch() call + setInterval()
Component function     JS function that returns HTML string
conditional render     if/else in JS, show/hide with CSS
.map() list render     forEach loop building innerHTML
onClick handler        addEventListener('click', fn)
import from lucide     Unicode symbol or inline SVG
```

---

---

# PATTERN 1 — JSX to HTML
## Converting Component Structure

React JSX looks like HTML but lives inside a function.
Pull the JSX out and put it directly in your HTML file.

### React version (TaskList.tsx)
```tsx
export default function TaskList() {
  return (
    <div className="task-panel">
      <div className="task-panel__head">
        <h2 className="task-panel__title">Downloads</h2>
        <button className="btn btn--primary">+ Add</button>
      </div>
      <ul className="task-list" id="task-list">
        {/* items injected by JS */}
      </ul>
    </div>
  );
}
```

### Plain HTML equivalent (index.html)
```html
<!-- Same structure, pulled out of the function, class not className -->
<div class="task-panel">
  <div class="task-panel__head">
    <h2 class="task-panel__title">Downloads</h2>
    <button class="btn btn--primary" id="btn-add-task">+ Add</button>
  </div>
  <ul class="task-list" id="task-list">
    <!-- items injected by JS -->
  </ul>
</div>
```

**Rules:**
- `className` → `class`
- `htmlFor` → `for`
- `{/* comment */}` → `<!-- comment -->`
- Self-closing tags like `<input />` → `<input>` (optional in HTML5)
- Everything else is identical

---

---

# PATTERN 2 — useState to JS Variables
## Converting State

`useState` is just a variable that triggers a re-render when changed.
In plain JS there's no auto re-render — you update the variable AND
manually update the DOM yourself.

### React version
```tsx
const [downloadLink, setDownloadLink] = useState('');
const [isAddOpen, setIsAddOpen]       = useState(false);
const [tasks, setTasks]               = useState([]);

// Changing state auto-updates the UI
setIsAddOpen(true);   // React re-renders automatically
```

### Plain JS equivalent
```javascript
// Plain variables — no magic re-render
let downloadLink = '';
let isAddOpen    = false;
let tasks        = [];

// You change the variable AND manually update the DOM
function openAddPanel() {
  isAddOpen = true;
  document.getElementById('add-panel').classList.remove('hidden');
}

function closeAddPanel() {
  isAddOpen = false;
  document.getElementById('add-panel').classList.add('hidden');
}
```

**The pattern:** every `setX(value)` call in React becomes two things
in plain JS — update the variable, then manually update the DOM element.

---

---

# PATTERN 3 — useEffect to fetch + setInterval
## Converting Data Fetching

`useEffect` with an empty `[]` dependency = "run once on page load."
`useEffect` with a `setInterval` inside = "run repeatedly."

### React version
```tsx
const [stats, setStats] = useState(null);

// Run once on mount
useEffect(() => {
  fetch('/api/overview')
    .then(r => r.json())
    .then(data => setStats(data));
}, []);

// Auto-refresh every 30 seconds
useEffect(() => {
  const timer = setInterval(() => {
    fetch('/api/overview')
      .then(r => r.json())
      .then(data => setStats(data));
  }, 30000);
  return () => clearInterval(timer);   // cleanup
}, []);
```

### Plain JS equivalent
```javascript
let stats = null;

// Run once on page load
async function loadStats() {
  const res  = await fetch('/api/overview');
  stats      = await res.json();
  renderStats();   // manually update the DOM after fetch
}

// Auto-refresh every 30 seconds
loadStats();
setInterval(loadStats, 30000);

// Cleanup isn't needed in plain JS for simple cases
// (page reload clears all intervals automatically)
```

---

---

# PATTERN 4 — .map() to forEach + innerHTML
## Converting List Rendering

React uses `.map()` inside JSX to render lists.
Plain JS uses a loop to build HTML strings and injects them.

### React version
```tsx
{tasks.map(task => (
  <li key={task.id} className="task-item">
    <span className="task-name">{task.name}</span>
    <span className={`badge badge--${task.status}`}>{task.status}</span>
    <button onClick={() => onPauseTask(task.id)}>Pause</button>
  </li>
))}
```

### Plain JS equivalent
```javascript
function renderTasks(tasks) {
  const list = document.getElementById('task-list');

  if (!tasks.length) {
    list.innerHTML = '<li class="empty">No tasks yet.</li>';
    return;
  }

  // Build HTML string with template literals
  list.innerHTML = tasks.map(task => `
    <li class="task-item" data-id="${task.id}">
      <span class="task-name">${task.name}</span>
      <span class="badge badge--${task.status}">${task.status}</span>
      <button class="btn-pause" data-id="${task.id}">Pause</button>
    </li>
  `).join('');

  // Attach events AFTER injecting HTML (important)
  list.querySelectorAll('.btn-pause').forEach(btn => {
    btn.addEventListener('click', () => {
      const id = btn.dataset.id;
      pauseTask(id);
    });
  });
}
```

**Important rule:** Always attach event listeners AFTER setting
`innerHTML` — the old elements are destroyed and replaced each time.

---

---

# PATTERN 5 — Conditional Rendering to show/hide
## Converting if/else UI logic

React uses ternary operators and && to show/hide parts of the UI.
Plain JS toggles a CSS class or sets display style.

### React version
```tsx
{isAddOpen && (
  <div className="add-form">
    <input value={downloadLink} onChange={e => setDownloadLink(e.target.value)} />
    <button onClick={handleSubmit}>Add</button>
  </div>
)}

{tasks.length === 0
  ? <p className="empty">No tasks yet.</p>
  : <TaskList tasks={tasks} />
}
```

### Plain JS equivalent
```javascript
// In HTML — both elements exist, one is hidden
// <div class="add-form hidden" id="add-form"> ... </div>
// <p class="empty" id="empty-msg">No tasks yet.</p>

function toggleAddForm(open) {
  const form = document.getElementById('add-form');
  form.classList.toggle('hidden', !open);
}

function updateEmptyState(tasks) {
  const msg  = document.getElementById('empty-msg');
  const list = document.getElementById('task-list');
  msg.classList.toggle('hidden',  tasks.length > 0);
  list.classList.toggle('hidden', tasks.length === 0);
}
```

```css
/* In style.css — the hidden utility class */
.hidden { display: none; }
```

---

---

# PATTERN 6 — Props to Function Parameters
## Converting Component Props

Props are just inputs to a component. In plain JS they become
parameters of a render function.

### React version
```tsx
interface StatCardProps {
  label:  string;
  value:  number;
  unit:   string;
  alert?: boolean;
}

function StatCard({ label, value, unit, alert }: StatCardProps) {
  return (
    <div className={`stat-card ${alert ? 'stat-card--alert' : ''}`}>
      <span className="stat-card__label">{label}</span>
      <span className="stat-card__value">{value}{unit}</span>
    </div>
  );
}

// Used as:
<StatCard label="CPU Load" value={19} unit="%" alert={false} />
<StatCard label="RAM"      value={87} unit="%" alert={true}  />
```

### Plain JS equivalent
```javascript
// Same idea — a function that returns an HTML string
function statCardHTML(label, value, unit, alert = false) {
  const alertClass = alert ? 'stat-card--alert' : '';
  return `
    <div class="stat-card ${alertClass}">
      <span class="stat-card__label">${label}</span>
      <span class="stat-card__value">${value}${unit}</span>
    </div>
  `;
}

// Used as:
document.getElementById('stats-grid').innerHTML = `
  ${statCardHTML('CPU Load', 19, '%', false)}
  ${statCardHTML('RAM',      87, '%', true)}
`;
```

---

---

# PATTERN 7 — Lucide Icons to Plain Alternatives
## Replacing Icon Imports

React uses lucide-react icon components. In plain HTML you have
three options — use the CDN, use Unicode symbols, or use inline SVG.

### React version
```tsx
import { Download, CheckCircle, AlertCircle, RefreshCw } from 'lucide-react';

// Used as JSX components
<Download className="w-5 h-5 text-blue-400" />
<CheckCircle className="w-5 h-5 text-emerald-400" />
```

### Option A — Lucide CDN (easiest, keeps same icons)
```html
<!-- Add to <head> in index.html -->
<script src="https://unpkg.com/lucide@latest/dist/umd/lucide.js"></script>
```
```html
<!-- Use anywhere in HTML -->
<i data-lucide="download"      class="icon icon--blue"></i>
<i data-lucide="check-circle"  class="icon icon--green"></i>
<i data-lucide="alert-circle"  class="icon icon--amber"></i>
<i data-lucide="refresh-cw"    class="icon icon--indigo"></i>
```
```javascript
// Call once after page loads to render all icons
lucide.createIcons();

// Call again after dynamic HTML injection
function renderTasks(tasks) {
  document.getElementById('task-list').innerHTML = tasks.map(t => `
    <li>
      <i data-lucide="download" class="icon"></i>
      ${t.name}
    </li>
  `).join('');
  lucide.createIcons();   // ← re-render icons after innerHTML update
}
```

### Option B — Unicode fallback (no CDN needed)
```javascript
// Simple mapping — no library at all
const ICONS = {
  download: '↓',
  backup:   '✓',
  raid:     '⚠',
  sync:     '↻',
  folder:   '📁',
  file:     '📄',
};

// Used inline in template literals
`<span class="icon">${ICONS[task.type]}</span> ${task.name}`
```

---

---

# FULL EXAMPLE — TaskList Fully Converted

## Original React (TaskList.tsx) → Plain HTML/CSS/JS

### index.html (structure)
```html
<!-- Task Manager Panel -->
<div class="task-panel">
  <div class="task-panel__head">
    <span class="panel-icon">↓</span>
    <h2 class="panel-title">Downloads & Tasks</h2>
    <button class="btn btn--primary" id="btn-open-add">+ Add Task</button>
  </div>

  <!-- Add task form (hidden by default) -->
  <div class="add-form hidden" id="add-form">
    <input
      class="form-input"
      id="input-link"
      type="text"
      placeholder="Paste download link or folder path..."
    />
    <div class="add-form__actions">
      <button class="btn btn--primary"  id="btn-submit-task">Add</button>
      <button class="btn btn--ghost"    id="btn-cancel-add">Cancel</button>
    </div>
  </div>

  <!-- Task list -->
  <ul class="task-list" id="task-list">
    <li class="task-empty" id="task-empty">No tasks yet. Add one above.</li>
  </ul>
</div>
```

### style.css (styles — same visual as React version)
```css
.task-panel {
  background:    var(--bg-panel);
  border:        1px solid var(--border);
  border-radius: 6px;
  overflow:      hidden;
}

.task-panel__head {
  display:         flex;
  align-items:     center;
  gap:             8px;
  padding:         12px 16px;
  border-bottom:   1px solid var(--border);
  background:      var(--bg-panel-alt);
}

.panel-title { flex: 1; font-size: 13px; font-weight: 700; }

.add-form {
  padding:        12px 16px;
  border-bottom:  1px solid var(--border);
  display:        flex;
  flex-direction: column;
  gap:            8px;
}

.add-form__actions { display: flex; gap: 8px; }

.task-list { list-style: none; padding: 0; margin: 0; }

.task-item {
  display:       flex;
  align-items:   center;
  gap:           10px;
  padding:       10px 16px;
  border-bottom: 1px solid var(--border);
}

.task-item:last-child { border-bottom: none; }

.task-name  { flex: 1; font-size: 13px; }
.task-empty { padding: 24px; text-align: center; color: var(--text-dim); }

.badge {
  font-size:     10px;
  font-weight:   700;
  padding:       2px 8px;
  border-radius: 20px;
  letter-spacing: 0.06em;
}

.badge--running   { background: rgba(0,200,255,0.15); color: var(--cyan);  }
.badge--paused    { background: rgba(255,215,64,0.15); color: var(--yellow); }
.badge--completed { background: rgba(0,230,118,0.15); color: var(--green); }
.badge--error     { background: rgba(255,82,82,0.15);  color: var(--red);  }

.hidden { display: none; }
```

### scripts/tasks.js (logic — replaces useState + handlers)
```javascript
// ── State ──────────────────────────────────────────────────
let tasks        = [];
let isAddOpen    = false;
let downloadLink = '';

// ── Render ─────────────────────────────────────────────────
function renderTasks() {
  const list  = document.getElementById('task-list');
  const empty = document.getElementById('task-empty');

  if (!tasks.length) {
    list.innerHTML = '';
    empty.classList.remove('hidden');
    return;
  }

  empty.classList.add('hidden');
  list.innerHTML = tasks.map(task => `
    <li class="task-item" data-id="${task.id}">
      <span class="task-icon">${getTaskIcon(task.type)}</span>
      <span class="task-name">${task.name}</span>
      <span class="badge badge--${task.status}">${task.status}</span>
      <button class="btn btn--ghost btn-pause"  data-id="${task.id}">⏸</button>
      <button class="btn btn--ghost btn-cancel" data-id="${task.id}">✕</button>
    </li>
  `).join('');

  // Reattach events after innerHTML update
  list.querySelectorAll('.btn-pause').forEach(btn =>
    btn.addEventListener('click', () => pauseTask(btn.dataset.id))
  );
  list.querySelectorAll('.btn-cancel').forEach(btn =>
    btn.addEventListener('click', () => cancelTask(btn.dataset.id))
  );

  lucide.createIcons();
}

// ── Icon helper ────────────────────────────────────────────
function getTaskIcon(type) {
  const icons = {
    download: '↓',
    backup:   '✓',
    raid:     '⚠',
    sync:     '↻',
  };
  return icons[type] || '↓';
}

// ── Actions ────────────────────────────────────────────────
function addTask(link) {
  tasks.push({
    id:     Date.now().toString(),
    type:   'download',
    name:   link,
    status: 'running',
  });
  renderTasks();
}

function pauseTask(id) {
  tasks = tasks.map(t =>
    t.id === id ? { ...t, status: t.status === 'paused' ? 'running' : 'paused' } : t
  );
  renderTasks();
}

function cancelTask(id) {
  tasks = tasks.filter(t => t.id !== id);
  renderTasks();
}

// ── Form handlers (replaces handleSubmit) ──────────────────
function openAddForm() {
  isAddOpen = true;
  document.getElementById('add-form').classList.remove('hidden');
  document.getElementById('input-link').focus();
}

function closeAddForm() {
  isAddOpen = false;
  downloadLink = '';
  document.getElementById('add-form').classList.add('hidden');
  document.getElementById('input-link').value = '';
}

function handleSubmit() {
  const link = document.getElementById('input-link').value.trim();
  if (!link) return;
  addTask(link);
  closeAddForm();
}

// ── Event listeners ────────────────────────────────────────
document.getElementById('btn-open-add').addEventListener('click', openAddForm);
document.getElementById('btn-submit-task').addEventListener('click', handleSubmit);
document.getElementById('btn-cancel-add').addEventListener('click', closeAddForm);

// Submit on Enter key
document.getElementById('input-link').addEventListener('keydown', e => {
  if (e.key === 'Enter') handleSubmit();
});

// ── Init ───────────────────────────────────────────────────
renderTasks();
```

---

---

# Quick Reference Card

Stick this at the top of every conversion session:

```
WHEN YOU SEE IN REACT          WRITE IN PLAIN JS
──────────────────────────     ────────────────────────────────────
useState(x)                    let x = value
setState(newVal)               x = newVal; renderX();
useEffect(() => {}, [])        call function on DOMContentLoaded
useEffect with setInterval     setInterval(fn, ms)
component.map(item => <X />)   items.map(i => `<li>${i.name}</li>`).join('')
onClick={fn}                   addEventListener('click', fn)
className="x"                  class="x"
{condition && <X />}           el.classList.toggle('hidden', !condition)
{a ? <X/> : <Y/>}             if(a) showX(); else showY();
props.value                    function parameter
import Icon from lucide        lucide CDN + data-lucide="icon-name"
../types NasTask interface      plain JS object, no type needed
```

---

## Git Commit After Each Component Conversion

```bash
git add .
git commit -m "refactor: convert [ComponentName] from React to plain HTML/CSS/JS"
```

---

*NEXUS PY NAS — Draft Migration Guide*
*React drafts preserved in: draft/app-react/*
*Active plain frontend in: app/*
