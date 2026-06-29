// forgot.js

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

function clearErrors() {
  ['err-email', 'err-phone', 'err-password', 'err-confirm']
    .forEach(id => {
      const el = document.getElementById(id);
      if (el) el.classList.remove('show');
    });
}

function handleForgotPassword() {
  clearErrors();

  const email    = document.getElementById('inp-email').value.trim();
  const phone    = document.getElementById('inp-phone').value.trim();
  const code     = document.getElementById('inp-country-code').value;
  const password = document.getElementById('inp-password').value;
  const confirm  = document.getElementById('inp-confirm').value;
  let valid = true;

  if (!email || !/\S+@\S+\.\S+/.test(email)) {
    document.getElementById('err-email').classList.add('show');
    valid = false;
  }
  if (!phone || !/^\d{10}$/.test(phone)) {
    document.getElementById('err-phone').classList.add('show');
    valid = false;
  }
  if (!password || password.length < 8) {
    document.getElementById('err-password').classList.add('show');
    valid = false;
  }
  if (password !== confirm) {
    document.getElementById('err-confirm').classList.add('show');
    valid = false;
  }

  if (!valid) return;

  const payload = {
    email,
    phone: `${code}${phone}`,
    new_password: password,
  };

  fetch('/auth/forgot-password', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
  .then(async r => {
    if (!r.ok) {
      const errData = await r.json();
      throw new Error(errData.detail || 'Reset failed');
    }
    return r.json();
  })
  .then(() => {
    alert('Password reset successful! Redirecting to login page...');
    window.location.href = '/static/login.html';
  })
  .catch(err => {
    alert(err.message);
  });
}
