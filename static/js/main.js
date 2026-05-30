// Auto-dismiss alerts after 5 seconds
document.addEventListener('DOMContentLoaded', function () {
  setTimeout(function () {
    document.querySelectorAll('.alert').forEach(function (el) {
      el.style.opacity = '0';
      el.style.transition = 'opacity 0.4s ease';
      setTimeout(() => el.remove(), 400);
    });
  }, 5000);

  // Password strength indicator
  var pwdInput = document.getElementById('password');
  var strengthBar = document.getElementById('pwd-strength');
  if (pwdInput && strengthBar) {
    pwdInput.addEventListener('input', function () {
      var val = pwdInput.value;
      var score = 0;
      if (val.length >= 8) score++;
      if (/[A-Z]/.test(val)) score++;
      if (/[0-9]/.test(val)) score++;
      if (/[^A-Za-z0-9]/.test(val)) score++;
      var colors = ['#f87171', '#fbbf24', '#34d399', '#34d399'];
      var widths = ['25%', '50%', '75%', '100%'];
      if (val.length === 0) {
        strengthBar.style.width = '0';
      } else {
        strengthBar.style.width = widths[score - 1] || '25%';
        strengthBar.style.background = colors[score - 1] || '#f87171';
      }
    });
  }

  // Confirm password match visual feedback
  var pwd2 = document.querySelector('input[name="password2"]');
  var pwd1 = document.querySelector('input[name="password"]');
  if (pwd2 && pwd1) {
    pwd2.addEventListener('input', function () {
      if (pwd2.value && pwd1.value) {
        if (pwd2.value === pwd1.value) {
          pwd2.style.borderColor = 'var(--success)';
        } else {
          pwd2.style.borderColor = 'var(--danger)';
        }
      } else {
        pwd2.style.borderColor = '';
      }
    });
  }

  // Set today's date as default for date inputs if empty
  var dateInputs = document.querySelectorAll('input[type="date"]');
  dateInputs.forEach(function (input) {
    if (!input.value) {
      var today = new Date().toISOString().split('T')[0];
      input.value = today;
    }
  });
});
