const dialogs = [...document.querySelectorAll('dialog')];
document.querySelectorAll('[data-open]').forEach(button => button.addEventListener('click', () => { document.getElementById(button.dataset.open).showModal(); }));
dialogs.forEach(dialog => { dialog.querySelector('.close').addEventListener('click', () => dialog.close()); dialog.addEventListener('click', event => { if (event.target === dialog) { const r = dialog.getBoundingClientRect(); if (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom) dialog.close(); } }); });
// Signup posts directly to Mailchimp; its confirmation flow handles errors and double opt-in.
