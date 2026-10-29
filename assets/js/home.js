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
const revealTargets = [...document.querySelectorAll('.section-topline, .display-heading, .about-heading-ja, .about-image, .about-text p, .section-heading-row > p, .service-row, .service-image, .company-table > div, .contact-grid p, .contact-action, .page-title-row > p, .page-jump-links, .service-detail-copy, .service-detail-image, .contact-form-panel')];
const marquee = document.querySelector('.tagline-marquee');
const marqueeTrack = marquee?.querySelector('.marquee-track');
const marqueeGroups = marqueeTrack ? [...marqueeTrack.children] : [];
const marqueePhrase = marqueeGroups[0] ? [...marqueeGroups[0].childNodes].map(node => node.cloneNode(true)) : [];
let marqueeAnimation;
let marqueeDistance = 0;
let marqueeDuration = 0;
let marqueeResizeFrame = 0;
const serviceImages = [...document.querySelectorAll('.service-image')];
const company = document.querySelector('.company');
const sectionLinks = [...navigation.querySelectorAll('a[href^="#"]')];
const motionAnimations = new Set();
let marqueePaused = false;
let observer;
let scrollFrame = 0;
const motionOff = () => motionPreference.matches;

function syncMarquee() {
  if (!marqueeTrack) return;
  if (motionPreference.matches) {
    marqueeAnimation?.cancel();
    marqueeAnimation = undefined;
    return;
  }
  // Each copy must cover the screen, including very wide viewports. Identical
  // groups and a half-track translation make the loop boundary seamless.
  const first = marqueeGroups[0];
  first.replaceChildren(...marqueePhrase.map(node => node.cloneNode(true)));
  const phraseWidth = first.getBoundingClientRect().width;
  if (!phraseWidth) return;
  const copies = Math.max(1, Math.ceil(marquee.clientWidth / phraseWidth));
  for (let index = 1; index < copies; index++) {
    first.append(...marqueePhrase.map(node => node.cloneNode(true)));
  }
  marqueeGroups[1].replaceChildren(...[...first.childNodes].map(node => node.cloneNode(true)));
  const distance = first.getBoundingClientRect().width;
  const duration = distance / (innerWidth < 761 ? 44 : 72) * 1000;
  if (!marqueeAnimation || Math.abs(distance - marqueeDistance) > .25 || Math.abs(duration - marqueeDuration) > 1) {
    const phase = marqueeAnimation && marqueeDuration ? (Number(marqueeAnimation.currentTime) % marqueeDuration) / marqueeDuration : 0;
    marqueeAnimation?.cancel();
    marqueeAnimation = marqueeTrack.animate([
      { transform: 'translate3d(0,0,0)' },
      { transform: 'translate3d(-50%,0,0)' },
    ], { duration, iterations: Infinity, easing: 'linear' });
    marqueeAnimation.currentTime = phase * duration;
    marqueeDistance = distance;
    marqueeDuration = duration;
  }
  if (marqueePaused) marqueeAnimation.pause();
  else if (marqueeAnimation.playState !== 'running') marqueeAnimation.play();
}

function requestMarqueeSync() {
  if (marqueeResizeFrame) return;
  marqueeResizeFrame = requestAnimationFrame(() => {
    marqueeResizeFrame = 0;
    syncMarquee();
  });
}

function animate(element, keyframes, timing) {
  const animation = element.animate(keyframes, timing);
  motionAnimations.add(animation);
  const release = () => motionAnimations.delete(animation);
  animation.finished.then(release, release);
  return animation;
}

function drawBrandMark() {
  if (motionOff()) return;
  motionAnimations.forEach(animation => {
    if (animation.effect.target?.matches('.brand-piece')) animation.cancel();
  });
  document.querySelectorAll('.brand-piece').forEach((path, index) => {
    animate(path, [
      { strokeDasharray: '1', strokeDashoffset: '1', strokeOpacity: 1, fillOpacity: 0 },
      { strokeDasharray: '1', strokeDashoffset: '0', strokeOpacity: 1, fillOpacity: 0, offset: .68 },
      { strokeDasharray: '1', strokeDashoffset: '0', strokeOpacity: 0, fillOpacity: 1 },
    ], { duration: 1600, delay: index * 150, easing: 'cubic-bezier(.45,0,.2,1)', fill: 'backwards' });
  });
}

