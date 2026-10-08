/**
 * main.js
 * Frontend controller for CinePlus - Movie Ticket Price & Show Finder Automation
 * Integrates Multi-Platform Live Booking (BookMyShow, PVR INOX, District, Cinépolis),
 * HD Trailer Popups, Upcoming Releases, and Price Matrix Comparisons.
 */

let currentMovies = [];
let currentUpcomingMovies = [];
let currentCity = 'Mumbai';
let activeCategory = 'all';
let currentMovieForCompare = null;
let currentActiveTab = 'now_showing'; // 'now_showing' | 'upcoming'

document.addEventListener('DOMContentLoaded', () => {
  loadMovies();
  loadAlerts();
  // Poll notifications every 15 seconds
  setInterval(loadAlerts, 15000);
});

// Switch between 'Now Showing' and 'Upcoming Movies'
function switchMainTab(tab) {
  currentActiveTab = tab;
  
  const navNowShowing = document.getElementById('nav-now-showing');
  const navUpcoming = document.getElementById('nav-upcoming');
  const categoryBar = document.getElementById('category-bar');
  const rankByBox = document.getElementById('rank-by-box');
  const sidebar = document.getElementById('main-sidebar');

  if (tab === 'now_showing') {
    navNowShowing.classList.add('active');
    navUpcoming.classList.remove('active');
    categoryBar.style.display = 'block';
    rankByBox.style.display = 'flex';
    sidebar.style.display = 'block';
    loadMovies();
  } else {
    navUpcoming.classList.add('active');
    navNowShowing.classList.remove('active');
    categoryBar.style.display = 'none';
    rankByBox.style.display = 'none';
    loadUpcomingMovies();
  }
}

// Load movies from REST API
async function loadMovies() {
  const city = document.getElementById('city-select').value;
  currentCity = city;
  const searchQuery = document.getElementById('nav-search-input').value;
  const sortBy = document.getElementById('sort-select').value;

  // Gather selected formats
  const formatCheckboxes = document.querySelectorAll('input[name="format_filter"]:checked');
  const formats = Array.from(formatCheckboxes).map(cb => cb.value);

  // Category pill override
  if (activeCategory !== 'all' && activeCategory !== 'budget') {
    if (!formats.includes(activeCategory)) {
      formats.push(activeCategory);
    }
  }

  // Price filter
  let maxPrice = null;
  const priceRadio = document.querySelector('input[name="price_filter"]:checked');
  if (priceRadio && priceRadio.value !== '1000') {
    maxPrice = parseInt(priceRadio.value);
  }
  if (activeCategory === 'budget') {
    maxPrice = 200;
  }

  // Chain filter
  const chainRadio = document.querySelector('input[name="chain_filter"]:checked');
  const chain = chainRadio ? chainRadio.value : 'All';

  let url = `/api/movies?city=${encodeURIComponent(city)}&sort_by=${sortBy}&chain=${encodeURIComponent(chain)}`;
  if (searchQuery) url += `&search=${encodeURIComponent(searchQuery)}`;
  if (maxPrice) url += `&max_price=${maxPrice}`;
  formats.forEach(f => { url += `&format=${encodeURIComponent(f)}`; });

  try {
    const res = await fetch(url);
    const data = await res.json();
    currentMovies = data.movies || [];
    renderMovieGrid(currentMovies);
    updateResultsCount(currentMovies.length, city, 'now_showing');
    populateAlertMovieDropdown(currentMovies);
  } catch (err) {
    console.error('Error fetching movies:', err);
  }
}

// Load Upcoming Tentpoles
async function loadUpcomingMovies() {
  const searchQuery = document.getElementById('nav-search-input').value;
  let url = '/api/upcoming';
  if (searchQuery) url += `?search=${encodeURIComponent(searchQuery)}`;

  try {
    const res = await fetch(url);
    const data = await res.json();
    currentUpcomingMovies = data.upcoming_movies || [];
    renderUpcomingGrid(currentUpcomingMovies);
    updateResultsCount(currentUpcomingMovies.length, currentCity, 'upcoming');
  } catch (err) {
    console.error('Error loading upcoming movies:', err);
  }
}

