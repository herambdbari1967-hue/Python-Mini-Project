"""
data_exporter.py
Pandas-powered data export utility for Movie Ticket Price & Show Finder.
Exports show listings, theatre price comparisons, and alerts to CSV/Excel formats.
"""

import io
import pandas as pd
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
                    "Silver Price (₹)": s["silver"],
                    "Gold Price (₹)": s["gold"],
                    "Recliner Price (₹)": s["recliner"],
                    "Seats Available": s["seats_left"],
                    "Booking URL": s["booking_url"]
                })
                
    df = pd.DataFrame(rows)
    output = io.StringIO()
    df.to_csv(output, index=False)
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
            "Silver (₹)": r["silver_price"],
            "Gold (₹)": r["gold_price"],
            "Recliner (₹)": r["recliner_price"],
            "Seats Left": r["seats_left"]
        })
        
    df = pd.DataFrame(rows)
    output = io.StringIO()
    df.to_csv(output, index=False)
    return output.getvalue()
