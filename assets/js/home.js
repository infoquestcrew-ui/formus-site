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
const revealTargets = [...document.querySelectorAll('.section-topline, .display-heading, .about-heading-ja, .about-image, .about-text p, .section-heading-row > p, .service-row, .service-image, .company-table > div, .contact-grid p, .contact-action')];
const marquee = document.querySelector('.tagline-marquee');
const serviceImages = [...document.querySelectorAll('.service-image')];
let observer;
let scrollFrame = 0;
const entranceAnimations = [];

// The page is fully visible without JavaScript or when motion is reduced.
// Independently implemented after inspecting Solvvy's title masks, logo drawing,
// scroll-linked typography, floating navigation and image parallax.
function setupMotion() {
  observer?.disconnect();
  entranceAnimations.forEach(animation => animation.cancel());
  entranceAnimations.length = 0;
  document.documentElement.classList.remove('motion-ready');
  if (motionPreference.matches || !('IntersectionObserver' in window)) {
    revealTargets.forEach(element => element.classList.add('is-inview'));
    hero.style.removeProperty('--hero-rise');
    hero.style.removeProperty('--symbol-rise');
    marquee.style.removeProperty('--marquee-shift');
    serviceImages.forEach(image => image.style.removeProperty('--image-shift'));
    return;
  }
  // A fully masked node has no intersection area. Observe its unmasked
  // container so heading/image wipes can actually start on every browser.
  const observedGroups = new Map();
  revealTargets.forEach(element => {
    element.dataset.reveal = '';
    const anchor = element.matches('.display-heading, .service-image') ? element.parentElement : element;
    const group = observedGroups.get(anchor) || [];
    group.push(element);
    observedGroups.set(anchor, group);
  });
  observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        observedGroups.get(entry.target).forEach(element => element.classList.add('is-inview'));
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -20px 0px' });
  observedGroups.forEach((_, anchor) => observer.observe(anchor));
  document.documentElement.classList.add('motion-ready');
  document.querySelectorAll('.about-text p').forEach((element, index) => element.style.setProperty('--reveal-delay', `${index * 60}ms`));
  document.querySelectorAll('.hero-symbol path').forEach((path, index) => {
    entranceAnimations.push(path.animate([
      { strokeDasharray: '1', strokeDashoffset: '1', fillOpacity: 0 },
      { strokeDasharray: '1', strokeDashoffset: '0', fillOpacity: 1 },
    ], { duration: 1500, delay: index * 120, easing: 'cubic-bezier(.45,0,.2,1)', fill: 'backwards' }));
  });
  document.querySelectorAll('.hero-word').forEach((word, index) => {
    entranceAnimations.push(word.animate([
      { clipPath: 'inset(0 100% 0 0)', backgroundPosition: '100% 50%' },
      { clipPath: 'inset(0 0 0 0)', backgroundPosition: '0% 50%' },
    ], { duration: 1600, delay: 250 + index * 180, easing: 'cubic-bezier(.65,0,.25,1)', fill: 'backwards' }));
  });
  document.querySelectorAll('.hero-copy > .eyebrow, .hero-caption, .hero-copy > .text-link').forEach((element, index) => {
    entranceAnimations.push(element.animate([
      { opacity: 0, transform: 'translateY(18px)' },
      { opacity: 1, transform: 'translateY(0)' },
    ], { duration: 900, delay: 400 + index * 250, easing: 'cubic-bezier(.2,.65,.25,1)', fill: 'backwards' }));
  });
}

function updateScroll() {
  scrollFrame = 0;
  header.classList.toggle('is-scrolled', window.scrollY > 30);
  if (motionPreference.matches) return;
  const progress = Math.max(0, Math.min(window.scrollY / hero.offsetHeight, 1));
  hero.style.setProperty('--hero-rise', `${-45 * progress}px`);
  hero.style.setProperty('--symbol-rise', `${55 * progress}px`);
  const viewport = window.innerHeight;
  const rect = marquee.getBoundingClientRect();
  const textProgress = Math.max(0, Math.min((viewport - rect.top) / (viewport + rect.height), 1));
  marquee.style.setProperty('--marquee-shift', `${50 - 230 * textProgress}px`);
  serviceImages.forEach(image => {
    const bounds = image.getBoundingClientRect();
    const position = Math.max(0, Math.min((viewport - bounds.top) / (viewport + bounds.height), 1));
    image.style.setProperty('--image-shift', `${(position - .5) * (innerWidth < 761 ? 22 : 58)}px`);
  });
}
window.addEventListener('scroll', () => {
  if (!scrollFrame) scrollFrame = requestAnimationFrame(updateScroll);
}, { passive: true });
motionPreference.addEventListener('change', () => { setupMotion(); updateScroll(); });
window.addEventListener('resize', () => {
  if (!scrollFrame) scrollFrame = requestAnimationFrame(updateScroll);
});
setupMotion();
updateScroll();

const newsDialog = document.querySelector('.news-dialog');
document.querySelector('[data-news-open]').addEventListener('click', () => newsDialog.showModal());
newsDialog.querySelector('.dialog-close').addEventListener('click', () => newsDialog.close());
newsDialog.addEventListener('click', event => {
  const rect = newsDialog.getBoundingClientRect();
  if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) newsDialog.close();
});
