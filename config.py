import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys - set these as environment variables
# Example: export YELP_API_KEY=your_key_here
EVENTBRITE_API_KEY = os.environ.get('EVENTBRITE_API_KEY', '')
YELP_API_KEY = os.environ.get('YELP_API_KEY', '')

# Austin, TX coordinates
AUSTIN_LAT = 30.2672
AUSTIN_LNG = -97.7431

# Cache settings
CACHE_DIR = os.path.join(os.path.dirname(__file__), 'cache')
CACHE_DURATION_SECONDS = 3600  # 1 hour

# Event window
EVENT_WINDOW_DAYS = 14
