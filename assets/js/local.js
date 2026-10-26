'use strict';

// Keep the original menu appearance while making it usable with a keyboard.
const menu = document.querySelector('.l-header .menu');
const navigation = document.querySelector('.l-header nav');
if (menu && navigation) {
  navigation.id = 'primary-navigation';
  menu.setAttribute('role', 'button');
  menu.setAttribute('tabindex', '0');
  menu.setAttribute('aria-controls', navigation.id);
  const updateMenu = () => {
    const expanded = menu.classList.contains('open');
    menu.setAttribute('aria-expanded', String(expanded));
    menu.setAttribute('aria-label', expanded ? 'メニューを閉じる' : 'メニューを開く');
  };
  updateMenu();
  new MutationObserver(updateMenu).observe(menu, {
    attributes: true,
    attributeFilter: ['class'],
  });
  menu.addEventListener('keydown', (event) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      menu.click();
    }
  });
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && menu.classList.contains('open')) {
      menu.classList.remove('open');
      menu.focus();
    }
  });
}

// This reconstruction has no delivery endpoint. Never forward visitor data to
// the reference site's contact service, including when a valid form is filled.
const contactForm = document.querySelector('#contact-form');
if (contactForm) {
  contactForm.addEventListener('submit', (event) => {
    event.preventDefault();
    if (!contactForm.reportValidity()) return;
    const status = document.querySelector('#form-status');
    status.textContent = '入力内容を確認しました。デモサイトのため、お問い合わせは送信されていません。';
    status.classList.add('is-visible');
    status.scrollIntoView({ behavior: 'smooth', block: 'center' });
  });
}
