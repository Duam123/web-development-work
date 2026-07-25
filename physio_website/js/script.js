// Restore Motion Physiotherapy — shared interactions

document.addEventListener('DOMContentLoaded', function () {

  var toggle = document.querySelector('.nav-toggle');
  var links = document.querySelector('.nav-links');
  if (toggle && links) {
    toggle.addEventListener('click', function () { links.classList.toggle('open'); });
  }

  // ---- Services page: tab switching ----
  var tabs = document.querySelectorAll('.service-tab');
  if (tabs.length) {
    tabs.forEach(function (tab) {
      tab.addEventListener('click', function () {
        var target = tab.getAttribute('data-target');
        tabs.forEach(function (t) { t.classList.remove('active'); });
        document.querySelectorAll('.service-panel').forEach(function (p) { p.classList.remove('active'); });
        tab.classList.add('active');
        var panel = document.getElementById(target);
        if (panel) panel.classList.add('active');
      });
    });
  }

  // ---- FAQ accordion ----
  document.querySelectorAll('.faq-item').forEach(function (item) {
    var q = item.querySelector('.faq-q');
    if (!q) return;
    q.addEventListener('click', function () {
      var wasOpen = item.classList.contains('open');
      document.querySelectorAll('.faq-item').forEach(function (i) { i.classList.remove('open'); });
      if (!wasOpen) item.classList.add('open');
    });
  });

  // ---- Contact / appointment form ----
  var form = document.getElementById('appointmentForm');
  if (form) {
    var params = new URLSearchParams(window.location.search);
    var concernParam = params.get('condition');
    var concernSelect = document.getElementById('condition');
    if (concernParam && concernSelect) {
      Array.from(concernSelect.options).forEach(function (opt) {
        if (opt.value === concernParam) opt.selected = true;
      });
    }

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var valid = true;
      form.querySelectorAll('[data-required]').forEach(function (field) {
        var wrapper = field.closest('.form-field');
        var value = field.value.trim();
        var fieldValid = value.length > 0;
        if (field.type === 'email' && fieldValid) fieldValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
        if (field.type === 'tel' && fieldValid) fieldValid = value.replace(/[^0-9]/g, '').length >= 7;
        if (wrapper) wrapper.classList.toggle('invalid', !fieldValid);
        if (!fieldValid) valid = false;
      });
      if (!valid) return;
      form.style.display = 'none';
      var success = document.getElementById('formSuccess');
      if (success) success.style.display = 'block';
    });

    form.querySelectorAll('[data-required]').forEach(function (field) {
      field.addEventListener('input', function () {
        var wrapper = field.closest('.form-field');
        if (wrapper) wrapper.classList.remove('invalid');
      });
    });
  }
});
