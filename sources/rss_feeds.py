import feedparser
import requests
from bs4 import BeautifulSoup
import json
import os
import re
from datetime import datetime, timedelta
from dateutil import parser as date_parser
from config import CACHE_DIR, CACHE_DURATION_SECONDS, EVENT_WINDOW_DAYS, AUSTIN_LAT, AUSTIN_LNG


# RSS Feed URLs
FEEDS = {
    'do512': 'https://do512.com/events/feed',
    'chronicle': 'https://www.austinchronicle.com/gyrobase/rss/events.xml',
}


def get_cache_path(source):
    return os.path.join(CACHE_DIR, f'{source}.json')


def is_cache_valid(source):
    cache_path = get_cache_path(source)
    if not os.path.exists(cache_path):
        return False
    mtime = os.path.getmtime(cache_path)
    return (datetime.now().timestamp() - mtime) < CACHE_DURATION_SECONDS


def load_from_cache(source):
    with open(get_cache_path(source), 'r', encoding='utf-8') as f:
        return json.load(f)


def save_to_cache(source, data):
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(get_cache_path(source), 'w', encoding='utf-8') as f:
        json.dump(data, f)


def parse_date(date_str):
    """Parse various date formats from RSS feeds."""
    if not date_str:
        return None
    try:
        return date_parser.parse(date_str)
    except (ValueError, TypeError):
        return None


def clean_html(html):
    """Remove HTML tags from text."""
    clean = re.sub(r'<[^>]+>', '', html)
    return clean.strip()[:200]


def categorize_from_content(title, description):
    """Categorize event based on content."""
    content = (title + ' ' + description).lower()

    if any(word in content for word in ['concert', 'music', 'live', 'band', 'dj', 'rave', 'hip-hop', 'jazz', 'rock']):
        return 'Music'
    elif any(word in content for word in ['art', 'gallery', 'exhibit', 'museum', 'painting']):
        return 'Art'
    elif any(word in content for word in ['food', 'restaurant', 'tasting', 'dinner', 'brunch', 'chef']):
        return 'Food'
    elif any(word in content for word in ['market', 'fair', 'bazaar', 'vintage', 'craft']):
        return 'Markets'
    elif any(word in content for word in ['club', 'party', 'night', 'dance', 'rave']):
        return 'Nightlife'
    return 'Other'


