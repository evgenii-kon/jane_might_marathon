(function () {
  var btn = document.getElementById('theme-toggle');
  if (!btn) return;
  var icon = btn.querySelector('.theme-toggle-icon') || btn;

  function apply(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    icon.textContent = theme === 'dark' ? '☀️' : '🌙';
    try { localStorage.setItem('theme', theme); } catch (e) {}
  }

  var current = document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
  icon.textContent = current === 'dark' ? '☀️' : '🌙';

  btn.addEventListener('click', function () {
    current = current === 'dark' ? 'light' : 'dark';
    apply(current);
  });
})();
