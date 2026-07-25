// Claria Skin Health — shared interactions

document.addEventListener('DOMContentLoaded', function () {

  // ---- Mobile nav toggle ----
  var toggle = document.querySelector('.nav-toggle');
  var links = document.querySelector('.nav-links');
  if (toggle && links) {
    toggle.addEventListener('click', function () {
      links.classList.toggle('open');
    });
  }

  // ---- Signature diagnostic-scan metric bars (hero) ----
  // Fills each metric bar to its target width shortly after load, so the
  // "scan result" reads as something that just finished analyzing.
  var metricFills = document.querySelectorAll('.metric-fill');
  if (metricFills.length) {
    setTimeout(function () {
      metricFills.forEach(function (fill) {
        var target = fill.getAttribute('data-value') || '0';
        fill.style.width = target + '%';
      });
    }, 600);
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

  // ---- Services page: expandable menu rows ----
  document.querySelectorAll('.menu-row').forEach(function (row) {
    row.addEventListener('click', function () {
      var wrap = row.closest('.menu-row-wrap');
      if (!wrap) return;
      var wasOpen = wrap.classList.contains('open');
      row.classList.toggle('open', !wasOpen);
      wrap.classList.toggle('open', !wasOpen);
    });
  });

  // ---- Contact / appointment form ----
  var form = document.getElementById('appointmentForm');
  if (form) {
    var params = new URLSearchParams(window.location.search);
    var concernParam = params.get('concern');
    var concernSelect = document.getElementById('concern');
    if (concernParam && concernSelect) {
      Array.from(concernSelect.options).forEach(function (opt) {
        if (opt.value === concernParam) opt.selected = true;
      });
    }

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var valid = true;

      var requiredFields = form.querySelectorAll('[data-required]');
      requiredFields.forEach(function (field) {
        var wrapper = field.closest('.form-field');
        var value = field.value.trim();
        var fieldValid = value.length > 0;

        if (field.type === 'email' && fieldValid) {
          fieldValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
        }
        if (field.type === 'tel' && fieldValid) {
          fieldValid = value.replace(/[^0-9]/g, '').length >= 7;
        }

        if (wrapper) wrapper.classList.toggle('invalid', !fieldValid);
        if (!fieldValid) valid = false;
      });

      if (!valid) return;

      // No backend wired up yet — show a friendly success state instead.
      // See README for how to connect this to a real email/backend service.
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
