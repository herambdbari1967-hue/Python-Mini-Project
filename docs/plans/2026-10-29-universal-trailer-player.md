# Universal HD Trailer Player Implementation Plan

> **For Claude / Antigravity:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task.

**Goal:** Eliminate the "Video unavailable" error when clicking "Watch Trailer" by replacing deprecated YouTube search-list embeds with a dynamic backend YouTube trailer resolver, verified trailer dictionary, and resilient Two26 modal player.

**Architecture:** 
1. **Root Cause Resolution**: YouTube deprecated and blocked `listType=search` in iframe embeds, which caused `trailer_id: "auto"` to fail universally.
2. **Dynamic Backend Resolver (`/api/trailer`)**: A cached, lightweight YouTube search scraper and curated dictionary that resolves exact 11-character YouTube video IDs on-demand in milliseconds.
3. **Resilient Frontend Player**: The modal seamlessly displays a sleek loading state while resolving dynamic IDs, embeds with `youtube-nocookie.com`, and provides an external "Watch on YouTube ↗" launcher if studio copyright restricts domain embedding.

**Tech Stack:** Python (Flask, regex, urllib), JavaScript (Fetch, DOM), HTML5/CSS3 (Two26 Design System).

---

### Task 1: Add Dynamic YouTube Trailer Resolver & Pre-Cached Catalog in `finder_engine.py`

**Files:**
- Modify: `finder_engine.py`

**Step 1: Define `CURATED_TRAILERS` Dictionary**
- Populate verified 11-character YouTube trailer IDs for popular Indian and international movies.

**Step 2: Implement `get_youtube_trailer_id(movie_title)` Function**
- Normalize movie title (strip special characters, year, language tags).
- Check `CURATED_TRAILERS` and `_trailer_cache`.
- If cache miss: Query `https://www.youtube.com/results?search_query={title}+official+trailer` with desktop User-Agent.
- Parse the 11-character `videoId` using regex `r'"videoId":"([a-zA-Z0-9_-]{11})"'`.
- Store in memory cache `_trailer_cache[title] = video_id` with TTL.
- Return resolved `video_id`.

**Step 3: Update Default Fallback Lists**
- Replace all placeholder `trailer_id: "auto"` in `NOW_SHOWING_MOVIES` and `UPCOMING_MOVIES` with curated IDs.

---

### Task 2: Add REST API Endpoint `/api/trailer` in `app.py`

**Files:**
- Modify: `app.py`

**Step 1: Implement `/api/trailer` Route**
- Accept GET parameter `title`.
- Call `get_youtube_trailer_id(title)`.
- If found: return JSON:
  ```json
  {
    "status": "success",
    "title": "Rajini: The Jailer 2",
    "trailer_id": "PWuJ5-WiEgY",
    "embed_url": "https://www.youtube-nocookie.com/embed/PWuJ5-WiEgY?autoplay=1&rel=0",
    "watch_url": "https://www.youtube.com/watch?v=PWuJ5-WiEgY"
  }
  ```

---

### Task 3: Enhance Trailer Modal UI in `templates/index.html`

**Files:**
- Modify: `templates/index.html`

**Step 1: Upgrade Modal Header Controls**
- Add external link button: `<a id="trailer-external-link" href="#" target="_blank" rel="noopener" class="trailer-external-btn">Watch on YouTube ↗</a>`.
- Add close button with Two26 capsule style.

**Step 2: Add Animated Skeleton Loading & Error Fallback Containers**
- Inside `#trailer-video-wrapper`, support dynamic rendering of:
  - Two26 Animated Loading Indicator (*"Locating Official 4K/HD Trailer..."*).
  - YouTube iframe (`youtube-nocookie.com`).
  - Studio restriction fallback banner with one-click direct YouTube launcher.

---

### Task 4: Revamp Client-Side Player in `static/js/main.js`

**Files:**
- Modify: `static/js/main.js`

**Step 1: Rewrite `openTrailerModal(trailerId, movieTitle)`**
- Check if `trailerId` is a valid 11-character string (`/^[a-zA-Z0-9_-]{11}$/`).
- **If valid**: Immediately render the iframe with `https://www.youtube-nocookie.com/embed/${trailerId}?autoplay=1&rel=0&modestbranding=1`.
- **If missing or "auto"**:
  - Show sleek loading state: `<div class="trailer-loading"><div class="spinner"></div><span>Fetching Official Trailer...</span></div>`.
  - Fetch `/api/trailer?title=${encodeURIComponent(movieTitle)}`.
  - On response: Update iframe and set `#trailer-external-link` href to `watch_url`.
  - Cache the resolved ID on the movie object in `currentMovies` so subsequent clicks are instantaneous.

---

### Task 5: Add Trailer Modal Styles in `static/css/style.css`

**Files:**
- Modify: `static/css/style.css`

**Step 1: Style Modal Elements**
- Style `.trailer-external-btn` (Two26 black capsule with orange hover).
- Style `.trailer-loading-spinner` and `.trailer-fallback-card`.
- Ensure 16:9 responsive aspect ratio for the video container across all devices.

---

### Task 6: Verification & End-to-End Testing

**Step 1: Unit Test `/api/trailer` Endpoint**
- Run test queries for now-showing and upcoming movies.
- Verify returned HTTP status is 200 and IDs are valid 11-character YouTube identifiers.

**Step 2: End-to-End Browser Verification**
- Click "Watch Trailer" across multiple cards (Now Showing + Upcoming).
- Confirm video loads and plays without "Video unavailable" error.
- Verify "Watch on YouTube ↗" link opens the official trailer.

**Step 3: Git Commit & Push**
- Stage, commit, and push changes to GitHub `main` branch.

