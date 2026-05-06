// ── State ─────────────────────────────────────────────────────────
const state = {
  token: localStorage.getItem('mp_token') || null,
  user: null,
  currentPatient: null
};

// ── API ───────────────────────────────────────────────────────────
const BASE = '';

async function apiFetch(path, { method = 'GET', body, form } = {}) {
  const headers = {};
  if (state.token) headers['Authorization'] = `Bearer ${state.token}`;

  let bodyPayload;
  if (form) {
    bodyPayload = form;
  } else if (body !== undefined) {
    headers['Content-Type'] = 'application/json';
    bodyPayload = JSON.stringify(body);
  }

  const res = await fetch(BASE + path, { method, headers, body: bodyPayload });

  if (res.status === 401) {
    logout();
    throw new Error('Sesija je istekla. Prijavite se ponovo.');
  }

  const text = await res.text();
  let data;
  try { data = JSON.parse(text); } catch { data = text; }

  if (!res.ok) {
    const msg = (data && data.detail) || (data && data.message) || `HTTP ${res.status}`;
    throw new Error(typeof msg === 'string' ? msg : JSON.stringify(msg));
  }
  return data;
}

// ── Auth ──────────────────────────────────────────────────────────
async function login(username, password) {
  const form = new FormData();
  form.append('username', username);
  form.append('password', password);
  const data = await apiFetch('/token', { method: 'POST', form });
  state.token = data;
  localStorage.setItem('mp_token', state.token);
}

function logout() {
  state.token = null;
  state.user = null;
  localStorage.removeItem('mp_token');
  showScreen('login');
}

// ── Role detection (from /api/user/account `role` field) ──────────
function isPatient(user) {
  return (user.role || '').toLowerCase() === 'patient';
}

// ── Screen / Page routing ─────────────────────────────────────────
function showScreen(name) {
  document.querySelectorAll('.screen').forEach(s => {
    s.classList.toggle('active', s.id === `screen-${name}`);
    s.classList.toggle('hidden', s.id !== `screen-${name}`);
  });
}

function showPage(name) {
  document.querySelectorAll('.page').forEach(p => {
    p.classList.toggle('active', p.id === `page-${name}`);
  });
  document.querySelectorAll('.nav-item').forEach(a => {
    a.classList.toggle('active', a.dataset.page === name);
  });
}

// ── Toast ─────────────────────────────────────────────────────────
let toastTimer;
function showToast(msg, duration = 3200) {
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.classList.remove('hidden');
  requestAnimationFrame(() => el.classList.add('show'));
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    el.classList.remove('show');
    setTimeout(() => el.classList.add('hidden'), 250);
  }, duration);
}

// ── Account page ──────────────────────────────────────────────────
async function loadAccount() {
  const area = document.getElementById('account-form-area');
  area.innerHTML = '<div class="skeleton-block"></div>';

  try {
    const u = await apiFetch('/api/user/account');
    state.user = u;
    document.getElementById('page-account').classList.remove('hidden');
    const fields = [
      { key: 'name',    label: 'Ime',           type: 'text' },
      { key: 'surname', label: 'Prezime',        type: 'text' },
      { key: 'email',   label: 'E-mail',         type: 'email' },
      { key: 'mobile',  label: 'Mobitel',        type: 'tel' },
      { key: 'username',label: 'Korisničko ime', type: 'text', readonly: true },
    ];

    // mbo je prisutan samo kod pacijenata (UserPersonal schema)
    if (u.mbo != null) {
      fields.unshift({ key: 'mbo', label: 'MBO', type: 'text', readonly: true });
    }

    area.innerHTML = '';
    fields.forEach(f => {
      const wrap = document.createElement('div');
      wrap.className = 'field';
      wrap.innerHTML = `
        <label>${f.label}</label>
        <input type="${f.type}" id="acc-${f.key}" value="${escHtml(u[f.key] ?? '')}"
          ${f.readonly ? 'readonly style="background:var(--bg);color:var(--text-muted)"' : ''} />
      `;
      area.appendChild(wrap);
    });

    const saveBtn = document.createElement('button');
    saveBtn.className = 'btn btn-primary';
    saveBtn.textContent = 'Spremi promjene';
    saveBtn.addEventListener('click', saveAccount);
    area.appendChild(saveBtn);

    document.getElementById('toggle-sms').checked   = !!u.receive_by_sms;
    document.getElementById('toggle-email').checked = !!u.receive_by_email;

  } catch (err) {
    area.innerHTML = `<p class="alert alert-error">${escHtml(err.message)}</p>`;
  }
}