// Render Now Showing movie cards
function renderMovieGrid(movies) {
  const grid = document.getElementById('movie-grid');
  grid.innerHTML = '';

  if (movies.length === 0) {
    grid.innerHTML = `
      <div style="grid-column: 1 / -1; text-align: center; padding: 60px 20px;">
        <h3 style="font-size: 18px; margin-bottom: 8px;">No movie shows match your filters</h3>
        <p style="color: var(--text-secondary); margin-bottom: 20px;">Try adjusting your format or price filters.</p>
        <button class="action-btn secondary" onclick="resetAllFilters()">Reset All Filters</button>
      </div>
    `;
    return;
  }

  movies.forEach(mov => {
    const card = document.createElement('div');
    card.className = 'movie-card';

    // Show previews for first 2 theatres
    let showtimesHtml = '';
    if (mov.theatre_shows && mov.theatre_shows.length > 0) {
      const firstTheatre = mov.theatre_shows[0];
      showtimesHtml = `
        <div class="theatres-showtimes">
          <div class="theatre-row-preview">
            <strong>${escapeHtml(firstTheatre.theatre_name.split(':')[0])}</strong> (${firstTheatre.chain})
          </div>
          <div class="timing-chips">
            ${firstTheatre.shows.slice(0, 3).map(s => `
              <button class="timing-chip" onclick="openBookingPortalModal('${mov.id}', '${escapeHtml(firstTheatre.theatre_name)}', '${s.time}', '${s.format}')" title="Click to book: ${s.format} - Silver ₹${s.silver}">
                <span>${s.time}</span>
                <span class="chip-price">₹${s.silver}</span>
              </button>
            `).join('')}
          </div>
        </div>
      `;
    }

    card.innerHTML = `
      <div class="card-badge">${escapeHtml(mov.badge || 'New')}</div>
      <div class="card-poster-container">
        <img src="${mov.poster}" alt="${escapeHtml(mov.title)}" class="card-poster" loading="lazy">
      </div>
      <div class="card-info">
        <div class="card-meta">
          <span class="meta-rating">⭐ ${mov.rating}/10</span>
          <span>•</span>
          <span>${escapeHtml(mov.genre)}</span>
          <span>•</span>
          <span>${escapeHtml(mov.duration)}</span>
        </div>

        <h3 class="card-title">${escapeHtml(mov.title)}</h3>
        <div class="card-discount-tag">${escapeHtml(mov.discount_tag)}</div>

        <div class="card-price-row">
          <span class="price-label">Starts at</span>
          <span class="price-val">₹${mov.min_price}</span>
          <span style="font-size: 11px; color: var(--text-secondary); margin-left: 4px;">in ${escapeHtml(mov.theatre_count)} multiplexes</span>
        </div>

        ${showtimesHtml}

        <div class="card-actions">
          <button class="action-btn secondary" onclick="openCompareModal('${mov.id}')">
            📊 Compare Prices
          </button>
          <button class="action-btn primary" onclick="openBookingPortalModal('${mov.id}')">
            🎟️ Book Now ➔
          </button>
          ${mov.trailer_id ? `
            <button class="action-btn trailer-btn" onclick="openTrailerModal('${mov.trailer_id}', '${escapeHtml(mov.title)}')">
              🎬 Watch Trailer
            </button>
          ` : ''}
          <button class="action-btn track-btn" onclick="openAlertForMovie('${mov.id}', '${escapeHtml(mov.title)}', ${mov.min_price})">
            🔔 Set Price Drop Watcher
          </button>
        </div>
      </div>
    `;

    grid.appendChild(card);
  });
}

