"""
data_exporter.py
High-performance data export utility for Movie Ticket Price & Show Finder.
Exports show listings, theatre price comparisons, and alerts to CSV formats.
Compatible with standard csv module and pandas.
"""

import io
import csv

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

from finder_engine import get_movie_shows, get_price_comparison

def export_shows_to_csv(city="Mumbai", search_query=None):
    """Exports all available shows for a city to a CSV buffer"""
    movies = get_movie_shows(city=city, search_query=search_query)
    
    rows = []
    for m in movies:
        for t in m["theatre_shows"]:
            for s in t["shows"]:
                rows.append({
                    "Movie Title": m["title"],
                    "City": city,
                    "Genre": m["genre"],
                    "Rating": m["rating"],
                    "Theatre": t["theatre_name"],
                    "Chain": t["chain"],
                    "Show Time": s["time"],
                    "Format": s["format"],
                    "Silver Price (Rs)": s["silver"],
                    "Gold Price (Rs)": s["gold"],
                    "Recliner Price (Rs)": s["recliner"],
                    "Seats Available": s["seats_left"],
                    "Booking URL": s["booking_url"]
                })
                
    if not rows:
        return ""

    if HAS_PANDAS:
        df = pd.DataFrame(rows)
        output = io.StringIO()
        df.to_csv(output, index=False)
        return output.getvalue()
    else:
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
        return output.getvalue()

def export_comparison_to_csv(movie_id, city="Mumbai"):
    """Exports price comparison breakdown for a single movie"""
    comparison = get_price_comparison(movie_id, city=city)
    if not comparison:
        return ""
        
    rows = []
    for r in comparison["comparison_table"]:
        rows.append({
            "Movie": comparison["movie_title"],
            "City": city,
            "Theatre": r["theatre"],
            "Chain": r["chain"],
            "Rating": r["theatre_rating"],
            "Show Time": r["time"],
            "Format": r["format"],
            "Silver (Rs)": r["silver_price"],
            "Gold (Rs)": r["gold_price"],
            "Recliner (Rs)": r["recliner_price"],
            "Seats Left": r["seats_left"]
        })
        
    if not rows:
        return ""

    if HAS_PANDAS:
        df = pd.DataFrame(rows)
        output = io.StringIO()
        df.to_csv(output, index=False)
        return output.getvalue()
    else:
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
        return output.getvalue()
