const sections = document.querySelectorAll('.table-section');
const links = document.querySelectorAll('#table-list a');
const mainSearch = document.getElementById('main-search');
const sideSearch = document.getElementById('sidebar-search-input');
const keysOnly = document.getElementById('keys-only-checkbox');
const countEl = document.getElementById('sidebar-count');
const btnAll = document.getElementById('btn-show-all');

let pinnedTable = null;

function normTxt(s) { return s.toLowerCase(); }

function applyFilters() {
  const q = normTxt(mainSearch.value.trim());
  const sq = normTxt(sideSearch.value.trim());
  const ko = keysOnly.checked;
  let visible = 0;

  sections.forEach(sec => {
    const name = sec.dataset.name;
    // Pinned: only show the pinned table
    if (pinnedTable !== null && name !== pinnedTable) {
      sec.classList.add('hidden');
      return;
    }
    // Sidebar text filter
    if (sq && !name.includes(sq)) {
      sec.classList.add('hidden');
    } else {
      sec.classList.remove('hidden');
      const rows = sec.querySelectorAll('tr.field-row');
      let anyVisible = false;
      rows.forEach(row => {
        const hide = (ko && !row.dataset.key) || (q && !row.dataset.search.includes(q));
        row.classList.toggle('hidden-row', hide);
        if (!hide) anyVisible = true;
      });
      if (q && !anyVisible) sec.classList.add('hidden');
      else visible++;
    }
  });

  links.forEach(a => {
    const name = a.dataset.name;
    a.style.display = (!sq || name.includes(sq)) ? '' : 'none';
    a.classList.toggle('active', pinnedTable === name);
  });

  btnAll.classList.toggle('visible', pinnedTable !== null);
  btnAll.textContent = pinnedTable ? `\u00d7 ${pinnedTable}` : '';
  countEl.textContent = `${visible} / ${sections.length} tables`;
}

// Sidebar link: click to pin, click again to unpin
links.forEach(link => {
  link.addEventListener('click', ev => {
    ev.preventDefault();
    const name = link.dataset.name;
    pinnedTable = (pinnedTable === name) ? null : name;
    history.pushState(null, '', pinnedTable ? '?q=' + encodeURIComponent(pinnedTable) : location.pathname);
    applyFilters();
    if (pinnedTable) {
      const sec = document.getElementById(pinnedTable);
      if (sec) sec.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
});

// "Back to all" button
btnAll.addEventListener('click', () => {
  pinnedTable = null;
  history.pushState(null, '', location.pathname);
  applyFilters();
});

// Navigate to a table via ref-link
function gotoTable(name) {
  pinnedTable = name;
  sideSearch.value = '';
  history.pushState(null, '', '?q=' + encodeURIComponent(name));
  applyFilters();
  const sec = document.getElementById(name);
  if (sec) setTimeout(() => sec.scrollIntoView({ behavior: 'smooth', block: 'start' }), 30);
  const sideLink = document.querySelector(`#table-list a[data-name="${name}"]`);
  if (sideLink) sideLink.scrollIntoView({ block: 'nearest' });
}

// Reference link clicks (delegated)
document.addEventListener('click', ev => {
  const a = ev.target.closest('a.ref-link[data-goto]');
  if (!a) return;
  ev.preventDefault();
  gotoTable(a.dataset.goto);
});

// Row selection: click = exclusive, shift+click = toggle
document.addEventListener('click', ev => {
  if (ev.target.closest('a.ref-link')) return; // ref link handled above
  const row = ev.target.closest('tr.field-row');
  if (!row) return;
  if (ev.ctrlKey || ev.metaKey) {
    row.classList.toggle('selected');
  } else {
    const already = row.classList.contains('selected');
    document.querySelectorAll('tr.field-row.selected').forEach(r => r.classList.remove('selected'));
    if (!already) row.classList.add('selected');
  }
});

// Sidebar scroll-spy (only when not pinned)
const observer = new IntersectionObserver(entries => {
  if (pinnedTable) return;
  entries.forEach(e => {
    if (e.isIntersecting) {
      const id = e.target.id;
      links.forEach(a => a.classList.toggle('active', a.dataset.name === id));
    }
  });
}, { threshold: 0.1 });
sections.forEach(s => observer.observe(s));

mainSearch.addEventListener('input', applyFilters);
sideSearch.addEventListener('input', applyFilters);
keysOnly.addEventListener('change', applyFilters);

countEl.textContent = `${sections.length} / ${sections.length} tables`;

// ?q= URL param: exact table name → pin it; anything else → fill sidebar filter
function handleQuery() {
  const q = new URLSearchParams(location.search).get('q') || '';
  const sec = q && document.getElementById(q);
  if (sec && sec.classList.contains('table-section')) {
    pinnedTable = q;
    applyFilters();
    sec.scrollIntoView({ block: 'start' });
    const sideLink = document.querySelector(`#table-list a[data-name="${q}"]`);
    if (sideLink) sideLink.scrollIntoView({ block: 'nearest' });
  } else {
    pinnedTable = null;
    sideSearch.value = q;
    applyFilters();
  }
}
handleQuery();
window.addEventListener('popstate', handleQuery);

// Navigate to table from URL hash (e.g. #projectiles_tables)
function handleHash() {
  const hash = location.hash.slice(1);
  if (!hash) return;
  const sec = document.getElementById(hash);
  if (!sec || !sec.classList.contains('table-section')) return;
  pinnedTable = hash;
  applyFilters();
  sec.scrollIntoView({ block: 'start' });
  const sideLink = document.querySelector(`#table-list a[data-name="${hash}"]`);
  if (sideLink) sideLink.scrollIntoView({ block: 'nearest' });
}
handleHash();
window.addEventListener('hashchange', handleHash);

// Keep --topbar-h in sync with actual rendered height
const topbarEl = document.getElementById('topbar');
new ResizeObserver(() => {
  document.documentElement.style.setProperty('--topbar-h', topbarEl.offsetHeight + 'px');
}).observe(topbarEl);