// Render Upcoming Movies Grid
function renderUpcomingGrid(upcoming) {
  const grid = document.getElementById('movie-grid');
  grid.innerHTML = '';

  if (upcoming.length === 0) {
    grid.innerHTML = `
      <div style="grid-column: 1 / -1; text-align: center; padding: 60px 20px;">
        <h3 style="font-size: 18px;">No upcoming movies found</h3>
        <p style="color: var(--text-secondary);">Try clearing your search keyword.</p>
      </div>
    `;
    return;
  }

  upcoming.forEach(mov => {
    const card = document.createElement('div');
    card.className = 'movie-card';

    card.innerHTML = `
      <div class="upcoming-release-badge">🗓️ ${escapeHtml(mov.release_date)}</div>
      <div class="card-badge" style="background-color: #0284c7;">${escapeHtml(mov.badge)}</div>
      <div class="card-poster-container">
        <img src="${mov.poster}" alt="${escapeHtml(mov.title)}" class="card-poster" loading="lazy">
      </div>
      <div class="card-info">
        <div class="hype-badge">🔥 ${escapeHtml(mov.hype_score)}</div>
        <div class="card-meta">
          <span>${escapeHtml(mov.certificate)}</span>
          <span>•</span>
          <span>${escapeHtml(mov.genre)}</span>
        </div>

        <h3 class="card-title">${escapeHtml(mov.title)}</h3>
        <p style="font-size: 12px; color: var(--text-secondary); line-height: 1.4; margin-bottom: 12px;">
          ${escapeHtml(mov.synopsis)}
        </p>

        <div style="font-size: 11px; color: var(--text-secondary); margin-bottom: 12px;">
          <strong>Starring:</strong> ${mov.cast ? mov.cast.join(', ') : 'All-Star Cast'}<br>
          <strong>Director:</strong> ${escapeHtml(mov.director)}
        </div>

        <div class="card-actions">
          <button class="action-btn trailer-btn" style="width: 100%; margin-bottom: 6px;" onclick="openTrailerModal('${mov.trailer_id}', '${escapeHtml(mov.title)}')">
            ▶️ Watch Official Trailer
          </button>
          <button class="action-btn primary" style="width: 100%;" onclick="openAlertForMovie('${mov.id}', '${escapeHtml(mov.title)}', 250)">
            🔔 Notify on Ticket Opening
          </button>
        </div>
      </div>
    `;

    grid.appendChild(card);
  });
}

function updateResultsCount(count, city, type) {
  const el = document.getElementById('results-count-text');
  if (type === 'upcoming') {
    el.textContent = `Showing ${count} Upcoming Blockbusters & Tentpoles`;
  } else {
    el.textContent = `Showing ${count} live movies in ${city}`;
  }
}

