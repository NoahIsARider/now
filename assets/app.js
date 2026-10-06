// MAYDAY — search + mood filter. No dependencies.
(function () {
  var data = JSON.parse(document.getElementById('films-data').textContent);
  var rows = Array.prototype.slice.call(document.querySelectorAll('.manifest tbody tr'));
  var chipBox = document.getElementById('chips');
  var input = document.getElementById('q');
  var count = document.getElementById('count');
  var empty = document.getElementById('empty');
  var active = [];

  function esc(s) { return s.replace(/[&<>"]/g, function (c) {
    return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]; }); }

  data.moods.forEach(function (m) {
    var b = document.createElement('button');
    b.className = 'chip'; b.type = 'button'; b.textContent = m;
    b.setAttribute('aria-pressed', 'false');
    b.addEventListener('click', function () {
      var i = active.indexOf(m);
      if (i < 0) { active.push(m); } else { active.splice(i, 1); }
      b.setAttribute('aria-pressed', i < 0 ? 'true' : 'false');
      apply();
    });
    chipBox.appendChild(b);
  });

  function apply() {
    var q = (input.value || '').trim().toLowerCase();
    var shown = 0;
    rows.forEach(function (tr) {
      var hay = (tr.getAttribute('data-hay') || '').toLowerCase();
      var tags = (tr.getAttribute('data-tags') || '').split(' ');
      var okQ = !q || hay.indexOf(q) > -1;
      var okM = active.every(function (m) { return tags.indexOf(m) > -1; });
      var ok = okQ && okM;
      tr.hidden = !ok;
      if (ok) { shown++; }
    });
    count.textContent = 'SHOWING ' + shown + ' / ' + rows.length + ' FILMS';
    empty.hidden = shown !== 0;
  }

  input.addEventListener('input', apply);
  document.addEventListener('keydown', function (e) {
    if (e.key === '/' && document.activeElement !== input) { e.preventDefault(); input.focus(); }
    if (e.key === 'Escape' && document.activeElement === input) { input.value = ''; apply(); input.blur(); }
  });
  apply();
})();
