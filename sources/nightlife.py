import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime, timedelta
from dateutil import parser as date_parser
from config import CACHE_DIR, CACHE_DURATION_SECONDS, AUSTIN_LAT, AUSTIN_LNG


# Austin electronic music venues
VENUES = {
    'kingdom': {
        'name': 'Kingdom',
        'url': 'https://do512.com/venues/kingdom-austin',
        'lat': 30.2672,
        'lng': -97.7366,
        'address': '505 E 7th St, Austin, TX',
    },
    'concourse': {
        'name': 'The Concourse Project',
        'url': 'https://do512.com/venues/the-concourse-project',
        'lat': 30.1945,
        'lng': -97.7125,
        'address': '8509 Burleson Rd, Austin, TX',
    },
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
    if not date_str:
        return None
    try:
        return date_parser.parse(date_str, fuzzy=True)
    except (ValueError, TypeError):
        return None


def scrape_resident_advisor():
    """Scrape events from Resident Advisor for Austin."""
    if is_cache_valid('ra'):
        return load_from_cache('ra')

    events = []
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

        # RA Austin events page
        response = requests.get(
            'https://ra.co/events/us/texas/austin',
            headers=headers,
            timeout=15
        )

        if response.status_code == 403:
            print("Resident Advisor: Access blocked (403) - they block scrapers")
            return []

        if response.status_code != 200:
            print(f"Resident Advisor error: Status {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find event cards
        event_cards = soup.select('[data-testid="event-listing"], .event-listing, article, [class*="event"]')

        for card in event_cards[:30]:
            try:
                # Title
                title_el = card.select_one('h3, h4, [class*="title"], a[href*="/events/"]')
                title = title_el.get_text(strip=True) if title_el else None
                if not title or len(title) < 3:
                    continue

                # URL
                link_el = card.select_one('a[href*="/events/"]')
                url = ''
                if link_el:
                    href = link_el.get('href', '')
                    url = 'https://ra.co' + href if href.startswith('/') else href

                # Venue
                venue_el = card.select_one('[class*="venue"], [class*="location"]')
                venue = venue_el.get_text(strip=True) if venue_el else 'See event details'

                # Date
                date_el = card.select_one('time, [class*="date"]')
                date_str = date_el.get('datetime') or date_el.get_text(strip=True) if date_el else ''
                event_date = parse_date(date_str)

                events.append({
                    'id': f"ra_{hash(url or title) % 100000}",
                    'title': title,
                    'description': 'Electronic music event',
                    'date': event_date.strftime('%Y-%m-%dT%H:%M:%S') if event_date else datetime.now().strftime('%Y-%m-%dT22:00:00'),
                    'venue': venue,
                    'address': 'Austin, TX',
                    'lat': AUSTIN_LAT + (hash(title) % 50) / 1000 - 0.025,
                    'lng': AUSTIN_LNG + (hash(url or title) % 50) / 1000 - 0.025,
                    'url': url,
                    'category': 'Nightlife',
                    'source': 'Resident Advisor',
                })
            except Exception:
                continue

        print(f"Resident Advisor: Found {len(events)} events")

        if events:
            save_to_cache('ra', events)
        return events

    except Exception as e:
        print(f"Resident Advisor error: {e}")
        return []


def scrape_venue(venue_key):
    """Scrape events from a specific venue via Do512 venue pages."""
    venue = VENUES.get(venue_key)
    if not venue:
        return []

    cache_key = f"venue_{venue_key}"
    if is_cache_valid(cache_key):
        return load_from_cache(cache_key)

    events = []
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }

        response = requests.get(venue['url'], headers=headers, timeout=10)

        if response.status_code != 200:
            print(f"{venue['name']} error: Status {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')

        # Do512 specific selectors first, then generic ones
        event_cards = soup.select(
            '.ds-listing, .ds-event-card, .ds-listing-event-title, '
            '.event, .event-card, .event-item, article, '
            '[class*="event"], .show, .listing, [data-event], '
            'a[href*="/events/"]'
        )

        seen_titles = set()
        for card in event_cards[:30]:
            try:
                # For Do512, events are often in links
                if card.name == 'a' and '/events/' in card.get('href', ''):
                    title = card.get_text(strip=True)
                    href = card.get('href', '')
                    url = 'https://do512.com' + href if href.startswith('/') else href
                else:
                    # Title - try multiple selectors
                    title_el = card.select_one(
                        '.ds-listing-event-title, .ds-event-title, '
                        'h2, h3, h4, .title, .event-title, '
                        '.event-name, [class*="title"], a[href*="/events/"]'
                    )
                    title = title_el.get_text(strip=True) if title_el else None

                    # URL
                    link_el = card.select_one('a[href*="/events/"], a[href]')
                    url = ''
                    if link_el:
                        href = link_el.get('href', '')
                        if href.startswith('/'):
                            url = 'https://do512.com' + href
                        elif href.startswith('http'):
                            url = href

                # Skip navigation/non-event elements
                if not title or len(title) < 3:
                    continue
                if title.lower() in ['events', 'shows', 'tickets', 'view all', 'see more']:
                    continue
                if title in seen_titles:
                    continue
                seen_titles.add(title)

                # Date - Do512 specific then generic
                date_el = card.select_one(
                    '.ds-listing-event-date, .ds-byline, '
                    'time, .date, .event-date, [class*="date"], '
                    '.when, [datetime]'
                )
                date_str = ''
                if date_el:
                    date_str = date_el.get('datetime') or date_el.get_text(strip=True)
                event_date = parse_date(date_str)

                # Description
                desc_el = card.select_one('.description, .summary, p, .info')
                description = desc_el.get_text(strip=True)[:200] if desc_el else ''

                events.append({
                    'id': f"{venue_key}_{hash(url or title) % 100000}",
                    'title': title,
                    'description': description or f"Live event at {venue['name']}",
                    'date': event_date.strftime('%Y-%m-%dT%H:%M:%S') if event_date else datetime.now().strftime('%Y-%m-%dT22:00:00'),
                    'venue': venue['name'],
                    'address': venue['address'],
                    'lat': venue['lat'],
                    'lng': venue['lng'],
                    'url': url or venue['url'],
                    'category': 'Nightlife',
                    'source': venue['name'],
                })
            except Exception:
                continue

        print(f"{venue['name']}: Found {len(events)} events")

        if events:
            save_to_cache(cache_key, events)
        return events

    except Exception as e:
        print(f"{venue['name']} error: {e}")
        return []


def scrape_19hz():
    """Scrape events from 19hz.info for Texas electronic music."""
    if is_cache_valid('19hz'):
        return load_from_cache('19hz')

    events = []
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }

        response = requests.get(
            'https://19hz.info/eventlisting_Texas.php',
            headers=headers,
            timeout=15
        )

        if response.status_code != 200:
            print(f"19hz error: Status {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')

        # 19hz uses table rows for events - look for all rows
        rows = soup.select('table tr, tr')

        for row in rows[:100]:
            try:
                cells = row.select('td')
                if len(cells) < 2:
                    continue

                # Get all text from the row to check for Austin
                row_text = row.get_text().lower()
                if 'austin' not in row_text:
                    continue

                # Try to extract event info
                # Date might be in first cell
                date_str = cells[0].get_text(strip=True) if cells else ''
                event_date = parse_date(date_str)

                # Event name - look for links or text
                title = ''
                url = ''
                for cell in cells:
                    link = cell.select_one('a')
                    if link:
                        title = link.get_text(strip=True)
                        url = link.get('href', '')
                        break

                if not title:
                    # Try to get title from any cell with substantial text
                    for cell in cells[1:]:
                        text = cell.get_text(strip=True)
                        if len(text) > 5 and not text.replace('/', '').replace('-', '').isdigit():
                            title = text
                            break

                if not title or len(title) < 3:
                    continue

                # Venue - usually has Austin in it
                venue = 'Austin Venue'
                for cell in cells:
                    text = cell.get_text(strip=True)
                    if 'austin' in text.lower() and len(text) < 100:
                        venue = text.split(',')[0].strip()
                        break

                events.append({
                    'id': f"19hz_{hash(title + str(date_str)) % 100000}",
                    'title': title[:100],
                    'description': 'Electronic music event from 19hz',
                    'date': event_date.strftime('%Y-%m-%dT%H:%M:%S') if event_date else datetime.now().strftime('%Y-%m-%dT22:00:00'),
                    'venue': venue[:50],
                    'address': 'Austin, TX',
                    'lat': AUSTIN_LAT + (hash(title) % 50) / 1000 - 0.025,
                    'lng': AUSTIN_LNG + (hash(venue) % 50) / 1000 - 0.025,
                    'url': url if url.startswith('http') else '',
                    'category': 'Nightlife',
                    'source': '19hz',
                })
            except Exception:
                continue

        # Remove duplicates by title
        seen = set()
        unique_events = []
        for e in events:
            if e['title'] not in seen:
                seen.add(e['title'])
                unique_events.append(e)

        print(f"19hz: Found {len(unique_events)} Austin events")

        if unique_events:
            save_to_cache('19hz', unique_events)
        return unique_events

    except Exception as e:
        print(f"19hz error: {e}")
        return []


def scrape_edmtrain():
    """Scrape events from EDM Train for Austin."""
    if is_cache_valid('edmtrain'):
        return load_from_cache('edmtrain')

    events = []
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }

        response = requests.get(
            'https://edmtrain.com/austin-tx',
            headers=headers,
            timeout=15
        )

        if response.status_code != 200:
            print(f"EDM Train error: Status {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find event cards
        event_cards = soup.select('.eventCard, .event-card, [class*="event"], article')

        for card in event_cards[:30]:
            try:
                # Title
                title_el = card.select_one('h2, h3, .title, .event-title, [class*="name"], a')
                title = title_el.get_text(strip=True) if title_el else None
                if not title or len(title) < 3:
                    continue

                # Skip non-event elements
                if title.lower() in ['events', 'shows', 'tickets', 'edm train']:
                    continue

                # URL
                link_el = card.select_one('a[href]')
                url = ''
                if link_el:
                    href = link_el.get('href', '')
                    url = 'https://edmtrain.com' + href if href.startswith('/') else href

                # Venue
                venue_el = card.select_one('.venue, [class*="venue"], [class*="location"]')
                venue = venue_el.get_text(strip=True) if venue_el else 'Austin Venue'

                # Date
                date_el = card.select_one('.date, time, [class*="date"]')
                date_str = date_el.get_text(strip=True) if date_el else ''
                event_date = parse_date(date_str)

                events.append({
                    'id': f"edmt_{hash(url or title) % 100000}",
                    'title': title,
                    'description': 'Electronic music event',
                    'date': event_date.strftime('%Y-%m-%dT%H:%M:%S') if event_date else datetime.now().strftime('%Y-%m-%dT22:00:00'),
                    'venue': venue,
                    'address': 'Austin, TX',
                    'lat': AUSTIN_LAT + (hash(title) % 50) / 1000 - 0.025,
                    'lng': AUSTIN_LNG + (hash(venue) % 50) / 1000 - 0.025,
                    'url': url,
                    'category': 'Nightlife',
                    'source': 'EDM Train',
                })
            except Exception:
                continue

        print(f"EDM Train: Found {len(events)} events")

        if events:
            save_to_cache('edmtrain', events)
        return events

    except Exception as e:
        print(f"EDM Train error: {e}")
        return []


def fetch_all_nightlife_events():
    """Fetch events from all nightlife sources."""
    events = []

    # Resident Advisor (often blocked)
    events.extend(scrape_resident_advisor())

    # 19hz - Texas electronic music
    events.extend(scrape_19hz())

    # EDM Train
    events.extend(scrape_edmtrain())

    # Individual venues
    for venue_key in VENUES:
        events.extend(scrape_venue(venue_key))

    return events
