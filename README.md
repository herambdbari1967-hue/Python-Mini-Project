# CinePlus - Movie Ticket Price & Show Finder Automation 🎬

A modern Python automation web application developed according to the project proposal document (**`Movie_Ticket_Price_Show_Finder_Project_Proposal.docx`**). The application features an editorial, high-craft UI inspired by the **Two26 Studio** design system (`https://two26.studio/`), live BookMyShow SSR aggregation, multi-platform booking deep links, and automated price drop tracking.

---

## 🚀 Key Features

1. **Two26 Studio Design System UI**
   - High-contrast typography featuring **MD Nichrome** and **Neue Montreal**.
   - Signature animated hero loop (`hero.mp4`) with synchronized split typography.
   - Interactive capsule pills, smooth horizontal marquee ribbons, and high-craft modal sheets.

2. **Real-Time City & Multiplex Show Aggregation**
   - Live showtime discovery across major Indian metro hubs: **Mumbai, Delhi NCR, Bengaluru, Hyderabad, Pune, Chennai, Kolkata, Ahmedabad**.
   - Aggregates shows across top cinema chains: **PVR INOX, Cinépolis, MovieMax, Miraj Cinemas, Prasads Multiplex**.
   - Direct integration with BookMyShow SSR endpoints with fail-safe local fallback catalog.

3. **Multi-Platform Direct Booking Deep-Links**
   - 1-click booking launchers that deep-link directly into:
     - **BookMyShow**
     - **PVR INOX**
     - **District by Zomato (Paytm Insider)**
     - **Cinépolis India**

4. **Multi-Tier Price Comparison Matrix**
   - Side-by-side comparison across **Silver**, **Gold**, and **VIP Recliner** seat tiers.
   - Instant identification of the lowest price theatre and luxury recliner deals.

5. **Price Drop Tracker & Notifications**
   - Background price drop watcher with target budget thresholds.
   - Real-time in-app badge alerts and toast notifications when prices drop.

6. **Dataset Export**
   - One-click CSV export of showtimes and price comparison matrices.

---

## 📂 Project Structure

```
├── api/
│   └── index.py                # Vercel serverless entry point
├── static/
│   ├── css/
│   │   └── style.css           # Two26 Studio design system & styling
│   ├── fonts/                  # MD Nichrome & Neue Montreal webfonts
│   ├── images/                 # Editorial visuals & posters
│   ├── js/
│   │   └── main.js             # Client-side dynamic filters, modals, and event handlers
│   └── videos/
│       └── hero.mp4            # Two26 3D animated hero video loop
├── templates/
│   └── index.html              # Main HTML template
├── app.py                      # Flask Application server & REST API controller
├── finder_engine.py            # Live aggregation, SSR scraper, multi-platform deep links
├── price_tracker.py            # Price drop tracking & notification manager
├── data_exporter.py            # CSV dataset generation (pandas / csv fallback)
├── requirements.txt            # Python dependencies
└── vercel.json                 # Vercel deployment & routing configuration
```

---

## 🛠️ How to Run Locally

1. Clone the repository and navigate to the folder:
   ```bash
   git clone https://github.com/herambdbari1967-hue/Python-Mini-Project.git
   cd Python-Mini-Project
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python app.py
   ```

4. The server starts at `http://127.0.0.1:5000` and automatically opens in your default browser.

---

## ☁️ Deploy to Vercel (1-Click Ready)

This repository is pre-configured with [`vercel.json`](vercel.json) and [`api/index.py`](api/index.py) for turnkey Vercel deployment:

1. Push your repository to GitHub (or use this repo).
2. Go to [Vercel Dashboard](https://vercel.com/dashboard) and click **"Add New Project"**.
3. Import this repository (`Python-Mini-Project`).
4. Click **"Deploy"** (leave all settings default).
5. Vercel automatically:
   - Deploys the Python serverless function via `api/index.py`.
   - Distributes all static assets (fonts, video, CSS, JS) over the Vercel Global Edge CDN with zero-config caching headers.
