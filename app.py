"""
app.py
Main entry point for Movie Ticket Price & Show Finder Automation.
Launches Flask web server and serves the OnePlus-inspired interface with live data,
upcoming movies, price comparison matrix, and multi-platform direct booking launchers.
"""

import os
import sys
import webbrowser
import threading
from flask import Flask, render_template, request, jsonify, Response
from finder_engine import (
    CITIES, THEATRES, NOW_SHOWING_MOVIES, UPCOMING_MOVIES, PROMO_CODES,
    get_movie_shows, get_upcoming_movies, get_price_comparison, get_booking_details
)
from price_tracker import alert_manager
from data_exporter import export_shows_to_csv, export_comparison_to_csv

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', cities=CITIES)

@app.route('/api/movies', methods=['GET'])
def api_movies():
    city = request.args.get('city', 'Mumbai')
    search = request.args.get('search', '')
    formats = request.args.getlist('format')
    max_price = request.args.get('max_price', type=int)
    chain = request.args.get('chain', 'All')
    sort_by = request.args.get('sort_by', 'cheapest')
    
    shows = get_movie_shows(
        city=city, 
        search_query=search, 
        selected_formats=formats if formats else None,
        max_price=max_price,
        theatre_chain=chain,
        sort_by=sort_by
    )
    return jsonify({
        "status": "success",
        "count": len(shows),
        "city": city,
        "movies": shows
    })

@app.route('/api/upcoming', methods=['GET'])
def api_upcoming():
    search = request.args.get('search', '')
    upcoming = get_upcoming_movies(search_query=search)
    return jsonify({
        "status": "success",
        "count": len(upcoming),
        "upcoming_movies": upcoming
    })

@app.route('/api/comparison', methods=['GET'])
def api_comparison():
    movie_id = request.args.get('movie_id')
    city = request.args.get('city', 'Mumbai')
    if not movie_id:
        return jsonify({"status": "error", "message": "movie_id is required"}), 400
        
    data = get_price_comparison(movie_id, city=city)
    if not data:
        return jsonify({"status": "error", "message": "Movie not found"}), 404
        
    return jsonify({"status": "success", "comparison": data})

@app.route('/api/booking-details', methods=['GET'])
def api_booking_details():
    movie_id = request.args.get('movie_id')
    city = request.args.get('city', 'Mumbai')
    theatre_id = request.args.get('theatre_id')
    
    if not movie_id:
        return jsonify({"status": "error", "message": "movie_id is required"}), 400
        
    data = get_booking_details(movie_id, theatre_id=theatre_id, city=city)
    if not data:
        return jsonify({"status": "error", "message": "Movie not found"}), 404
        
    return jsonify({"status": "success", "data": data})

@app.route('/api/promos', methods=['GET'])
def api_promos():
    return jsonify({
        "status": "success",
        "promos": PROMO_CODES
    })

@app.route('/api/alerts', methods=['GET', 'POST', 'DELETE'])
def api_alerts():
    if request.method == 'GET':
        return jsonify({
            "status": "success",
            "alerts": alert_manager.get_alerts(),
            "notifications": alert_manager.get_notifications()
        })
        
    elif request.method == 'POST':
        payload = request.get_json() or {}
        movie_id = payload.get('movie_id')
        movie_title = payload.get('movie_title')
        target_price = payload.get('target_price', 200)
        city = payload.get('city', 'Mumbai')
        format_type = payload.get('format_type', 'All')
        email = payload.get('email', '')
        
        if not movie_title:
            return jsonify({"status": "error", "message": "movie_title is required"}), 400
            
        alert = alert_manager.add_alert(
            movie_id=movie_id,
            movie_title=movie_title,
            target_price=target_price,
            city=city,
            format_type=format_type,
            email=email
        )
        return jsonify({"status": "success", "alert": alert})
        
    elif request.method == 'DELETE':
        alert_id = request.args.get('alert_id')
        if not alert_id:
            return jsonify({"status": "error", "message": "alert_id is required"}), 400
        alert_manager.delete_alert(alert_id)
        return jsonify({"status": "success", "message": "Alert deleted"})

@app.route('/api/export/shows', methods=['GET'])
def export_shows():
    city = request.args.get('city', 'Mumbai')
    search = request.args.get('search', '')
    csv_data = export_shows_to_csv(city=city, search_query=search)
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename=movie_shows_{city.lower().replace(' ', '_')}.csv"}
    )

@app.route('/api/export/comparison', methods=['GET'])
def export_comparison():
    movie_id = request.args.get('movie_id')
    city = request.args.get('city', 'Mumbai')
    csv_data = export_comparison_to_csv(movie_id, city=city)
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename=price_comparison_{movie_id}_{city.lower()}.csv"}
    )

def open_browser():
    """Automatically open default web browser to the app"""
    webbrowser.open_new("http://127.0.0.1:5000")

if __name__ == '__main__':
    print("=================================================================")
    print("  [CinePlus] Movie Ticket Price & Show Finder Automation         ")
    print("=================================================================")
    print("  Starting server at: http://127.0.0.1:5000")
    print("  Opening browser automatically...")
    print("=================================================================")
    
    threading.Timer(1.2, open_browser).start()
    app.run(host='127.0.0.1', port=5000, debug=False)

