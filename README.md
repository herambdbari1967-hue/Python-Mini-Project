# CinePlus - Movie Ticket Price & Show Finder Automation 🎬

A modern Python automation web application developed according to the project proposal document (**`Movie_Ticket_Price_Show_Finder_Project_Proposal.docx`**). The application features a clean, minimalist UI inspired by the OnePlus Store design layout.

---

## 🚀 Key Features

1. **City & Multiplex Show Finder**
   - Live showtime discovery across major cities: **Mumbai, Delhi NCR, Bengaluru, Hyderabad, Pune, Chennai, Kolkata, Ahmedabad**.
   - Aggregates shows across top cinema chains: **PVR INOX, Cinépolis, MovieMax, Miraj Cinemas**.

2. **OnePlus Store-Inspired UI Layout**
   - Minimalist top navigation with city selector, live search, and notification badges.
   - Horizontal category icon bar with active underline indicator (**All Shows, IMAX 3D, 4DX Motion, Dolby Atmos, 2D Standard, 3D Glasses, Under ₹200**).
   - Left sidebar multi-select filters (**Screen Format, Price Ranges, Theatre Chains, Show Timings**) with red accent tags (`New`, `Popular`, `Best Deal`).
   - Clean 3-column product cards with deal badges, live price tags, and theatre showtime chips.

3. **Multi-Tier Price Comparison Matrix (Pandas Integration)**
   - Side-by-side comparison modal across **Silver**, **Gold**, and **VIP Recliner** seat tiers.
   - Instant identification of the lowest price theatre and best luxury value.

4. **Automated Price Drop Tracker & Notifications (`schedule` & `threading`)**
   - Background daemon watcher that continuously monitors ticket price thresholds.
   - Logs price drops and triggers in-app alerts when ticket prices drop within budget.

5. **1-Click Direct Booking Launcher**
   - Direct button links to launch the booking portal (`BookMyShow` / `PVR INOX`) for any selected movie and showtime.

6. **Data Export (`pandas`)**
   - One-click CSV export of showtimes and price comparison matrices.

---

## 📂 Project Structure

```
c:\Users\ratho\OneDrive\Desktop\Python App\
├── app.py                      # Flask Application server & REST API controller
├── finder_engine.py            # Show aggregation, theatre catalog, price comparison engine
├── price_tracker.py            # Background price drop tracker (threading & schedule)
├── data_exporter.py            # Pandas export utility for CSV dataset generation
├── static/
│   ├── css/
│   │   └── style.css           # Custom OnePlus design system & styling
│   └── js/
│       └── main.js             # Client-side dynamic filters, modals, and event handlers
└── templates/
    └── index.html              # Main HTML template
```

---

## 🛠️ How to Run

1. Open your terminal in this directory:
   ```bash
   cd "c:\Users\ratho\OneDrive\Desktop\Python App"
   ```

2. Run the application:
   ```bash
   python app.py
   ```

3. The application will start the Flask server and **automatically launch your browser** at:
   ```
   http://127.0.0.1:5000
   ```

---

## 📦 Installed Dependencies Used
- `Flask` - Web application server & API
- `pandas` - Price matrix aggregation & CSV exports
- `schedule` - Automated background price monitoring
- `requests` & `beautifulsoup4` - Web scraping utilities
- `selenium` - Automation and booking launcher support
