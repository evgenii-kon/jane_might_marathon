(function () {
  var btn = document.getElementById('theme-toggle');
  if (!btn) return;

  function apply(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    btn.textContent = theme === 'dark' ? '☀️' : '🌙';
    try { localStorage.setItem('theme', theme); } catch (e) {}
  }

  var current = document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
  btn.textContent = current === 'dark' ? '☀️' : '🌙';

  btn.addEventListener('click', function () {
    current = current === 'dark' ? 'light' : 'dark';
    apply(current);
  });
})();
