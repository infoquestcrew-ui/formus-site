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

const motionPreference = matchMedia('(prefers-reduced-motion: reduce)');
const header = document.querySelector('.site-header');
const hero = document.querySelector('.hero');
const revealTargets = [...document.querySelectorAll('.section-topline, .display-heading, .about-heading-ja, .about-image, .about-text p, .section-heading-row > p, .service-row, .company-table > div, .contact-grid p, .contact-action')];
let observer;
let scrollFrame = 0;
const entranceAnimations = [];

// The page is fully visible without JavaScript or when motion is reduced.
// Motion timing is isolated here for adjustment after reference-site review.
function setupMotion() {
  observer?.disconnect();
  entranceAnimations.forEach(animation => animation.cancel());
  entranceAnimations.length = 0;
  document.documentElement.classList.remove('motion-ready');
  if (motionPreference.matches || !('IntersectionObserver' in window)) {
    revealTargets.forEach(element => element.classList.add('is-inview'));
    hero.style.removeProperty('--photo-offset');
    hero.style.removeProperty('--stamp-turn');
    return;
  }
  observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-inview');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -20px 0px' });
  revealTargets.forEach(element => {
    element.dataset.reveal = '';
    observer.observe(element);
  });
  document.documentElement.classList.add('motion-ready');
  document.querySelectorAll('.hero-copy > *, .hero-visual').forEach((element, index) => {
    entranceAnimations.push(element.animate([
      { opacity: 0, transform: 'translateY(24px)', clipPath: 'inset(0 0 100% 0)' },
      { opacity: 1, transform: 'translateY(0)', clipPath: 'inset(0 0 0 0)' },
    ], { duration: 950, delay: index * 95, easing: 'cubic-bezier(.2,.65,.25,1)', fill: 'backwards' }));
  });
}

function updateScroll() {
  scrollFrame = 0;
  header.classList.toggle('is-scrolled', window.scrollY > 30);
  if (motionPreference.matches) return;
  const progress = Math.max(0, Math.min(window.scrollY / hero.offsetHeight, 1));
  hero.style.setProperty('--photo-offset', `${-25 * progress}px`);
  hero.style.setProperty('--stamp-turn', `${progress * 28}deg`);
}
window.addEventListener('scroll', () => {
  if (!scrollFrame) scrollFrame = requestAnimationFrame(updateScroll);
}, { passive: true });
motionPreference.addEventListener('change', setupMotion);
setupMotion();
updateScroll();

const newsDialog = document.querySelector('.news-dialog');
document.querySelector('[data-news-open]').addEventListener('click', () => newsDialog.showModal());
newsDialog.querySelector('.dialog-close').addEventListener('click', () => newsDialog.close());
newsDialog.addEventListener('click', event => {
  const rect = newsDialog.getBoundingClientRect();
  if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) newsDialog.close();
});
