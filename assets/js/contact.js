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

// The preview has no delivery endpoint. Keep input local and never submit it to
// the reference site's service. Native validation still checks required fields.
contactForm.addEventListener('submit', event => {
  event.preventDefault();
  if (!contactForm.reportValidity()) return;
  const status = document.querySelector('#form-status');
  status.textContent = '入力内容を確認しました。デザイン確認用のため、お問い合わせは送信されていません。';
  status.scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth', block: 'center' });
});
contactForm.querySelector('[type="submit"]').disabled = false;
