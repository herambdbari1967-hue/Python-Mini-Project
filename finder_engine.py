"""
finder_engine.py
Core data engine and scraper for Movie Ticket Price & Show Finder Automation.
Provides movie listings, live theatre shows, price comparison calculations, and booking URL generation.
"""

import json
import re
from datetime import datetime, timedelta

# Rich catalog of movies with showtimes, theatres, formats, and pricing across major Indian & Global cities
CITIES = [
    "Mumbai", "Delhi NCR", "Bengaluru", "Hyderabad", 
    "Pune", "Chennai", "Kolkata", "Ahmedabad"
]

THEATRES = {
    "Mumbai": [
        {"id": "t1", "name": "PVR ICON: Phoenix Palladium, Lower Parel", "chain": "PVR INOX", "rating": 4.7},
        {"id": "t2", "name": "INOX: Megaplex, Inorbit Mall, Malad", "chain": "PVR INOX", "rating": 4.6},
        {"id": "t3", "name": "Cinépolis: Viviana Mall, Thane", "chain": "Cinépolis", "rating": 4.5},
        {"id": "t4", "name": "MovieMax: Sion Circle", "chain": "MovieMax", "rating": 4.2},
        {"id": "t5", "name": "Miraj Cinemas: Kandivali", "chain": "Miraj", "rating": 4.1}
    ],
    "Delhi NCR": [
        {"id": "t6", "name": "PVR Director's Cut: Ambience Mall, Vasant Kunj", "chain": "PVR INOX", "rating": 4.9},
        {"id": "t7", "name": "INOX: Nehru Place", "chain": "PVR INOX", "rating": 4.5},
        {"id": "t8", "name": "Cinépolis: DLF Place, Saket", "chain": "Cinépolis", "rating": 4.6},
        {"id": "t9", "name": "MovieMax: Pacific Mall, NSP", "chain": "MovieMax", "rating": 4.3}
    ],
    "Bengaluru": [
        {"id": "t10", "name": "PVR Superplex: Vega City Mall, Bannerghatta", "chain": "PVR INOX", "rating": 4.8},
        {"id": "t11", "name": "Cinépolis: Forum Shantiniketan, Whitefield", "chain": "Cinépolis", "rating": 4.6},
        {"id": "t12", "name": "INOX: Garuda Mall, Magrath Road", "chain": "PVR INOX", "rating": 4.4},
        {"id": "t13", "name": "Miraj Cinemas: TNS Mall", "chain": "Miraj", "rating": 4.2}
    ],
    "Hyderabad": [
        {"id": "t14", "name": "Prasads Multiplex: Necklace Road (Large Screen)", "chain": "Independent", "rating": 4.9},
        {"id": "t15", "name": "PVR: Inorbit Mall, Hitec City", "chain": "PVR INOX", "rating": 4.7},
        {"id": "t16", "name": "Cinépolis: DSL Virtue Mall, Uppal", "chain": "Cinépolis", "rating": 4.5},
        {"id": "t17", "name": "AMB Cinemas: Gachibowli", "chain": "AMB", "rating": 4.8}
    ],
    "Pune": [
        {"id": "t18", "name": "PVR: Phoenix Marketcity, Viman Nagar", "chain": "PVR INOX", "rating": 4.7},
        {"id": "t19", "name": "Cinépolis: Seasons Mall, Magarpatta", "chain": "Cinépolis", "rating": 4.6},
        {"id": "t20", "name": "INOX: Bund Garden", "chain": "PVR INOX", "rating": 4.3}
    ],
    "Chennai": [
        {"id": "t21", "name": "SPI Cinemas (PVR): Sathyam, Royapettah", "chain": "PVR INOX", "rating": 4.9},
        {"id": "t22", "name": "PVR: VR Chennai, Anna Nagar", "chain": "PVR INOX", "rating": 4.7},
        {"id": "t23", "name": "INOX: Phoenix Market City, Velachery", "chain": "PVR INOX", "rating": 4.6}
    ],
    "Kolkata": [
        {"id": "t24", "name": "PVR: Mani Square, EM Bypass", "chain": "PVR INOX", "rating": 4.6},
        {"id": "t25", "name": "INOX: Quest Mall, Park Circus", "chain": "PVR INOX", "rating": 4.7},
        {"id": "t26", "name": "Cinépolis: Acropolis Mall", "chain": "Cinépolis", "rating": 4.5}
    ],
    "Ahmedabad": [
        {"id": "t27", "name": "PVR: Acropolis Mall, Thaltej", "chain": "PVR INOX", "rating": 4.6},
        {"id": "t28", "name": "Cinépolis: Alpha One Mall, Vastrapur", "chain": "Cinépolis", "rating": 4.5},
        {"id": "t29", "name": "Miraj Cinemas: Vitthal Mall", "chain": "Miraj", "rating": 4.2}
    ]
}

