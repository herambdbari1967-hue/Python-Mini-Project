"""
price_tracker.py
Background price tracking and alert notification engine.
Allows users to subscribe to price drops on specific movies and formats.
Runs background polling with schedule and logs/triggers notifications.
"""

import threading
import time
import schedule
from datetime import datetime
from finder_engine import get_movie_shows

class PriceAlertManager:
    def __init__(self):
        self.alerts = []
        self.notification_history = []
        self.is_running = False
        self._thread = None
        self._lock = threading.Lock()

    def add_alert(self, movie_id, movie_title, target_price, city="Mumbai", format_type="All", email=None):
        """Adds a price alert watcher"""
        with self._lock:
            alert = {
                "id": f"alert-{int(time.time() * 1000)}",
                "movie_id": movie_id,
                "movie_title": movie_title,
                "target_price": int(target_price),
                "city": city,
                "format_type": format_type,
                "email": email or "user@example.com",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "Active",
                "last_checked": None,
                "last_price_found": None
            }
            self.alerts.append(alert)
            self._check_single_alert(alert)
            return alert

    def get_alerts(self):
        """Returns list of active alerts"""
        with self._lock:
            return list(self.alerts)

    def delete_alert(self, alert_id):
        """Removes an alert by ID"""
        with self._lock:
            self.alerts = [a for a in self.alerts if a["id"] != alert_id]
            return True

    def get_notifications(self):
        """Returns trigger history"""
        with self._lock:
            return list(self.notification_history)

    def _check_single_alert(self, alert):
        """Evaluates price condition against current movie database"""
        shows = get_movie_shows(city=alert["city"])
        for m in shows:
            if m["id"] == alert["movie_id"] or m["title"].lower() == alert["movie_title"].lower():
                current_min = m["min_price"]
                alert["last_checked"] = datetime.now().strftime("%H:%M:%S")
                alert["last_price_found"] = current_min

                if current_min <= alert["target_price"]:
                    alert["status"] = "TRIGGERED"
                    notif = {
                        "id": f"notif-{int(time.time() * 1000)}",
                        "title": f"🎉 Price Drop Alert: {alert['movie_title']}",
                        "message": f"Tickets for {alert['movie_title']} in {alert['city']} are now available for ₹{current_min} (Target: ₹{alert['target_price']})!",
                        "movie_title": alert["movie_title"],
                        "city": alert["city"],
                        "price": current_min,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    if not any(n["title"] == notif["title"] and n["price"] == current_min for n in self.notification_history):
                        self.notification_history.insert(0, notif)
                break

    def check_all_alerts(self):
        """Runs check on all alerts"""
        with self._lock:
            for alert in self.alerts:
                self._check_single_alert(alert)

    def start_scheduler(self):
        """Starts background periodic checking thread using schedule library"""
        if self.is_running:
            return

        self.is_running = True
        schedule.every(30).seconds.do(self.check_all_alerts)

        def run_loop():
            while self.is_running:
                schedule.run_pending()
                time.sleep(1)

        self._thread = threading.Thread(target=run_loop, daemon=True)
        self._thread.start()

# Global alert manager singleton
alert_manager = PriceAlertManager()
alert_manager.start_scheduler()