async function saveAccount() {
  // UpdateBody: mbo, username, password, email, mobile, name, surname, receive_by_sms, receive_by_email
  // Šaljemo samo polja koja korisnik može mijenjati
  const body = {};
  ['name','surname','email','mobile'].forEach(k => {
    const el = document.getElementById(`acc-${k}`);
    if (el && el.value.trim() !== '') body[k] = el.value.trim();
  });

  try {
    await apiFetch('/api/user/account/update', { method: 'POST', body });
    showToast('Podatci uspješno ažurirani.');
    await loadAccount();
    refreshSidebarUser();
  } catch (err) {
    showToast(`Greška: ${err.message}`);
  }
}

// ── Notification toggles ──────────────────────────────────────────
document.getElementById('toggle-sms').addEventListener('change', async e => {
  try {
    await apiFetch('/api/user/settings/notifications/sms', {
      method: 'POST', body: { enabled: e.target.checked }
    });
    showToast(e.target.checked ? 'SMS obavijesti uključene.' : 'SMS obavijesti isključene.');
  } catch (err) {
    showToast(`Greška: ${err.message}`);
    e.target.checked = !e.target.checked;
  }
});

document.getElementById('toggle-email').addEventListener('change', async e => {
  try {
    await apiFetch('/api/user/settings/notifications/email', {
      method: 'POST', body: { enabled: e.target.checked }
    });
    showToast(e.target.checked ? 'Email obavijesti uključene.' : 'Email obavijesti isključene.');
  } catch (err) {
    showToast(`Greška: ${err.message}`);
    e.target.checked = !e.target.checked;
  }
});

// ── Patient treatments (patient view) ─────────────────────────────
async function loadPatientTreatments() {
  const list = document.getElementById('treatments-list');
  document.getElementById('page-treatments').classList.remove('hidden');
  list.innerHTML = '<div class="skeleton-block"></div>';
  try {
    const treatments = await apiFetch('/api/patient/treatments');
    renderTreatments(list, treatments, 'card');
  } catch (err) {
    list.innerHTML = `<p class="alert alert-error">${escHtml(err.message)}</p>`;
  }
}

function renderTreatments(container, treatments, style = 'card') {
  document.getElementById('page-patient-lookup').classList.remove('hidden');
  if (!treatments || treatments.length === 0) {
    container.innerHTML = '<p class="empty-state">Nema aktivnih tretmana.</p>';
    return;
  }

  container.innerHTML = '';

  if (style === 'card') {
    treatments.forEach(t => {
      const card = document.createElement('div');
      card.className = 'treatment-card';
      card.innerHTML = `
        <div class="treatment-drug">${escHtml(t.drugName || t.drug_name || '–')}</div>
        <div class="treatment-times">
          ${(t.times || t.schedule || []).map(tm => `<span class="time-chip">${escHtml(tm)}</span>`).join('')}
        </div>
        <div class="treatment-pickup">
          <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
            <rect x=".75" y="1.75" width="11.5" height="10.5" rx="1.5" stroke="currentColor" stroke-width="1.2"/>
            <path d="M4 .75v2M9 .75v2M.75 5h11.5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
          </svg>
          Preuzimanje: <strong>${escHtml(t.pickupDay || t.pickup_day || '–')}</strong>
        </div>
      `;
      container.appendChild(card);
    });
  } else {
    treatments.forEach(t => {
      const row = document.createElement('div');
      row.className = 'treatment-row';
      row.innerHTML = `
        <div style="flex:1">
          <div class="treatment-row-drug">${escHtml(t.drugName || t.drug_name || '–')}</div>
          <div class="treatment-row-times">
            ${(t.times || t.schedule || []).map(tm => `<span class="time-chip">${escHtml(tm)}</span>`).join('')}
          </div>
        </div>
        <div style="font-size:12px;color:var(--text-muted);white-space:nowrap">
          Preuzimanje:<br><strong>${escHtml(t.pickupDay || t.pickup_day || '–')}</strong>
        </div>
      `;
      container.appendChild(row);
    });
  }
}

// ── Patient lookup (provider) ──────────────────────────────────────
document.getElementById('page-patient-lookup').classList.remove('hidden');
document.getElementById('btn-search-patient').addEventListener('click', searchPatient);
document.getElementById('patient-mbo-input').addEventListener('keydown', e => {
  if (e.key === 'Enter') searchPatient();
});

