// MAYDAY — search + rating filter. No dependencies.
(function () {
  var rows = Array.prototype.slice.call(document.querySelectorAll('.entries .entry'));
  var input = document.getElementById('q');
  var count = document.getElementById('count');
  var empty = document.getElementById('empty');
  var chips = Array.prototype.slice.call(document.querySelectorAll('.chip'));
  var ratings = [];       // selected star values, matched with OR
  var likedOnly = false;

  chips.forEach(function (chip) {
    chip.addEventListener('click', function () {
      if (chip.hasAttribute('data-liked')) {
        likedOnly = !likedOnly;
        chip.setAttribute('aria-pressed', likedOnly ? 'true' : 'false');
      } else {
        var v = chip.getAttribute('data-rating');
        var i = ratings.indexOf(v);
        if (i < 0) { ratings.push(v); } else { ratings.splice(i, 1); }
        chip.setAttribute('aria-pressed', i < 0 ? 'true' : 'false');
      }
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
      var okR = ratings.length === 0 || ratings.indexOf(r) > -1;
      var okL = !likedOnly || row.getAttribute('data-liked') === '1';
      var ok = okQ && okR && okL;
      row.hidden = !ok;
      if (ok) { shown++; }
    });
    count.textContent = 'showing ' + shown + ' of ' + rows.length + ' films';
    empty.hidden = shown !== 0;
  }

  input.addEventListener('input', apply);
  document.addEventListener('keydown', function (e) {
    if (e.key === '/' && document.activeElement !== input) { e.preventDefault(); input.focus(); }
    if (e.key === 'Escape' && document.activeElement === input) { input.value = ''; apply(); input.blur(); }
  });
  apply();
})();
