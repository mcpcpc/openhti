(() => {
  'use strict';

  /* ── Theme ─────────────────────────────────────────────── */
  const getStored = () => localStorage.getItem('app-theme') || 'auto';
  const setStored = t  => localStorage.setItem('app-theme', t);

  function resolveTheme(t) {
    return t === 'auto'
      ? (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')
      : t;
  }

  function applyTheme(t) {
    document.documentElement.setAttribute('data-theme', resolveTheme(t));
    document.documentElement.setAttribute('data-stored-theme', t);
  }

  // Apply immediately (before paint) to avoid flash
  applyTheme(getStored());

  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
    if (getStored() === 'auto') applyTheme('auto');
  });

  window.cycleTheme = () => {
    const order = { light: 'dark', dark: 'auto', auto: 'light' };
    const next = order[getStored()] || 'light';
    setStored(next);
    applyTheme(next);
    updateThemeLabel();
  };

  function updateThemeLabel() {
    const el = document.getElementById('theme-label');
    if (el) el.textContent = { light: 'Light', dark: 'Dark', auto: 'Auto' }[getStored()] || 'Auto';
  }

  /* ── Modal system ───────────────────────────────────────── */
  window.showModal = id => {
    const m = document.getElementById(id);
    if (!m) return;
    m.classList.add('active');
    document.body.classList.add('modal-open');
  };

  window.hideModal = id => {
    const m = document.getElementById(id);
    if (!m) return;
    m.classList.remove('active');
    document.body.classList.remove('modal-open');
  };

  /* ── Sidebar / bottom-nav drawer ───────────────────────── */
  let sidebar, overlay, menuBtn;

  function openSidebar() {
    if (!sidebar) return;
    sidebar.classList.add('open');
    if (overlay) overlay.classList.add('visible');
    document.body.style.overflow = 'hidden';
  }

  function closeSidebar() {
    if (!sidebar) return;
    sidebar.classList.remove('open');
    if (overlay) overlay.classList.remove('visible');
    document.body.style.overflow = '';
  }

  /* ── Filter dropdown ────────────────────────────────────── */
  window.toggleFilter = (btn) => {
    const menu = btn.nextElementSibling;
    if (!menu) return;
    const isOpen = menu.classList.contains('open');
    // close all
    document.querySelectorAll('.filter-menu.open').forEach(m => m.classList.remove('open'));
    if (!isOpen) menu.classList.add('open');
  };

  /* ── Select-all checkboxes ──────────────────────────────── */
  window.selectAll = source => {
    const form = source.closest('form');
    if (!form) return;
    form.querySelectorAll('input[type="checkbox"]').forEach(cb => {
      cb.checked = source.checked;
    });
  };

  /* ── Accordion toggle (test results) ────────────────────── */
  document.addEventListener('click', e => {
    /* Backdrop clicks → close modal */
    if (e.target.classList.contains('modal-backdrop')) {
      const m = e.target.closest('.modal');
      if (m) hideModal(m.id);
      return;
    }
    /* Accordion buttons */
    const accBtn = e.target.closest('.accordion-button');
    if (accBtn) {
      const collapse = accBtn.closest('.accordion-item')?.querySelector('.accordion-collapse');
      if (collapse) collapse.classList.toggle('show');
    }
    /* Filter dropdown close when clicking outside */
    if (!e.target.closest('.filter-dropdown')) {
      document.querySelectorAll('.filter-menu.open').forEach(m => m.classList.remove('open'));
    }
  });

  /* Escape key → close modal or sidebar */
  document.addEventListener('keydown', e => {
    if (e.key !== 'Escape') return;
    document.querySelectorAll('.modal.active').forEach(m => hideModal(m.id));
    closeSidebar();
  });

  /* ── DOMContentLoaded ───────────────────────────────────── */
  document.addEventListener('DOMContentLoaded', () => {
    sidebar  = document.getElementById('sidebar');
    overlay  = document.getElementById('sidebar-overlay');
    menuBtn  = document.getElementById('menu-toggle');

    if (menuBtn) menuBtn.addEventListener('click', () => {
      sidebar?.classList.contains('open') ? closeSidebar() : openSidebar();
    });
    if (overlay) overlay.addEventListener('click', closeSidebar);

    updateThemeLabel();
  });
})();
