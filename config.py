import os

# API Keys - set these as environment variables
EVENTBRITE_API_KEY = '24IIKPJS6XJ3VMFEEPX4'
YELP_API_KEY = 'ML7kfLxVS_2DFVcsxi7N_Q-DvnljYRQMnJ_A-snSviGawnTLcvr8E54-oH1NSqe2H49_kbDGlNe7Nu2amYWaskLCVPoLeZVlUKyFGVNQ6LiMlk48NDMMc-eQ8gPIanYx'

# Austin, TX coordinates
AUSTIN_LAT = 30.2672
AUSTIN_LNG = -97.7431

# Cache settings
CACHE_DIR = os.path.join(os.path.dirname(__file__), 'cache')
CACHE_DURATION_SECONDS = 3600  # 1 hour

# Event window
EVENT_WINDOW_DAYS = 14