// Multi-Platform Live Booking Modal Launcher
async function openBookingPortalModal(movieId, theatreName = null, showTime = null, format = null) {
  const modal = document.getElementById('booking-portal-modal');
  const modalBody = document.getElementById('booking-modal-body');
  
  modalBody.innerHTML = '<div style="text-align: center; padding: 40px;">Fetching live booking portals and offers...</div>';
  modal.style.display = 'flex';

  try {
    const res = await fetch(`/api/booking-details?movie_id=${movieId}&city=${encodeURIComponent(currentCity)}`);
    const data = await res.json();
    if (data.status === 'success') {
      const d = data.data;
      const movie = d.movie;
      const links = d.platform_links;
      const selectedTheatre = theatreName || d.theatre_name;

      modalBody.innerHTML = `
        <div style="display: flex; gap: 16px; align-items: center; border-bottom: 1px solid var(--border-light); padding-bottom: 16px;">
          <img src="${movie.poster}" alt="${escapeHtml(movie.title)}" style="width: 70px; height: 100px; object-fit: cover; border-radius: var(--radius-sm);">
          <div>
            <h3 style="font-size: 18px; font-weight: 700;">${escapeHtml(movie.title)}</h3>
            <p style="font-size: 13px; color: var(--text-secondary); margin: 3px 0;">
              ${escapeHtml(movie.genre)} • ⭐ ${movie.rating}/10 (${movie.votes || 'Popular'})
            </p>
            <p style="font-size: 12px; color: var(--brand-red); font-weight: 600;">
              📍 ${escapeHtml(selectedTheatre)} ${showTime ? `• ⏰ ${showTime} (${format})` : ''}
            </p>
          </div>
        </div>

        <div class="platform-choices-grid">
          <!-- BookMyShow -->
          <div class="platform-choice-card">
            <div class="platform-card-header">
              <span class="platform-name" style="color: #eb0028;">🔴 BookMyShow</span>
              <span class="platform-tag" style="background: #fff0f2; color: #eb0028;">Official API</span>
            </div>
            <p class="platform-desc">Instant seat reservation, M-Ticket on WhatsApp & food pre-orders.</p>
            <a href="${links.bookmyshow}" target="_blank" class="platform-launch-btn btn-bms" onclick="trackBookingClick('BookMyShow', '${escapeHtml(movie.title)}')">
              Launch BookMyShow ➔
            </a>
          </div>

          <!-- PVR INOX -->
          <div class="platform-choice-card">
            <div class="platform-card-header">
              <span class="platform-name" style="color: #d97706;">🎬 PVR INOX Cinemas</span>
              <span class="platform-tag" style="background: #fffbf0; color: #d97706;">Direct Multiplex</span>
            </div>
            <p class="platform-desc">Zero convenience fee on Passport subscribers & luxury recliner deals.</p>
            <a href="${links.pvr_inox}" target="_blank" class="platform-launch-btn btn-pvr" onclick="trackBookingClick('PVR INOX', '${escapeHtml(movie.title)}')">
              Launch PVR INOX ➔
            </a>
          </div>

          <!-- District by Zomato -->
          <div class="platform-choice-card">
            <div class="platform-card-header">
              <span class="platform-name" style="color: #7c3aed;">⚡ District (by Zomato)</span>
              <span class="platform-tag" style="background: #f3f0ff; color: #7c3aed;">Fast Checkout</span>
            </div>
            <p class="platform-desc">Zomato Gold dining combos & instant cashback on movie tickets.</p>
            <a href="${links.district}" target="_blank" class="platform-launch-btn btn-district" onclick="trackBookingClick('District', '${escapeHtml(movie.title)}')">
              Launch District ➔
            </a>
          </div>

          <!-- Cinépolis India -->
          <div class="platform-choice-card">
            <div class="platform-card-header">
              <span class="platform-name" style="color: #0284c7;">🎟️ Cinépolis India</span>
              <span class="platform-tag" style="background: #f0f7ff; color: #0284c7;">Club Cinépolis</span>
            </div>
            <p class="platform-desc">Earn Club Cinepolis points & exclusive Wednesday saver discounts.</p>
            <a href="${links.cinepolis}" target="_blank" class="platform-launch-btn btn-cinepolis" onclick="trackBookingClick('Cinépolis', '${escapeHtml(movie.title)}')">
              Launch Cinépolis ➔
            </a>
          </div>
        </div>

        <!-- Promo Section -->
        <div class="promo-section-box">
          <strong style="font-size: 13px;">🎁 Verified Discount Coupons (Click to Copy):</strong>
          <div class="promo-grid">
            ${d.promos.map(p => `
              <div class="promo-chip" onclick="copyPromoCode('${p.code}')" title="Click to copy coupon code">
                <div>
                  <span class="promo-code-text">${p.code}</span>
                  <div style="font-size: 10px; color: var(--text-secondary);">${p.desc}</div>
                </div>
                <span style="font-size: 10px; color: var(--brand-red); font-weight: 700;">COPY</span>
              </div>
            `).join('')}
          </div>
        </div>
      `;
    }
  } catch (err) {
    modalBody.innerHTML = '<p style="color: red; text-align: center;">Error loading platform booking links.</p>';
  }
}

