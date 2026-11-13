const dialogs = [...document.querySelectorAll('dialog')];
document.querySelectorAll('[data-open]').forEach(button => button.addEventListener('click', () => { document.getElementById(button.dataset.open).showModal(); }));
dialogs.forEach(dialog => { dialog.querySelector('.close').addEventListener('click', () => dialog.close()); dialog.addEventListener('click', event => { if (event.target === dialog) { const r = dialog.getBoundingClientRect(); if (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom) dialog.close(); } }); });
// Signup posts directly to Mailchimp; its confirmation flow handles errors and double opt-in.

// Track a qualified email-signup submission as a Meta Lead event.
const signupForm = document.getElementById('signup-form');
if (signupForm) {
  signupForm.addEventListener('submit', () => {
    if (!signupForm.checkValidity()) return;
    if (typeof window.fbq === 'function') {
      window.fbq('track', 'Lead', { content_name: '100-Day Roadmap Signup' });
    }
  });
}

// Track booking intent when a visitor leaves for Calendly.
// We use Contact for Meta optimization and a custom event to preserve which option they chose.
document.querySelectorAll('#booking .booking-option').forEach((link, index) => {
  link.addEventListener('click', () => {
    if (typeof window.fbq !== 'function') return;
    const bookingType = index === 0 ? 'project_conversation' : 'paid_consultation';
    const bookingLabel = index === 0 ? 'Project Conversation' : '1-Hour Consultation';
    window.fbq('track', 'Contact', {
      content_name: bookingLabel,
      contact_method: 'Calendly'
    });
    window.fbq('trackCustom', 'BookCallClick', {
      booking_type: bookingType,
      booking_label: bookingLabel
    });
  });
});

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
const dialogs = [...document.querySelectorAll('dialog')];
document.querySelectorAll('[data-open]').forEach(button => button.addEventListener('click', () => { document.getElementById(button.dataset.open).showModal(); }));
dialogs.forEach(dialog => { dialog.querySelector('.close').addEventListener('click', () => dialog.close()); dialog.addEventListener('click', event => { if (event.target === dialog) { const r = dialog.getBoundingClientRect(); if (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom) dialog.close(); } }); });
// Signup posts directly to Mailchimp; its confirmation flow handles errors and double opt-in.

// Track a qualified email-signup submission as a Meta Lead event.
const signupForm = document.getElementById('signup-form');
if (signupForm) {
  signupForm.addEventListener('submit', () => {
    if (!signupForm.checkValidity()) return;
    if (typeof window.fbq === 'function') {
      window.fbq('track', 'Lead', { content_name: '100-Day Roadmap Signup' });
    }
  });
}

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
