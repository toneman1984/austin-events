import requests
import json
import os
from datetime import datetime, timedelta
from config import EVENTBRITE_API_KEY, AUSTIN_LAT, AUSTIN_LNG, CACHE_DIR, CACHE_DURATION_SECONDS, EVENT_WINDOW_DAYS


def get_cache_path():
    return os.path.join(CACHE_DIR, 'eventbrite.json')


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


def fetch_eventbrite_events():
    """Eventbrite API deprecated - returns empty list.

    Note: Eventbrite deprecated their public search API in 2019.
    Public event search now requires their Destination API (approval needed).
    """
    print("Eventbrite: Public search API deprecated - skipping")
    return []


def categorize_event(title):
    """Categorize event based on title keywords."""
    title_lower = title.lower()
    if any(word in title_lower for word in ['concert', 'music', 'live', 'band', 'dj', 'rave', 'festival']):
        return 'Music'
    elif any(word in title_lower for word in ['art', 'gallery', 'exhibit', 'painting', 'sculpture']):
        return 'Art'
    elif any(word in title_lower for word in ['food', 'restaurant', 'tasting', 'brunch', 'dinner', 'chef']):
        return 'Food'
    elif any(word in title_lower for word in ['market', 'fair', 'bazaar', 'craft', 'vintage', 'flea', 'farmers', 'artisan', 'pop-up', 'popup', 'swap', 'thrift', 'handmade', 'vendor']):
        return 'Markets'
    elif any(word in title_lower for word in ['club', 'party', 'night', 'dance']):
        return 'Nightlife'
    return 'Other'


def get_demo_events():
    """Return demo events when API is unavailable."""
    base_date = datetime.now()
    return [
        {
            'id': 'demo_1',
            'title': 'Live Music at Mohawk',
            'description': 'Local bands showcase featuring Austin\'s best indie rock acts.',
            'date': (base_date + timedelta(days=1)).strftime('%Y-%m-%dT20:00:00'),
            'venue': 'Mohawk Austin',
            'address': '912 Red River St, Austin, TX',
            'lat': 30.2685,
            'lng': -97.7365,
            'url': 'https://mohawkaustin.com',
            'category': 'Music',
            'source': 'Demo',
        },
        {
            'id': 'demo_2',
            'title': 'Contemporary Art Exhibition',
            'description': 'New works by emerging Texas artists exploring identity and place.',
            'date': (base_date + timedelta(days=2)).strftime('%Y-%m-%dT10:00:00'),
            'venue': 'Blanton Museum of Art',
            'address': '200 E Martin Luther King Jr Blvd, Austin, TX',
            'lat': 30.2809,
            'lng': -97.7377,
            'url': 'https://blantonmuseum.org',
            'category': 'Art',
            'source': 'Demo',
        },
        {
            'id': 'demo_3',
            'title': 'East Austin Food Truck Festival',
            'description': 'Over 30 food trucks serving cuisines from around the world.',
            'date': (base_date + timedelta(days=3)).strftime('%Y-%m-%dT11:00:00'),
            'venue': 'Zilker Park',
            'address': '2100 Barton Springs Rd, Austin, TX',
            'lat': 30.2669,
            'lng': -97.7729,
            'url': '',
            'category': 'Food',
            'source': 'Demo',
        },
        {
            'id': 'demo_4',
            'title': 'SoCo Vintage Market',
            'description': 'Vintage clothing, antiques, and handmade crafts from local vendors.',
            'date': (base_date + timedelta(days=4)).strftime('%Y-%m-%dT09:00:00'),
            'venue': 'South Congress Ave',
            'address': 'South Congress Ave, Austin, TX',
            'lat': 30.2484,
            'lng': -97.7501,
            'url': '',
            'category': 'Markets',
            'source': 'Demo',
        },
        {
            'id': 'demo_5',
            'title': 'Underground Rave: Neon Dreams',
            'description': 'Electronic music night featuring house and techno DJs.',
            'date': (base_date + timedelta(days=5)).strftime('%Y-%m-%dT22:00:00'),
            'venue': 'The Concourse Project',
            'address': '8509 Burleson Rd, Austin, TX',
            'lat': 30.1945,
            'lng': -97.7125,
            'url': '',
            'category': 'Nightlife',
            'source': 'Demo',
        },
    ]