function closeBookingPortalModal() {
  document.getElementById('booking-portal-modal').style.display = 'none';
}

function trackBookingClick(platform, movieTitle) {
  showToast(`🚀 Opening ${platform} for ${movieTitle}...`);
}

function copyPromoCode(code) {
  navigator.clipboard.writeText(code).then(() => {
    showToast(`✅ Coupon code ${code} copied to clipboard!`);
  }).catch(() => {
    showToast(`Coupon: ${code}`);
  });
}

// Trailer Modal Player
function openTrailerModal(trailerId, movieTitle) {
  const modal = document.getElementById('trailer-modal');
  const titleEl = document.getElementById('trailer-modal-title');
  const wrapper = document.getElementById('trailer-video-wrapper');

  titleEl.textContent = `${movieTitle} - Official Trailer (HD)`;
  wrapper.innerHTML = `
    <iframe src="https://www.youtube.com/embed/${trailerId}?autoplay=1&rel=0&modestbranding=1" 
            title="${escapeHtml(movieTitle)}" 
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
            allowfullscreen>
    </iframe>
  `;
  modal.style.display = 'flex';
}

function closeTrailerModal() {
  const modal = document.getElementById('trailer-modal');
  const wrapper = document.getElementById('trailer-video-wrapper');
  wrapper.innerHTML = '';
  modal.style.display = 'none';
}

// Category Pill Bar
function selectCategoryPill(btn, cat) {
  document.querySelectorAll('.cat-item').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  activeCategory = cat;
  loadMovies();
}

function filterCategory(cat) {
  activeCategory = cat;
  document.querySelectorAll('.cat-item').forEach(b => b.classList.remove('active'));
  document.querySelector('.cat-item').classList.add('active');
  loadMovies();
}

function onCityChange() {
  if (currentActiveTab === 'now_showing') {
    loadMovies();
  }
}

let searchTimer;
function onSearchInput(val) {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => {
    if (currentActiveTab === 'upcoming') {
      loadUpcomingMovies();
    } else {
      loadMovies();
    }
  }, 300);
}

function applyFilters() {
  loadMovies();
}

function resetAllFilters() {
  document.querySelectorAll('input[name="format_filter"]').forEach(cb => cb.checked = false);
  document.querySelector('input[name="price_filter"][value="1000"]').checked = true;
  document.querySelector('input[name="chain_filter"][value="All"]').checked = true;
  document.getElementById('nav-search-input').value = '';
  document.querySelectorAll('.cat-item').forEach(b => b.classList.remove('active'));
  document.querySelector('.cat-item').classList.add('active');
  activeCategory = 'all';
  loadMovies();
}

// Price Comparison Modal
async function openCompareModal(movieId) {
  currentMovieForCompare = movieId;
  const modal = document.getElementById('compare-modal');
  const modalBody = document.getElementById('compare-modal-body');
  modalBody.innerHTML = '<div style="text-align: center; padding: 40px;">Calculating price comparison matrix across multiplexes...</div>';
  modal.style.display = 'flex';

  try {
    const res = await fetch(`/api/comparison?movie_id=${movieId}&city=${encodeURIComponent(currentCity)}`);
    const data = await res.json();
    if (data.status === 'success') {
      renderComparisonModal(data.comparison);
    }
  } catch (err) {
    modalBody.innerHTML = '<p style="color: red;">Error loading comparison matrix.</p>';
  }
}