async function searchPatient() {
  const mbo = document.getElementById('patient-mbo-input').value.trim();
  if (!mbo) return;

  const resultEl = document.getElementById('patient-result');
  const notFound = document.getElementById('patient-not-found');
  resultEl.classList.add('hidden');
  notFound.classList.add('hidden');

  try {
    const [patient, treatments] = await Promise.all([
      apiFetch(`/api/provider/patients/${encodeURIComponent(mbo)}`),
      apiFetch(`/api/provider/patients/${encodeURIComponent(mbo)}/treatments`)
    ]);

    state.currentPatient = patient;

    const fullName = `${patient.name || ''} ${patient.surname || ''}`.trim() || '–';
    document.getElementById('patient-name').textContent = fullName;

    const initials = [patient.name, patient.surname]
      .filter(Boolean).map(s => s[0].toUpperCase()).join('');
    document.getElementById('patient-avatar').textContent = initials || '?';

    const badge = document.getElementById('patient-risk-badge');
    if (patient.risky) {
      badge.textContent = '⚠ Rizični pacijent';
      badge.className = 'badge badge-danger';
    } else {
      badge.textContent = 'Niska rizičnost';
      badge.className = 'badge badge-success';
    }

    const details = document.getElementById('patient-details');
    const detailFields = [
      { label: 'MBO',     value: patient.mbo    },
      { label: 'Email',   value: patient.email   },
      { label: 'Mobitel', value: patient.mobile  },
    ];
    details.innerHTML = detailFields.map(f => `
      <div class="patient-detail-item">
        <label>${f.label}</label>
        <span>${escHtml(f.value || '–')}</span>
      </div>
    `).join('');

    const treatList = document.getElementById('patient-treatments-list');
    renderTreatments(treatList, treatments, 'row');

    resultEl.classList.remove('hidden');
  } catch (err) {
    notFound.textContent = err.message || 'Pacijent nije pronađen.';
    notFound.classList.remove('hidden');
  }
}

// ── Prescribe (provider) ───────────────────────────────────────────
// PerscriptionBody: patientMbo, drugName, times, pickupDay (date string YYYY-MM-DD)
document.getElementById('btn-add-time').addEventListener('click', () => addTimeEntry());

function addTimeEntry(value = '') {
  document.getElementById("page-prescribe").classList.remove('hidden');
  const list  = document.getElementById('rx-times-list');
  const entry = document.createElement('div');
  entry.className = 'rx-time-entry';
  entry.innerHTML = `
    <input type="text" placeholder="npr. 08:00" value="${escHtml(value)}" />
    <button class="rx-time-remove" title="Ukloni">
      <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
        <path d="M3 3l8 8M11 3l-8 8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
      </svg>
    </button>
  `;
  entry.querySelector('.rx-time-remove').addEventListener('click', () => entry.remove());
  list.appendChild(entry);
  entry.querySelector('input').focus();
}

document.getElementById('btn-submit-rx').addEventListener('click', submitRx);

async function submitRx() {
  const alertEl = document.getElementById('prescribe-alert');
  alertEl.className = 'alert hidden';

  // Spec koristi patientMbo (malo b), ne patientMBO
  const patientMbo = document.getElementById('rx-mbo').value.trim();
  const drugName   = document.getElementById('rx-drug').value.trim();
  const pickupDay  = document.getElementById('rx-pickup-date').value; // YYYY-MM-DD format
  const times = [...document.querySelectorAll('#rx-times-list .rx-time-entry input')]
    .map(i => i.value.trim()).filter(Boolean);

  if (!patientMbo || !drugName || times.length === 0 || !pickupDay) {
    alertEl.textContent = 'Molimo ispunite sva polja (MBO, lijek, barem jedno vrijeme, dan preuzimanja).';
    alertEl.className = 'alert alert-error';
    return;
  }

  try {
    await apiFetch('/api/provider/perscription', {
      method: 'POST',
      body: { patientMbo, drugName, times, pickupDay }
    });
    showToast('Recept uspješno ispisan.');
    document.getElementById('rx-mbo').value = '';
    document.getElementById('rx-drug').value = '';
    document.getElementById('rx-times-list').innerHTML = '';
    document.getElementById('rx-pickup-date').value = '';
  } catch (err) {
    alertEl.textContent = `Greška: ${err.message}`;
    alertEl.className = 'alert alert-error';
  }
}

