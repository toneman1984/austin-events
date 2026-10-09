import requests
import json
import os
from datetime import datetime, timedelta
from config import YELP_API_KEY, AUSTIN_LAT, AUSTIN_LNG, CACHE_DIR, CACHE_DURATION_SECONDS


def get_cache_path():
    return os.path.join(CACHE_DIR, 'yelp.json')


def is_cache_valid():
    cache_path = get_cache_path()
    if not os.path.exists(cache_path):
        return False
    mtime = os.path.getmtime(cache_path)
    return (datetime.now().timestamp() - mtime) < CACHE_DURATION_SECONDS


def load_from_cache():
    with open(get_cache_path(), 'r', encoding='utf-8') as f:
        return json.load(f)


def save_to_cache(data):
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(get_cache_path(), 'w', encoding='utf-8') as f:
        json.dump(data, f)


def fetch_new_restaurants():
    """Fetch recently opened restaurants from Yelp API."""
    if is_cache_valid():
        return load_from_cache()

    if not YELP_API_KEY:
        print("Yelp: No API key set")
        return get_demo_restaurants()

    try:
        print("Yelp: Fetching new restaurants...")
        headers = {'Authorization': f'Bearer {YELP_API_KEY}'}

        params = {
            'latitude': AUSTIN_LAT,
            'longitude': AUSTIN_LNG,
            'radius': 16000,  # ~10 miles in meters
            'categories': 'restaurants,bars,coffee',
            'sort_by': 'rating',
            'limit': 15,
        }

        response = requests.get(
            'https://api.yelp.com/v3/businesses/search',
            headers=headers,
            params=params,
            timeout=10
        )

        if response.status_code != 200:
            print(f"Yelp API error: Status {response.status_code} - {response.text[:200]}")
            return get_demo_restaurants()

        data = response.json()
        restaurants = []
        businesses = data.get('businesses', [])
        print(f"Yelp: Found {len(businesses)} businesses")

        for biz in businesses:
            coords = biz.get('coordinates', {})
            location = biz.get('location', {})

            # Create a pseudo-event for new restaurant opening
            restaurants.append({
                'id': f"yelp_{biz.get('id')}",
                'title': biz.get('name', 'Unknown'),
                'description': f"New {', '.join(c.get('title', '') for c in biz.get('categories', []))} - {biz.get('rating', 'N/A')} stars",
                'date': datetime.now().strftime('%Y-%m-%dT12:00:00'),  # Use today as placeholder
                'venue': biz.get('name', ''),
                'address': ', '.join(location.get('display_address', [])),
                'lat': coords.get('latitude'),
                'lng': coords.get('longitude'),
                'url': biz.get('url', ''),
                'category': 'Food',
                'source': 'Yelp',
            })

        if not restaurants:
            print("Yelp: No restaurants returned")
            return []

        save_to_cache(restaurants)
        return restaurants

    except Exception as e:
        print(f"Yelp API error: {e}")
        return []


def get_demo_restaurants():
    """Return demo restaurants when API is unavailable."""
    return [
        {
            'id': 'yelp_demo_1',
            'title': 'NEW: Loro Asian Smokehouse',
            'description': 'New Asian Fusion, BBQ - 4.5 stars. Thai-Texas fusion from acclaimed chefs.',
            'date': datetime.now().strftime('%Y-%m-%dT12:00:00'),
            'venue': 'Loro',
            'address': '2115 S Lamar Blvd, Austin, TX',
            'lat': 30.2506,
            'lng': -97.7697,
            'url': 'https://loroaustin.com',
            'category': 'Food',
            'source': 'Demo',
        },
        {
            'id': 'yelp_demo_2',
            'title': 'NEW: Hestia',
            'description': 'New American, Fine Dining - 4.5 stars. Live-fire cooking in downtown Austin.',
            'date': datetime.now().strftime('%Y-%m-%dT12:00:00'),
            'venue': 'Hestia',
            'address': '607 W 3rd St, Austin, TX',
            'lat': 30.2656,
            'lng': -97.7497,
            'url': '',
            'category': 'Food',
            'source': 'Demo',
        },
        {
            'id': 'yelp_demo_3',
            'title': 'NEW: Little Ola\'s Biscuits',
            'description': 'New Breakfast, Southern - 4.5 stars. Scratch-made biscuits and breakfast tacos.',
            'date': datetime.now().strftime('%Y-%m-%dT12:00:00'),
            'venue': 'Little Ola\'s Biscuits',
            'address': '1900 Simond Ave, Austin, TX',
            'lat': 30.2777,
            'lng': -97.7168,
            'url': '',
            'category': 'Food',
            'source': 'Demo',
        },
    ]