function renderComparisonModal(comp) {
  document.getElementById('compare-movie-title').textContent = `${comp.movie_title} - Price Comparison`;
  document.getElementById('compare-movie-city').textContent = `Aggregating ${comp.total_shows} showtimes across ${currentCity}`;

  const cheapest = comp.cheapest_option;
  const modalBody = document.getElementById('compare-modal-body');

  let rowsHtml = comp.comparison_table.map((row, idx) => {
    const isCheapest = idx === 0;
    return `
      <tr class="${isCheapest ? 'cheapest-row' : ''}">
        <td>
          <strong>${escapeHtml(row.theatre)}</strong>
          ${isCheapest ? '<span class="badge-cheapest">Lowest Price</span>' : ''}
          <div style="font-size: 11px; color: var(--text-secondary);">${row.chain} • ⭐ ${row.theatre_rating} • ${row.location}</div>
        </td>
        <td><strong>${row.time}</strong></td>
        <td><span style="font-weight: 600;">${row.format}</span></td>
        <td><strong>₹${row.silver_price}</strong></td>
        <td>₹${row.gold_price}</td>
        <td>₹${row.recliner_price}</td>
        <td><span style="color: ${row.seats_left < 10 ? 'var(--brand-red)' : '#27ae60'}; font-weight: 600;">${row.seats_left} seats</span></td>
        <td>
          <button class="action-btn primary" style="padding: 4px 10px; font-size: 11px;" onclick="openBookingPortalModal('${comp.cheapest_option ? currentMovieForCompare : ''}', '${escapeHtml(row.theatre)}', '${row.time}', '${row.format}')">
            Book ➔
          </button>
        </td>
      </tr>
    `;
  }).join('');

  modalBody.innerHTML = `
    <div style="background-color: var(--brand-red-light); padding: 14px 18px; border-radius: var(--radius-sm); border: 1px solid #ffd1d8; display: flex; align-items: center; justify-content: space-between;">
      <div>
        <strong>🏆 Best Deal Found:</strong> ${escapeHtml(cheapest.theatre)} (${cheapest.format}) at <strong>₹${cheapest.silver_price}</strong>
      </div>
      <button class="action-btn primary" style="font-size: 12px; padding: 6px 12px;" onclick="openBookingPortalModal('${currentMovieForCompare}', '${escapeHtml(cheapest.theatre)}', '${cheapest.time}', '${cheapest.format}')">
        Book Lowest Price
      </button>
    </div>

    <div class="comparison-table-wrapper">
      <table class="compare-table">
        <thead>
          <tr>
            <th>Theatre & Location</th>
            <th>Showtime</th>
            <th>Format</th>
            <th>Silver Tier</th>
            <th>Gold Tier</th>
            <th>VIP Recliner</th>
            <th>Seats Left</th>
            <th>1-Click Booking</th>
          </tr>
        </thead>
        <tbody>
          ${rowsHtml}
        </tbody>
      </table>
    </div>
  `;
}

function closeCompareModal() {
  document.getElementById('compare-modal').style.display = 'none';
}

function openQuickCompare() {
  if (currentMovies.length > 0) {
    openCompareModal(currentMovies[0].id);
  }
}

// Price Alert & Notification Manager
async function loadAlerts() {
  try {
    const res = await fetch('/api/alerts');
    const data = await res.json();
    if (data.status === 'success') {
      renderAlertsList(data.alerts);
      renderNotificationsList(data.notifications);

      document.getElementById('alert-badge-count').textContent = data.alerts.length;
      document.getElementById('active-alerts-count').textContent = data.alerts.length;
      document.getElementById('notif-count').textContent = data.notifications.length;

      const dot = document.getElementById('notif-dot');
      if (data.notifications.length > 0) {
        dot.style.display = 'block';
      }
    }
  } catch (err) {
    console.error('Error loading alerts:', err);
  }
}

function renderAlertsList(alerts) {
  const container = document.getElementById('active-alerts-list');
  if (!alerts || alerts.length === 0) {
    container.innerHTML = '<p style="color: var(--text-secondary); font-size: 12px;">No active price alerts. Add one above!</p>';
    return;
  }

  container.innerHTML = alerts.map(a => `
    <div class="alert-item-card">
      <div>
        <strong>${escapeHtml(a.movie_title)}</strong> in ${escapeHtml(a.city)}
        <div style="font-size: 11px; color: var(--text-secondary);">
          Target: ₹${a.target_price} | Current: ₹${a.last_price_found || 'Scanning...'} | Format: ${a.format_type}
        </div>
      </div>
      <button class="reset-link" style="color: var(--brand-red); font-size: 12px;" onclick="deleteAlert('${a.id}')">Delete</button>
    </div>
  `).join('');
}

