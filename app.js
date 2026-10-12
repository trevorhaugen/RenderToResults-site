const dialogs = [...document.querySelectorAll('dialog')];
document.querySelectorAll('[data-open]').forEach(button => button.addEventListener('click', () => { document.getElementById(button.dataset.open).showModal(); }));
dialogs.forEach(dialog => { dialog.querySelector('.close').addEventListener('click', () => dialog.close()); dialog.addEventListener('click', event => { if (event.target === dialog) { const r = dialog.getBoundingClientRect(); if (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom) dialog.close(); } }); });
// Signup posts directly to Mailchimp; its confirmation flow handles errors and double opt-in.

// Load the YouTube player only after a visitor clicks the custom thumbnail.
document.addEventListener('click', event => {
  const button = event.target.closest('.short-launch');
  if (!button) return;
  const id = button.dataset.videoId;
  if (!/^[A-Za-z0-9_-]{11}$/.test(id)) return;
  const iframe = document.createElement('iframe');
  iframe.src = 'https://www.youtube-nocookie.com/embed/' + id + '?autoplay=1';
  iframe.title = button.getAttribute('aria-label');
  iframe.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';
  iframe.allowFullscreen = true;
  iframe.referrerPolicy = 'strict-origin-when-cross-origin';
  button.replaceWith(iframe);
});