def scrape_do512_events():
    """Scrape events directly from Do512 website."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get('https://do512.com/events', headers=headers, timeout=10)

        if response.status_code != 200:
            print(f"Do512 scrape error: Status {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        events = []

        # Find event cards on the page
        event_cards = soup.select('.ds-listing, .event-card, [data-event-id], .ds-event-card')

        for card in event_cards[:30]:
            try:
                title_el = card.select_one('h2, h3, .ds-listing-event-title, .event-title, a[href*="/events/"]')
                title = title_el.get_text(strip=True) if title_el else None

                if not title:
                    continue

                link_el = card.select_one('a[href*="/events/"]')
                url = 'https://do512.com' + link_el['href'] if link_el and link_el.get('href', '').startswith('/') else (link_el['href'] if link_el else '')

                venue_el = card.select_one('.ds-venue-name, .venue, .location')
                venue = venue_el.get_text(strip=True) if venue_el else 'See event details'

                date_el = card.select_one('.ds-listing-event-date, .date, time')
                date_str = date_el.get_text(strip=True) if date_el else ''
                event_date = parse_date(date_str) if date_str else datetime.now()

                events.append({
                    'id': f"do512_{hash(url) % 100000}",
                    'title': title,
                    'description': '',
                    'date': event_date.strftime('%Y-%m-%dT%H:%M:%S') if event_date else datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                    'venue': venue,
                    'address': 'Austin, TX',
                    'lat': AUSTIN_LAT + (hash(title) % 100) / 1000 - 0.05,
                    'lng': AUSTIN_LNG + (hash(url) % 100) / 1000 - 0.05,
                    'url': url,
                    'category': categorize_from_content(title, ''),
                    'source': 'Do512',
                })
            except Exception as e:
                continue

        print(f"Do512 scrape: Found {len(events)} events")
        return events

    except Exception as e:
        print(f"Do512 scrape error: {e}")
        return []


def fetch_do512_events():
    """Fetch events from Do512 RSS feed or scrape website."""
    if is_cache_valid('do512'):
        return load_from_cache('do512')

    events = []

    # Try RSS feed first
    try:
        feed = feedparser.parse(FEEDS['do512'])
        cutoff_date = datetime.now() + timedelta(days=EVENT_WINDOW_DAYS)

        for entry in feed.entries[:30]:
            pub_date = parse_date(entry.get('published', ''))

            if pub_date and pub_date > cutoff_date:
                continue

            events.append({
                'id': f"do512_{hash(entry.get('link', '')) % 100000}",
                'title': entry.get('title', 'Untitled Event'),
                'description': clean_html(entry.get('summary', entry.get('description', ''))),
                'date': pub_date.strftime('%Y-%m-%dT%H:%M:%S') if pub_date else datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                'venue': 'See event details',
                'address': 'Austin, TX',
                'lat': AUSTIN_LAT + (hash(entry.get('title', '')) % 100) / 1000 - 0.05,
                'lng': AUSTIN_LNG + (hash(entry.get('link', '')) % 100) / 1000 - 0.05,
                'url': entry.get('link', ''),
                'category': categorize_from_content(entry.get('title', ''), entry.get('summary', '')),
                'source': 'Do512',
            })

        if events:
            print(f"Do512 RSS: Found {len(events)} events")

    except Exception as e:
        print(f"Do512 RSS error: {e}")

    # If RSS failed, try scraping
    if not events:
        print("Do512: RSS empty, trying web scrape...")
        events = scrape_do512_events()

    if not events:
        print("Do512: All methods failed, no events")
        return []

    save_to_cache('do512', events)
    return events


def scrape_chronicle_events():
    """Scrape events directly from Austin Chronicle website."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get('https://www.austinchronicle.com/events/', headers=headers, timeout=10)

        if response.status_code != 200:
            print(f"Chronicle scrape error: Status {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        events = []

        # Find event listings
        event_items = soup.select('.event-listing, .listing, article, .event-item, .cal-listing')

        for item in event_items[:30]:
            try:
                # Try to find title
                title_el = item.select_one('h2 a, h3 a, .title a, .event-title a, a.title')
                if not title_el:
                    title_el = item.select_one('h2, h3, .title, .event-title')

                title = title_el.get_text(strip=True) if title_el else None
                if not title or len(title) < 3:
                    continue

                # Get URL
                link_el = item.select_one('a[href*="/events/"]')
                url = link_el['href'] if link_el else ''
                if url and not url.startswith('http'):
                    url = 'https://www.austinchronicle.com' + url

                # Get venue
                venue_el = item.select_one('.venue, .location, .event-venue')
                venue = venue_el.get_text(strip=True) if venue_el else 'See event details'

                # Get date
                date_el = item.select_one('.date, time, .event-date, .cal-date')
                date_str = date_el.get_text(strip=True) if date_el else ''
                event_date = parse_date(date_str) if date_str else datetime.now()

                # Get description
                desc_el = item.select_one('.description, .summary, p')
                description = clean_html(desc_el.get_text()) if desc_el else ''

                events.append({
                    'id': f"chron_{hash(url or title) % 100000}",
                    'title': title,
                    'description': description[:200],
                    'date': event_date.strftime('%Y-%m-%dT%H:%M:%S') if event_date else datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                    'venue': venue,
                    'address': 'Austin, TX',
                    'lat': AUSTIN_LAT + (hash(title) % 100) / 1000 - 0.05,
                    'lng': AUSTIN_LNG + (hash(url or title) % 100) / 1000 - 0.05,
                    'url': url,
                    'category': categorize_from_content(title, description),
                    'source': 'Austin Chronicle',
                })
            except Exception:
                continue

        print(f"Chronicle scrape: Found {len(events)} events")
        return events

    except Exception as e:
        print(f"Chronicle scrape error: {e}")
        return []


def fetch_chronicle_events():
    """Fetch events from Austin Chronicle RSS feed or scrape website."""
    if is_cache_valid('chronicle'):
        return load_from_cache('chronicle')

    events = []

    # Try RSS feed first
    try:
        feed = feedparser.parse(FEEDS['chronicle'])
        cutoff_date = datetime.now() + timedelta(days=EVENT_WINDOW_DAYS)

        for entry in feed.entries[:30]:
            pub_date = parse_date(entry.get('published', ''))

            if pub_date and pub_date > cutoff_date:
                continue

            events.append({
                'id': f"chron_{hash(entry.get('link', '')) % 100000}",
                'title': entry.get('title', 'Untitled Event'),
                'description': clean_html(entry.get('summary', entry.get('description', ''))),
                'date': pub_date.strftime('%Y-%m-%dT%H:%M:%S') if pub_date else datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                'venue': 'See event details',
                'address': 'Austin, TX',
                'lat': AUSTIN_LAT + (hash(entry.get('title', '')) % 100) / 1000 - 0.05,
                'lng': AUSTIN_LNG + (hash(entry.get('link', '')) % 100) / 1000 - 0.05,
                'url': entry.get('link', ''),
                'category': categorize_from_content(entry.get('title', ''), entry.get('summary', '')),
                'source': 'Austin Chronicle',
            })

        if events:
            print(f"Chronicle RSS: Found {len(events)} events")

    except Exception as e:
        print(f"Chronicle RSS error: {e}")

    # If RSS failed, try scraping
    if not events:
        print("Chronicle: RSS empty, trying web scrape...")
        events = scrape_chronicle_events()

    if not events:
        print("Chronicle: All methods failed, no events")
        return []

    save_to_cache('chronicle', events)
    return events


def get_demo_do512_events():
    """Demo events for Do512."""
    base_date = datetime.now()
    return [
        {
            'id': 'do512_demo_1',
            'title': 'Barton Springs Sunset Sessions',
            'description': 'Weekly acoustic performances at Barton Springs featuring local singer-songwriters.',
            'date': (base_date + timedelta(days=2)).strftime('%Y-%m-%dT18:00:00'),
            'venue': 'Barton Springs Pool',
            'address': '2201 Barton Springs Rd, Austin, TX',
            'lat': 30.2640,
            'lng': -97.7711,
            'url': 'https://do512.com',
            'category': 'Music',
            'source': 'Demo',
        },
        {
            'id': 'do512_demo_2',
            'title': 'East Side Studio Tour',
            'description': 'Open studios on the east side featuring painters, sculptors, and mixed media artists.',
            'date': (base_date + timedelta(days=6)).strftime('%Y-%m-%dT12:00:00'),
            'venue': 'East Austin Studios',
            'address': 'East 6th Street, Austin, TX',
            'lat': 30.2629,
            'lng': -97.7234,
            'url': 'https://do512.com',
            'category': 'Art',
            'source': 'Demo',
        },
    ]


def get_demo_chronicle_events():
    """Demo events for Austin Chronicle."""
    base_date = datetime.now()
    return [
        {
            'id': 'chron_demo_1',
            'title': 'Austin City Limits Taping',
            'description': 'Live taping of the legendary Austin City Limits TV show. Free tickets via lottery.',
            'date': (base_date + timedelta(days=7)).strftime('%Y-%m-%dT20:00:00'),
            'venue': 'ACL Live at The Moody Theater',
            'address': '310 Willie Nelson Blvd, Austin, TX',
            'lat': 30.2649,
            'lng': -97.7495,
            'url': 'https://acltv.com',
            'category': 'Music',
            'source': 'Demo',
        },
        {
            'id': 'chron_demo_2',
            'title': 'Hope Outdoor Gallery Farewell',
            'description': 'Final exhibition at Austin\'s beloved graffiti park before relocation.',
            'date': (base_date + timedelta(days=9)).strftime('%Y-%m-%dT10:00:00'),
            'venue': 'HOPE Outdoor Gallery',
            'address': '1101 Baylor St, Austin, TX',
            'lat': 30.2825,
            'lng': -97.7536,
            'url': '',
            'category': 'Art',
            'source': 'Demo',
        },
    ]


def fetch_all_rss_events():
    """Fetch events from all RSS sources."""
    events = []
    events.extend(fetch_do512_events())
    events.extend(fetch_chronicle_events())
    return events