// The page is fully visible without JavaScript or when motion is reduced.
// Independently implemented after inspecting Solvvy's title masks, logo drawing,
// scroll-linked typography, floating navigation and image parallax.
function setupMotion({ opening = false } = {}) {
  observer?.disconnect();
  motionAnimations.forEach(animation => animation.cancel());
  motionAnimations.clear();
  document.documentElement.classList.remove('motion-ready');
  syncMarquee();
  if (motionOff() || !('IntersectionObserver' in window)) {
    revealTargets.forEach(element => element.classList.add('is-inview'));
    ['--hero-rise', '--symbol-rise', '--symbol-turn', '--symbol-scale', '--hero-piece-gap'].forEach(name => hero?.style.removeProperty(name));
    ['--company-logo-y', '--company-logo-turn', '--company-logo-fill', '--company-logo-draw', '--company-piece-gap'].forEach(name => company?.style.removeProperty(name));
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
  if (!opening) return;
  drawBrandMark();
  document.querySelectorAll('.hero-symbol path').forEach((path, index) => {
    const direction = index === 0 ? -1 : 1;
    animate(path, [
      { strokeDasharray: '1', strokeDashoffset: '1', fillOpacity: 0, transform: `translate(${direction * 9}px,${direction * -6}px) rotate(${direction * 8}deg)` },
      { strokeDasharray: '1', strokeDashoffset: '0', fillOpacity: .12, transform: `translate(${direction * 2}px,0) rotate(0deg)`, offset: .65 },
      { strokeDasharray: '1', strokeDashoffset: '0', fillOpacity: 1, transform: 'translate(0,0) rotate(0deg)' },
    ], { duration: 2100, delay: index * 150, easing: 'cubic-bezier(.45,0,.2,1)', fill: 'backwards' });
  });
  document.querySelectorAll('.hero-word').forEach((word, index) => {
    animate(word, [
      { clipPath: 'inset(0 100% 0 0)', backgroundPosition: '100% 50%' },
      { clipPath: 'inset(0 0 0 0)', backgroundPosition: '0% 50%' },
    ], { duration: 1600, delay: 250 + index * 180, easing: 'cubic-bezier(.65,0,.25,1)', fill: 'backwards' });
  });
  document.querySelectorAll('.hero-copy > .eyebrow, .hero-caption, .hero-copy > .text-link').forEach((element, index) => {
    animate(element, [
      { opacity: 0, transform: 'translateY(18px)' },
      { opacity: 1, transform: 'translateY(0)' },
    ], { duration: 900, delay: 400 + index * 250, easing: 'cubic-bezier(.2,.65,.25,1)', fill: 'backwards' });
  });
}

function updateScroll() {
  scrollFrame = 0;
  header.classList.toggle('is-scrolled', window.scrollY > 30);
  let current;
  sectionLinks.forEach(link => {
    if (document.querySelector(link.getAttribute('href'))?.getBoundingClientRect().top <= innerHeight * .4) current = link;
  });
  sectionLinks.forEach(link => {
    if (link === current) link.setAttribute('aria-current', 'location');
    else link.removeAttribute('aria-current');
  });
  if (motionOff()) return;
  if (hero) {
    const progress = Math.max(0, Math.min(window.scrollY / hero.offsetHeight, 1));
    hero.style.setProperty('--hero-rise', `${-45 * progress}px`);
    hero.style.setProperty('--symbol-rise', `${55 * progress}px`);
    hero.style.setProperty('--symbol-turn', `${11 * progress}deg`);
    hero.style.setProperty('--symbol-scale', `${1 + progress * .1}`);
    hero.style.setProperty('--hero-piece-gap', `${2.5 * progress}px`);
  }
  const viewport = window.innerHeight;
  serviceImages.forEach(image => {
    const bounds = image.getBoundingClientRect();
    const position = Math.max(0, Math.min((viewport - bounds.top) / (viewport + bounds.height), 1));
    image.style.setProperty('--image-shift', `${(position - .5) * (innerWidth < 761 ? 22 : 58)}px`);
  });
  if (!company) return;
  const companyRect = company.getBoundingClientRect();
  const logoProgress = Math.max(0, Math.min((viewport - companyRect.top) / (viewport * .9 + companyRect.height * .4), 1));
  company.style.setProperty('--company-piece-gap', `${14 * (1 - logoProgress)}px`);
  company.style.setProperty('--company-logo-draw', `${1 - logoProgress}`);
  company.style.setProperty('--company-logo-fill', `${.12 + logoProgress * .78}`);
  company.style.setProperty('--company-logo-y', `${22 * (1 - logoProgress)}px`);
  company.style.setProperty('--company-logo-turn', `${-5 * (1 - logoProgress)}deg`);
}
window.addEventListener('scroll', () => {
  if (!scrollFrame) scrollFrame = requestAnimationFrame(updateScroll);
}, { passive: true });
motionPreference.addEventListener('change', () => { setupMotion(); updateScroll(); });
document.querySelector('.brand').addEventListener('pointerenter', drawBrandMark);
document.querySelector('.brand').addEventListener('focusin', drawBrandMark);
window.addEventListener('resize', () => {
  if (!scrollFrame) scrollFrame = requestAnimationFrame(updateScroll);
  requestMarqueeSync();
});
document.fonts.ready.then(requestMarqueeSync);
document.fonts.addEventListener('loadingdone', requestMarqueeSync);
setupMotion({ opening: true });
updateScroll();

// The moving typography itself supports click / Enter / Space to pause, without
// adding a visible control to the composition.
marquee?.querySelector('.marquee-toggle').addEventListener('click', event => {
  marqueePaused = !marqueePaused;
  event.currentTarget.setAttribute('aria-pressed', String(marqueePaused));
  event.currentTarget.setAttribute('aria-label', marqueePaused ? '流れる文字を再開' : '流れる文字を停止');
  syncMarquee();
});