MOVIES_DATABASE = [
    {
        "id": "mov-1",
        "title": "Dune: Part Two",
        "genre": "Sci-Fi / Adventure",
        "rating": 8.9,
        "duration": "2h 46m",
        "languages": ["English", "Hindi"],
        "formats": ["IMAX 3D", "4DX", "2D", "Dolby Atmos"],
        "poster": "https://images.unsplash.com/photo-1534447677768-be436bb09401?w=800&auto=format&fit=crop&q=80",
        "badge": "Blockbuster",
        "discount_tag": "Up to 30% off",
        "description": "Paul Atreides unites with Chani and the Fremen while seeking revenge against the conspirators who destroyed his family.",
        "shows_template": [
            {"time": "10:15 AM", "format": "IMAX 3D", "silver": 280, "gold": 420, "recliner": 650, "seats_left": 42},
            {"time": "01:45 PM", "format": "2D", "silver": 160, "gold": 240, "recliner": 380, "seats_left": 88},
            {"time": "05:30 PM", "format": "4DX", "silver": 350, "gold": 500, "recliner": 750, "seats_left": 15},
            {"time": "09:15 PM", "format": "IMAX 3D", "silver": 320, "gold": 480, "recliner": 700, "seats_left": 6}
        ]
    },
    {
        "id": "mov-2",
        "title": "Oppenheimer",
        "genre": "Biography / Drama / History",
        "rating": 8.9,
        "duration": "3h 00m",
        "languages": ["English", "Hindi"],
        "formats": ["IMAX 3D", "2D", "Dolby Atmos"],
        "poster": "https://images.unsplash.com/photo-1440404653325-ab127d49abc1?w=800&auto=format&fit=crop&q=80",
        "badge": "Oscar Winner",
        "discount_tag": "Special ₹150 morning show",
        "description": "The story of American scientist J. Robert Oppenheimer and his role in the development of the atomic bomb.",
        "shows_template": [
            {"time": "09:30 AM", "format": "2D", "silver": 140, "gold": 200, "recliner": 320, "seats_left": 65},
            {"time": "01:15 PM", "format": "IMAX 3D", "silver": 290, "gold": 440, "recliner": 680, "seats_left": 28},
            {"time": "06:00 PM", "format": "Dolby Atmos", "silver": 220, "gold": 320, "recliner": 500, "seats_left": 12},
            {"time": "10:00 PM", "format": "2D", "silver": 180, "gold": 260, "recliner": 420, "seats_left": 50}
        ]
    },
    {
        "id": "mov-3",
        "title": "Deadpool & Wolverine",
        "genre": "Action / Comedy / Sci-Fi",
        "rating": 8.1,
        "duration": "2h 08m",
        "languages": ["English", "Hindi", "Telugu", "Tamil"],
        "formats": ["3D", "4DX", "IMAX 3D", "2D"],
        "poster": "https://images.unsplash.com/photo-1563089145-599997674d42?w=800&auto=format&fit=crop&q=80",
        "badge": "New Release",
        "discount_tag": "Fast Filling",
        "description": "Wolverine is recovering from his injuries when he crosses paths with the loudmouth Deadpool to defeat a common enemy.",
        "shows_template": [
            {"time": "11:00 AM", "format": "3D", "silver": 190, "gold": 280, "recliner": 450, "seats_left": 18},
            {"time": "02:30 PM", "format": "4DX", "silver": 380, "gold": 520, "recliner": 800, "seats_left": 8},
            {"time": "07:00 PM", "format": "IMAX 3D", "silver": 340, "gold": 500, "recliner": 750, "seats_left": 4},
            {"time": "10:30 PM", "format": "2D", "silver": 170, "gold": 250, "recliner": 390, "seats_left": 35}
        ]
    },
    {
        "id": "mov-4",
        "title": "Interstellar (10th Anniversary Re-Release)",
        "genre": "Sci-Fi / Adventure / Drama",
        "rating": 8.7,
        "duration": "2h 49m",
        "languages": ["English"],
        "formats": ["IMAX 3D", "Dolby Atmos", "2D"],
        "poster": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800&auto=format&fit=crop&q=80",
        "badge": "Trending",
        "discount_tag": "Exclusive ₹199",
        "description": "When Earth becomes uninhabitable in the future, a farmer and ex-NASA pilot is tasked to pilot a spacecraft to find a new planet.",
        "shows_template": [
            {"time": "10:00 AM", "format": "IMAX 3D", "silver": 300, "gold": 450, "recliner": 690, "seats_left": 9},
            {"time": "03:15 PM", "format": "2D", "silver": 150, "gold": 220, "recliner": 350, "seats_left": 40},
            {"time": "08:00 PM", "format": "IMAX 3D", "silver": 350, "gold": 520, "recliner": 780, "seats_left": 2}
        ]
    },
    {
        "id": "mov-5",
        "title": "Kalki 2898 AD",
        "genre": "Action / Sci-Fi / Mythology",
        "rating": 8.0,
        "duration": "3h 01m",
        "languages": ["Telugu", "Hindi", "Tamil", "English"],
        "formats": ["3D", "IMAX 3D", "2D"],
        "poster": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=800&auto=format&fit=crop&q=80",
        "badge": "Mega Hit",
        "discount_tag": "Flat 25% off",
        "description": "A modern avatar of Hindu god Vishnu descends to earth to protect the world from evil forces in a dystopian future.",
        "shows_template": [
            {"time": "10:30 AM", "format": "2D", "silver": 140, "gold": 210, "recliner": 330, "seats_left": 70},
            {"time": "02:00 PM", "format": "3D", "silver": 210, "gold": 300, "recliner": 480, "seats_left": 25},
            {"time": "06:30 PM", "format": "IMAX 3D", "silver": 310, "gold": 460, "recliner": 700, "seats_left": 14},
            {"time": "09:45 PM", "format": "2D", "silver": 180, "gold": 260, "recliner": 400, "seats_left": 30}
        ]
    },
    {
        "id": "mov-6",
        "title": "Spider-Man: Beyond the Spider-Verse",
        "genre": "Animation / Action / Adventure",
        "rating": 8.8,
        "duration": "2h 20m",
        "languages": ["English", "Hindi", "Tamil"],
        "formats": ["3D", "IMAX 3D", "4DX", "2D"],
        "poster": "https://images.unsplash.com/photo-1635805737707-575885ab0820?w=800&auto=format&fit=crop&q=80",
        "badge": "Popular",
        "discount_tag": "35% off on Matinee",
        "description": "Miles Morales catapults across the Multiverse, where he encounters a team of Spider-People charged with protecting its very existence.",
        "shows_template": [
            {"time": "11:30 AM", "format": "3D", "silver": 180, "gold": 270, "recliner": 420, "seats_left": 50},
            {"time": "03:30 PM", "format": "4DX", "silver": 360, "gold": 510, "recliner": 780, "seats_left": 12},
            {"time": "07:15 PM", "format": "IMAX 3D", "silver": 320, "gold": 480, "recliner": 720, "seats_left": 7}
        ]
    }
]

