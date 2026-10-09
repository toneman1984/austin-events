from flask import Flask, render_template, jsonify, request
from datetime import datetime
import os
import sys

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from sources.eventbrite import fetch_eventbrite_events
from sources.yelp import fetch_new_restaurants
from sources.rss_feeds import fetch_all_rss_events
from sources.nightlife import fetch_all_nightlife_events
from config import AUSTIN_LAT, AUSTIN_LNG, EVENTBRITE_API_KEY, YELP_API_KEY

app = Flask(__name__)


import re

def normalize_title(title):
    """Normalize title for comparison."""
    # Lowercase and remove special characters
    title = title.lower()
    title = re.sub(r'[^\w\s]', '', title)
    # Remove common words
    title = re.sub(r'\b(the|a|an|at|in|on|with|and|or|presents?|live|show|night)\b', '', title)
    # Remove extra whitespace
    title = ' '.join(title.split())
    return title[:40]


def aggregate_events():
    """Fetch and combine events from all sources."""
    all_events = []

    # Fetch from all sources
    all_events.extend(fetch_eventbrite_events())
    all_events.extend(fetch_new_restaurants())
    all_events.extend(fetch_all_rss_events())
    all_events.extend(fetch_all_nightlife_events())

    # Deduplicate by multiple criteria
    seen = set()
    unique_events = []

    for event in all_events:
        # Create multiple keys to catch duplicates
        title_norm = normalize_title(event['title'])
        date_short = event['date'][:10] if event['date'] else ''
        venue_norm = event.get('venue', '').lower()[:20]

        # Key 1: Normalized title
        key1 = title_norm

        # Key 2: Title + Date (catches same event on different sources)
        key2 = f"{title_norm}_{date_short}"

        # Key 3: Venue + Date (catches same venue/date with different title formats)
        key3 = f"{venue_norm}_{date_short}" if venue_norm and date_short else None

        # Check if any key exists
        is_duplicate = key1 in seen or key2 in seen or (key3 and key3 in seen)

        if not is_duplicate:
            seen.add(key1)
            seen.add(key2)
            if key3:
                seen.add(key3)
            unique_events.append(event)

    # Sort by date
    def parse_date(event):
        try:
            return datetime.fromisoformat(event['date'].replace('Z', '+00:00'))
        except (ValueError, TypeError):
            return datetime.now()

    unique_events.sort(key=parse_date)

    return unique_events


@app.route('/')
def index():
    """Main page with event list and map."""
    events = aggregate_events()
    categories = ['All', 'Music', 'Art', 'Food', 'Markets', 'Nightlife', 'Other']
    return render_template(
        'index.html',
        events=events,
        categories=categories,
        austin_lat=AUSTIN_LAT,
        austin_lng=AUSTIN_LNG
    )


@app.route('/api/events')
def api_events():
    """JSON API endpoint for events."""
    events = aggregate_events()
    category = request.args.get('category', 'All')

    if category != 'All':
        events = [e for e in events if e['category'] == category]

    return jsonify(events)


@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})


if __name__ == '__main__':
    # Ensure cache directory exists
    os.makedirs('cache', exist_ok=True)

    print("=" * 50)
    print("Austin Events Web App")
    print("=" * 50)
    print(f"Open http://localhost:5000 in your browser")
    print()
    print("API Keys Status:")
    print(f"  EVENTBRITE_API_KEY: {'Set' if EVENTBRITE_API_KEY else 'Not set (using demo data)'}")
    print(f"  YELP_API_KEY: {'Set' if YELP_API_KEY else 'Not set (using demo data)'}")
    print("=" * 50)

    app.run(debug=True, host='0.0.0.0', port=5000)
