'use strict';

const toggle = document.querySelector('.menu-toggle');
const navigation = document.querySelector('#main-nav');
function closeMenu(returnFocus = false) {
  toggle.setAttribute('aria-expanded', 'false');
  toggle.setAttribute('aria-label', 'メニューを開く');
  navigation.classList.remove('is-open');
  document.body.classList.remove('nav-open');
  if (returnFocus) toggle.focus();
}
toggle.addEventListener('click', () => {
  const open = toggle.getAttribute('aria-expanded') !== 'true';
  toggle.setAttribute('aria-expanded', String(open));
  toggle.setAttribute('aria-label', open ? 'メニューを閉じる' : 'メニューを開く');
  navigation.classList.toggle('is-open', open);
  document.body.classList.toggle('nav-open', open);
});
navigation.querySelectorAll('a').forEach(link => link.addEventListener('click', () => closeMenu()));
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') closeMenu(true);
  if (event.key === 'Tab' && toggle.getAttribute('aria-expanded') === 'true') {
    const links = [...navigation.querySelectorAll('a')];
    if (!event.shiftKey && document.activeElement === toggle) {
      event.preventDefault(); links[0].focus();
    } else if (event.shiftKey && document.activeElement === links[0]) {
      event.preventDefault(); toggle.focus();
    } else if (event.shiftKey && document.activeElement === toggle) {
      event.preventDefault(); links.at(-1).focus();
    } else if (!event.shiftKey && document.activeElement === links.at(-1)) {
      event.preventDefault(); toggle.focus();
    }
  }
});
matchMedia('(min-width: 761px)').addEventListener('change', event => {
  if (event.matches) closeMenu();
});

const video = document.querySelector('video');
const videoToggle = document.querySelector('.video-toggle');
const motionPreference = matchMedia('(prefers-reduced-motion: reduce)');
function updateVideoButton() {
  videoToggle.setAttribute('aria-label', video.paused ? '動画を再生' : '動画を一時停止');
  videoToggle.firstElementChild.textContent = video.paused ? '▶' : 'Ⅱ';
}
videoToggle.addEventListener('click', () => {
  if (video.paused) video.play().catch(updateVideoButton);
  else video.pause();
});
video.addEventListener('play', updateVideoButton);
video.addEventListener('pause', updateVideoButton);
if (motionPreference.matches) {
  video.removeAttribute('autoplay');
  video.pause();
}
motionPreference.addEventListener('change', event => {
  if (event.matches) video.pause();
});
updateVideoButton();

const newsDialog = document.querySelector('.news-dialog');
document.querySelector('[data-news-open]').addEventListener('click', () => newsDialog.showModal());
newsDialog.querySelector('.dialog-close').addEventListener('click', () => newsDialog.close());
newsDialog.addEventListener('click', event => {
  const rect = newsDialog.getBoundingClientRect();
  if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) newsDialog.close();
});