def generate_booking_url(movie_title, theatre_name, city, show_time, format_type):
    """Generates direct 1-click booking launcher URL for BookMyShow / PVR INOX"""
    clean_movie = re.sub(r'[^a-zA-Z0-9\s]', '', movie_title).lower().replace(' ', '-')
    clean_city = city.lower().replace(' ', '-')
    return f"https://in.bookmyshow.com/explore/movies-{clean_city}?search={clean_movie}"

def get_movie_shows(city="Mumbai", search_query=None, selected_formats=None, max_price=None, theatre_chain=None, sort_by="cheapest"):
    """
    Searches and aggregates all show details across theatres for a specified city and filters.
    Computes best deals, lowest prices, and formats.
    """
    theatres = THEATRES.get(city, THEATRES["Mumbai"])
    results = []
    
    for mov in MOVIES_DATABASE:
        if search_query:
            q = search_query.strip().lower()
            if q not in mov["title"].lower() and q not in mov["genre"].lower():
                continue
                
        # Generate theatre show instances for this city
        theatre_shows = []
        min_price = float('inf')
        max_discount_str = mov["discount_tag"]
        
        for t_idx, theatre in enumerate(theatres):
            if theatre_chain and theatre_chain != "All" and theatre["chain"] != theatre_chain:
                continue
                
            # slight price variance per theatre chain
            price_multiplier = 1.0
            if theatre["chain"] == "PVR INOX":
                price_multiplier = 1.15
            elif theatre["chain"] == "MovieMax" or theatre["chain"] == "Miraj":
                price_multiplier = 0.85
                
            shows_list = []
            for s in mov["shows_template"]:
                fmt = s["format"]
                if selected_formats and len(selected_formats) > 0 and fmt not in selected_formats:
                    continue
                    
                silver_p = int(s["silver"] * price_multiplier)
                gold_p = int(s["gold"] * price_multiplier)
                recliner_p = int(s["recliner"] * price_multiplier)
                
                if max_price and silver_p > max_price:
                    continue
                    
                if silver_p < min_price:
                    min_price = silver_p
                    
                booking_link = generate_booking_url(mov["title"], theatre["name"], city, s["time"], fmt)
                
                shows_list.append({
                    "time": s["time"],
                    "format": fmt,
                    "silver": silver_p,
                    "gold": gold_p,
                    "recliner": recliner_p,
                    "seats_left": s["seats_left"],
                    "booking_url": booking_link
                })
                
            if shows_list:
                theatre_shows.append({
                    "theatre_id": theatre["id"],
                    "theatre_name": theatre["name"],
                    "chain": theatre["chain"],
                    "rating": theatre["rating"],
                    "shows": shows_list
                })
                
        if theatre_shows:
            item = {
                "id": mov["id"],
                "title": mov["title"],
                "genre": mov["genre"],
                "rating": mov["rating"],
                "duration": mov["duration"],
                "languages": mov["languages"],
                "formats": mov["formats"],
                "poster": mov["poster"],
                "badge": mov["badge"],
                "discount_tag": max_discount_str,
                "description": mov["description"],
                "city": city,
                "min_price": min_price if min_price != float('inf') else 150,
                "theatre_count": len(theatre_shows),
                "theatre_shows": theatre_shows
            }
            results.append(item)
            
    # Sorting
    if sort_by == "cheapest":
        results.sort(key=lambda x: x["min_price"])
    elif sort_by == "highest_rated":
        results.sort(key=lambda x: x["rating"], reverse=True)
    elif sort_by == "theatre_count":
        results.sort(key=lambda x: x["theatre_count"], reverse=True)
        
    return results

def get_price_comparison(movie_id, city="Mumbai"):
    """
    Generates a detailed comparison matrix across all theatres and seat tiers for a specific movie.
    """
    shows = get_movie_shows(city=city)
    target = None
    for m in shows:
        if m["id"] == movie_id:
            target = m
            break
            
    if not target:
        return None
        
    rows = []
    for t in target["theatre_shows"]:
        for s in t["shows"]:
            rows.append({
                "theatre": t["theatre_name"],
                "chain": t["chain"],
                "theatre_rating": t["rating"],
                "time": s["time"],
                "format": s["format"],
                "silver_price": s["silver"],
                "gold_price": s["gold"],
                "recliner_price": s["recliner"],
                "seats_left": s["seats_left"],
                "booking_url": s["booking_url"]
            })
            
    # Sort by cheapest silver price
    rows.sort(key=lambda x: x["silver_price"])
    
    cheapest = rows[0] if rows else None
    vip_best = sorted(rows, key=lambda x: x["recliner_price"])[0] if rows else None
    
    return {
        "movie_title": target["title"],
        "city": city,
        "cheapest_option": cheapest,
        "vip_best_option": vip_best,
        "total_shows": len(rows),
        "comparison_table": rows
    }