function renderNotificationsList(notifs) {
  const container = document.getElementById('notif-history-list');
  if (!notifs || notifs.length === 0) {
    container.innerHTML = '<p style="color: var(--text-secondary); font-size: 12px;">No price drop triggers yet.</p>';
    return;
  }

  container.innerHTML = notifs.map(n => `
    <div class="notif-item-card">
      <div>
        <strong>${escapeHtml(n.title)}</strong>
        <div style="font-size: 12px; color: var(--text-primary);">${escapeHtml(n.message)}</div>
        <div style="font-size: 10px; color: var(--text-secondary); margin-top: 2px;">${n.timestamp}</div>
      </div>
    </div>
  `).join('');
}

function populateAlertMovieDropdown(movies) {
  const select = document.getElementById('alert-movie-select');
  select.innerHTML = movies.map(m => `
    <option value="${m.id}" data-title="${escapeHtml(m.title)}">${escapeHtml(m.title)} (from ₹${m.min_price})</option>
  `).join('');
}

function openAlertForMovie(movieId, title, currentMin) {
  openAlertsModal();
  const select = document.getElementById('alert-movie-select');
  select.value = movieId;
  document.getElementById('alert-target-price').value = Math.max(50, currentMin - 40);
}

function openAlertsModal() {
  document.getElementById('alert-modal').style.display = 'flex';
  loadAlerts();
}

function closeAlertsModal() {
  document.getElementById('alert-modal').style.display = 'none';
}

async function submitNewAlert(e) {
  e.preventDefault();
  const movieSelect = document.getElementById('alert-movie-select');
  const movieId = movieSelect.value;
  const movieTitle = movieSelect.options[movieSelect.selectedIndex]?.getAttribute('data-title') || movieSelect.options[movieSelect.selectedIndex]?.text.split('(')[0].trim() || 'Movie';
  const city = document.getElementById('alert-city-select').value;
  const targetPrice = document.getElementById('alert-target-price').value;
  const formatType = document.getElementById('alert-format-select').value;

  try {
    const res = await fetch('/api/alerts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        movie_id: movieId,
        movie_title: movieTitle,
        city: city,
        target_price: targetPrice,
        format_type: formatType
      })
    });
    const data = await res.json();
    if (data.status === 'success') {
      showToast(`⚡ Price alert activated for ${movieTitle} under ₹${targetPrice}!`);
      loadAlerts();
    }
  } catch (err) {
    showToast('Failed to create alert');
  }
}

async function deleteAlert(alertId) {
  try {
    await fetch(`/api/alerts?alert_id=${alertId}`, { method: 'DELETE' });
    showToast('Alert removed');
    loadAlerts();
  } catch (err) {
    console.error(err);
  }
}

// Pandas Data Exports
function exportDataCSV() {
  const city = document.getElementById('city-select').value;
  const search = document.getElementById('nav-search-input').value;
  window.location.href = `/api/export/shows?city=${encodeURIComponent(city)}&search=${encodeURIComponent(search)}`;
  showToast('📥 Exporting movie shows dataset via Pandas (CSV)...');
}

function exportComparisonCSV() {
  if (currentMovieForCompare) {
    window.location.href = `/api/export/comparison?movie_id=${currentMovieForCompare}&city=${encodeURIComponent(currentCity)}`;
    showToast('📥 Exporting price comparison report (CSV)...');
  }
}

// Toast notification helper
function showToast(msg) {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.innerHTML = `<span>${escapeHtml(msg)}</span>`;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
