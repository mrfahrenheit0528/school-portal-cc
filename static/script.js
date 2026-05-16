// ── Page Switching ──
function showPage(page, updateHash = true) {
  const targetPage = document.getElementById('page-' + page);
  const targetNav = document.getElementById('nav-' + page);

  if (!targetPage) return false;

  // Update UI
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-links a').forEach(a => a.classList.remove('active'));
  
  targetPage.classList.add('active');
  if (targetNav) targetNav.classList.add('active');

  // Update URL Hash if requested
  if (updateHash) {
    window.location.hash = page;
  }

  window.scrollTo({ top: 0, behavior: 'smooth' });

  // Re-trigger scroll reveal for the newly active page
  requestAnimationFrame(() => {
    initScrollReveal();
    staggerCards(targetPage);
  });

  return false;
}

// ── Scroll Reveal (IntersectionObserver) ──
function initScrollReveal() {
  const revealElements = document.querySelectorAll('.reveal:not(.visible)');
  if (!revealElements.length) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

  revealElements.forEach(el => observer.observe(el));
}

// ── Staggered Card Entrance ──
function staggerCards(container) {
  if (!container) return;
  const cards = container.querySelectorAll(
    '.announcement-card, .file-card, .quick-card'
  );
  cards.forEach((card, i) => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(20px)';
    card.style.transition = 'none';

    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        card.style.transition = `opacity 0.5s ease ${i * 0.08}s, transform 0.5s ease ${i * 0.08}s`;
        card.style.opacity = '1';
        card.style.transform = 'translateY(0)';
      });
    });
  });
}

// ── Routing Logic ──
function handleRouting() {
  const hash = window.location.hash.replace('#', '');
  if (hash) {
    showPage(hash, false); // Don't update hash again to avoid loops
  } else {
    showPage('home', false);
  }
}

// ── Init on Load ──
document.addEventListener('DOMContentLoaded', () => {
  // Mark section headings for scroll reveal
  document.querySelectorAll('.section-heading').forEach(el => {
    el.classList.add('reveal');
  });

  initScrollReveal();

  // Listen for hash changes (back/forward buttons)
  window.addEventListener('hashchange', handleRouting);

  // Initial routing check
  handleRouting();
});
