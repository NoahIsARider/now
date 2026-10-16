// shkb — search + score filter. No dependencies. Same grammar as MAYDAY.
(function () {
  var rows = Array.prototype.slice.call(document.querySelectorAll('.entries .entry'));
  var input = document.getElementById('q');
  var count = document.getElementById('count');
  var empty = document.getElementById('empty');
  var chips = Array.prototype.slice.call(document.querySelectorAll('.chip'));
  var scores = [];      // selected scores, matched with OR

  chips.forEach(function (chip) {
    chip.addEventListener('click', function () {
      var v = chip.getAttribute('data-rating');
      var i = scores.indexOf(v);
      if (i < 0) { scores.push(v); } else { scores.splice(i, 1); }
      chip.setAttribute('aria-pressed', i < 0 ? 'true' : 'false');
      apply();
    });
  });

  function apply() {
    var q = (input.value || '').trim().toLowerCase();
    var shown = 0;
    rows.forEach(function (row) {
      var hay = (row.getAttribute('data-hay') || '').toLowerCase();
      var okQ = !q || hay.indexOf(q) > -1;
      var r = row.getAttribute('data-rating');
      var okS = scores.length === 0 || scores.indexOf(r) > -1;
      var ok = okQ && okS;
      row.hidden = !ok;
      if (ok) { shown++; }
    });
    count.textContent = 'showing ' + shown + ' of ' + rows.length + ' releases';
    empty.hidden = shown !== 0;
  }

  input.addEventListener('input', apply);
  document.addEventListener('keydown', function (e) {
    if (e.key === '/' && document.activeElement !== input) { e.preventDefault(); input.focus(); }
    if (e.key === 'Escape' && document.activeElement === input) { input.value = ''; apply(); input.blur(); }
  });
  apply();
})();