// ── Dashboard ──────────────────────────────────────────────────────
async function loadDashboard() {
  const hour     = new Date().getHours();
  const greeting = hour < 12 ? 'Dobro jutro' : hour < 18 ? 'Dobar dan' : 'Dobra večer';
  document.getElementById('dashboard-greeting').textContent =
    `${greeting}${state.user ? ', ' + state.user.name : ''}.`;

  const grid = document.getElementById('dashboard-cards');
  if (!state.user) { grid.innerHTML = ''; return; }

  const pat = isPatient(state.user);
  const cards = pat
    ? [
        { label: 'MBO',     value: state.user.mbo    || '–', sub: 'Matični broj osiguranika' },
        { label: 'Email',   value: state.user.email  || '–', sub: 'Kontakt e-pošta' },
        { label: 'Mobitel', value: state.user.mobile || '–', sub: 'Kontakt broj' },
      ]
    : [
        { label: 'Korisnik', value: state.user.username || '–', sub: 'Korisničko ime' },
        { label: 'Email',    value: state.user.email    || '–', sub: 'Kontakt e-pošta' },
        { label: 'Uloga',    value: state.user.role     || '–', sub: 'Tip korisnika' },
      ];

  grid.innerHTML = cards.map(c => `
    <div class="info-card">
      <div class="info-card-label">${escHtml(c.label)}</div>
      <div class="info-card-value">${escHtml(String(c.value))}</div>
      <div class="info-card-sub">${escHtml(c.sub)}</div>
    </div>
  `).join('');
}

// ── Sidebar user ───────────────────────────────────────────────────
function refreshSidebarUser() {
  const u = state.user;
  if (!u) return;
  const name = [u.name, u.surname].filter(Boolean).join(' ') || u.username || '–';
  document.getElementById('sidebar-user-name').textContent = name;
  document.getElementById('user-avatar-initials').textContent =
    [u.name, u.surname].filter(Boolean).map(s => s[0].toUpperCase()).join('') || '?';

  const pat = isPatient(u);
  document.getElementById('sidebar-user-role').textContent = pat ? 'Pacijent' : 'Liječnik / Farmaceut';
  document.getElementById('nav-provider').style.display = pat ? 'none' : 'flex';
  document.getElementById('nav-patient').style.display  = pat ? 'flex'  : 'none';
}

// ── Navigation ─────────────────────────────────────────────────────
document.querySelectorAll('.nav-item').forEach(a => {
  a.addEventListener('click', e => {
    e.preventDefault();
    navigateTo(a.dataset.page);
  });
});

function navigateTo(page) {
  showPage(page);
  if (page === 'account')        loadAccount();
  if (page === 'treatments')     loadPatientTreatments();
  if (page === 'dashboard')      loadDashboard();
  if (page === 'patient-lookup') {
    document.getElementById('patient-result').classList.add('hidden');
    document.getElementById('patient-not-found').classList.add('hidden');
  }
  if (page === 'prescribe') {
    const list = document.getElementById('rx-times-list');
    if (!list.children.length) addTimeEntry();
  }
}

// ── Login UI ───────────────────────────────────────────────────────
document.getElementById('btn-login').addEventListener('click', handleLogin);
['username','password'].forEach(id =>
  document.getElementById(id).addEventListener('keydown', e => {
    if (e.key === 'Enter') handleLogin();
  })
);

async function handleLogin() {
  const btn     = document.getElementById('btn-login');
  const errorEl = document.getElementById('login-error');
  errorEl.classList.add('hidden');
  btn.disabled = true;
  btn.querySelector('span').textContent = 'Prijava…';

  try {
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    await login(username, password);
    await initApp();
  } catch (err) {
    errorEl.textContent = err.message;
    errorEl.classList.remove('hidden');
    btn.disabled = false;
    btn.querySelector('span').textContent = 'Prijava';
  }
}

document.getElementById('btn-logout').addEventListener('click', logout);

// ── Init ───────────────────────────────────────────────────────────
async function initApp() {
  try {
    state.user = await apiFetch('/api/user/account');
  } catch { return logout(); }

  refreshSidebarUser();
  showScreen('app');
  navigateTo('dashboard');
}

// ── Bootstrap ──────────────────────────────────────────────────────
(function bootstrap() {
  if (state.token) {
    showScreen('app');
    initApp();
  } else {
    showScreen('login');
  }
})();

// ── Utilities ──────────────────────────────────────────────────────
function escHtml(str) {
  return String(str)
    .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
    .replace(/"/g,'&quot;').replace(/'/g,'&#39;');
}
