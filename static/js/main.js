// BlackBox Movies — main.js

// ── LOADER ──────────────────────────────────────
window.addEventListener('load', () => {
  setTimeout(() => {
    document.getElementById('loader')?.classList.add('hidden');
  }, 1400);
});

// ── NAVBAR SCROLL ───────────────────────────────
const navbar = document.getElementById('navbar');
window.addEventListener('scroll', () => {
  navbar?.classList.toggle('scrolled', window.scrollY > 40);
}, { passive: true });

// ── SLIDER BUTTONS ──────────────────────────────
document.querySelectorAll('.slider-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    const row = document.getElementById(btn.dataset.target);
    if (!row) return;
    const dir = parseInt(btn.dataset.dir);
    row.scrollBy({ left: dir * 650, behavior: 'smooth' });
  });
});

// ── LIVE SEARCH ─────────────────────────────────
const searchInput = document.getElementById('liveSearch');
const dropdown = document.getElementById('searchDropdown');

if (searchInput && dropdown) {
  let debounce;
  searchInput.addEventListener('input', () => {
    clearTimeout(debounce);
    const q = searchInput.value.trim();
    if (q.length < 2) {
      dropdown.innerHTML = '';
      dropdown.classList.remove('open');
      return;
    }
    debounce = setTimeout(() => {
      fetch(`/search/ajax/?q=${encodeURIComponent(q)}`)
        .then(r => r.json())
        .then(data => {
          if (!data.results.length) {
            dropdown.innerHTML = '<div style="padding:12px 14px;color:#7a7a90;font-size:.82rem">No results found</div>';
          } else {
            dropdown.innerHTML = data.results.map(m => `
              <a class="search-result-item" href="/movie/${m.slug}/">
                ${m.poster ? `<img src="${m.poster}" alt="${m.title}">` : ''}
                <div class="sri-info">
                  <div class="sri-title">${m.title}</div>
                  <div class="sri-meta">${m.genre} · ${m.year}</div>
                </div>
              </a>
            `).join('');
          }
          dropdown.classList.add('open');
        });
    }, 300);
  });

  document.addEventListener('click', e => {
    if (!searchInput.contains(e.target) && !dropdown.contains(e.target)) {
      dropdown.classList.remove('open');
    }
  });

  searchInput.addEventListener('keydown', e => {
    if (e.key === 'Enter') {
      window.location.href = `/search/?q=${encodeURIComponent(searchInput.value)}`;
    }
  });
}

// ── WATCHLIST BUTTONS (movie cards) ─────────────
document.querySelectorAll('.watchlist-btn').forEach(btn => {
  btn.addEventListener('click', e => {
    e.preventDefault(); e.stopPropagation();
    const slug = btn.dataset.slug;
    const csrfToken = document.cookie.match(/csrftoken=([^;]+)/)?.[1] || '';
    fetch(`/watchlist/toggle/${slug}/`, {
      headers: { 'X-CSRFToken': csrfToken }
    })
    .then(r => r.json())
    .then(d => {
      btn.style.color = d.status === 'added' ? '#e63946' : '';
      btn.title = d.status === 'added' ? 'In Watchlist' : 'Add to Watchlist';
    });
  });
});

// ── AUTO-DISMISS MESSAGES ────────────────────────
document.querySelectorAll('.message').forEach(msg => {
  setTimeout(() => {
    msg.style.transition = 'opacity 0.4s';
    msg.style.opacity = '0';
    setTimeout(() => msg.remove(), 400);
  }, 4000);
});

// ── SMOOTH CARD ENTRANCE (IntersectionObserver) ──
if ('IntersectionObserver' in window) {
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

  document.querySelectorAll('.movie-card').forEach((card, i) => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(20px)';
    card.style.transition = `opacity 0.4s ease ${i * 0.05}s, transform 0.4s ease ${i * 0.05}s`;
    observer.observe(card);
  });
}


// ── THEME TOGGLE ──────────────────────────────────────
const themeToggle = document.getElementById('themeToggle');
const html = document.documentElement;

if (themeToggle) {
  themeToggle.addEventListener('click', () => {
    const current = html.getAttribute('data-theme') || 'dark';
    const next = current === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', next);
    localStorage.setItem('bbTheme', next);
    themeToggle.style.transform = 'scale(0.85) rotate(20deg)';
    setTimeout(() => { themeToggle.style.transform = ''; }, 200);
  });
}

// ── NAV GENRE SCROLL ──────────────────────
const navLinks     = document.getElementById('navLinks');
const navScrollLeft  = document.getElementById('navScrollLeft');
const navScrollRight = document.getElementById('navScrollRight');

if (navLinks && navScrollLeft && navScrollRight) {
  navScrollLeft.addEventListener('click',  () => navLinks.scrollBy({ left: -200, behavior: 'smooth' }));
  navScrollRight.addEventListener('click', () => navLinks.scrollBy({ left:  200, behavior: 'smooth' }));

  function updateNavArrows() {
    navScrollLeft.style.opacity  = navLinks.scrollLeft > 10 ? '1' : '0.3';
    navScrollRight.style.opacity = navLinks.scrollLeft < navLinks.scrollWidth - navLinks.clientWidth - 10 ? '1' : '0.3';
  }
  navLinks.addEventListener('scroll', updateNavArrows);
  updateNavArrows();
}