'use strict';

const contactForm = document.querySelector('#contact-form');
const privacyDialog = document.querySelector('#privacy');
const privacyLink = document.querySelector('.policy-link');
privacyLink.addEventListener('click', event => {
  event.preventDefault();
  privacyDialog.showModal();
});
privacyDialog.querySelector('.dialog-close').addEventListener('click', () => privacyDialog.close());
privacyDialog.addEventListener('click', event => {
  const bounds = privacyDialog.getBoundingClientRect();
  if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) privacyDialog.close();
});
privacyDialog.addEventListener('close', () => privacyLink.focus());

const submit = contactForm.querySelector('[type="submit"]');
const submitLabel = submit.querySelector('span');
const status = document.querySelector('#form-status');
const endpoint = new URL(contactForm.getAttribute('action'), location.href);
const fallback = '送信できませんでした。入力内容は残っています。時間をおいてお試しいただくか、info@formus.jpへメールでご連絡ください。';
let csrf = '';
let busy = false;
let delivered = false;

function report(message) {
  status.textContent = message;
  status.scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth', block: 'center' });
}

async function requestToken() {
  const response = await fetch(endpoint, { credentials: 'same-origin', cache: 'no-store', headers: { Accept: 'application/json' }, signal: AbortSignal.timeout(15000) });
  const result = await response.json();
  if (!response.ok || !result.ok || typeof result.csrf !== 'string') throw new Error('Token unavailable');
  csrf = result.csrf;
}

contactForm.addEventListener('submit', async event => {
  event.preventDefault();
  if (busy || delivered || !contactForm.reportValidity()) return;
  busy = true;
  submit.disabled = true;
  submitLabel.textContent = '送信中…';
  contactForm.setAttribute('aria-busy', 'true');
  let posted = false;
  try {
    if (!csrf) await requestToken();
    const body = new FormData(contactForm);
    body.set('csrf', csrf);
    // A timed-out response can still mean the server accepted the message.
    // Never automatically retry a POST and accidentally deliver duplicates.
    posted = true;
    const response = await fetch(endpoint, { method: 'POST', body, credentials: 'same-origin', cache: 'no-store', headers: { Accept: 'application/json' }, signal: AbortSignal.timeout(30000) });
    const result = await response.json();
    if (!response.ok || !result.ok) {
      if (response.status === 403) {
        csrf = '';
        try { await requestToken(); } catch { /* The next explicit submit can retry preparation. */ }
      }
      report(result.message || fallback);
      return;
    }
    delivered = true;
    contactForm.reset();
    report(result.message);
  } catch (error) {
    report(posted ? '送信の結果を確認できませんでした。すでに送信されている場合があります。再送する前に、info@formus.jpへご確認ください。' : fallback);
  } finally {
    busy = false;
    submit.disabled = delivered;
    submitLabel.textContent = delivered ? '送信を受け付けました' : 'お問い合わせを送信する';
    contactForm.removeAttribute('aria-busy');
  }
});

// A temporary connection failure does not trap visitors behind a disabled
// button: an explicit submit can retry token preparation.
requestToken().catch(() => {
  status.textContent = '送信の準備ができませんでした。送信ボタンからもう一度お試しいただくか、info@formus.jpへメールでご連絡ください。';
}).finally(() => { submit.disabled = false; });
