// login.js

function togglePw(inputId, btn) {
  const inp = document.getElementById(inputId);
  if (inp.type === 'password') {
    inp.type = 'text';
    btn.textContent = '🙈';
  } else {
    inp.type = 'password';
    btn.textContent = '👁';
  }
}

function handleLogin() {
  const email    = document.getElementById('inp-email').value.trim();
  const password = document.getElementById('inp-password').value;
  let valid = true;

  document.getElementById('err-email').classList.remove('show');
  document.getElementById('err-password').classList.remove('show');

  if (!email || !/\S+@\S+\.\S+/.test(email)) {
    document.getElementById('err-email').classList.add('show');
    valid = false;
  }

  if (!password) {
    document.getElementById('err-password').classList.add('show');
    valid = false;
  }

  if (!valid) return;

  fetch('/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  })
  .then(async r => {
    if (!r.ok) {
      const errData = await r.json();
      throw new Error(errData.detail || 'Login failed');
    }
    return r.json();
  })
  .then(data => {
    localStorage.setItem('token', data.access_token);
    window.location.href = '/';
  })
  .catch(err => {
    alert(err.message);
  });
}

document.addEventListener('keydown', e => {
  if (e.key === 'Enter') handleLogin();
});