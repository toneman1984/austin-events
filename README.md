# Austin Events Aggregator

[![CI/CD Pipeline](https://github.com/YOUR_USERNAME/austin-events/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/YOUR_USERNAME/austin-events/actions/workflows/ci-cd.yml)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-2.3+-green.svg)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A full-stack web application that aggregates events, concerts, art exhibits, markets, and nightlife happenings in Austin, TX. Features interactive mapping with Leaflet.js, real-time data aggregation from multiple sources, and a responsive calendar view.

![Austin Events Screenshot](docs/images/screenshot.png)

## Features

- **Multi-Source Aggregation**: Pulls events from Do512, Austin Chronicle, Yelp, EDM Train, and venue-specific sources
- **Interactive GIS Mapping**: Leaflet.js + OpenStreetMap with color-coded category markers
- **Calendar View**: 3-week calendar visualization with event density indicators
- **Category Filtering**: Filter by Music, Art, Food, Markets, Nightlife
- **Smart Deduplication**: Normalizes and deduplicates events across sources
- **Caching Layer**: 1-hour cache to respect API rate limits
- **Responsive Design**: Mobile-friendly dark theme UI
- **Docker Ready**: Containerized for easy deployment

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Python 3.11, Flask |
| **Frontend** | HTML5, CSS3, JavaScript |
| **Mapping** | Leaflet.js, OpenStreetMap |
| **Data Sources** | REST APIs, RSS Feeds, Web Scraping |
| **Containerization** | Docker, Docker Compose |
| **CI/CD** | GitHub Actions |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ List View   │  │ Calendar    │  │ Leaflet Map         │  │
│  │             │  │ View        │  │ (OpenStreetMap)     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Flask Backend                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Routes      │  │ Aggregator  │  │ Deduplication       │  │
│  │ /           │  │ Engine      │  │ Engine              │  │
│  │ /api/events │  │             │  │                     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Data Sources Layer                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────────┐  │
│  │ Do512    │ │ Yelp API │ │ Chronicle│ │ Venue Scrapers │  │
│  │ Scraper  │ │          │ │ RSS      │ │ Kingdom, etc.  │  │
│  └──────────┘ └──────────┘ └──────────┘ └────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Cache Layer                             │
│                   (File-based JSON)                          │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/austin-events.git
cd austin-events

# Set environment variables (optional - works with demo data)
export YELP_API_KEY=your_key_here

# Run with Docker Compose
docker-compose up -d

# Open http://localhost:5000
```

### Option 2: Local Development

```bash
# Clone and enter directory
git clone https://github.com/YOUR_USERNAME/austin-events.git
cd austin-events

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables (optional)
export YELP_API_KEY=your_key_here

# Run the application
python app.py

# Open http://localhost:5000
```

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `YELP_API_KEY` | No | Yelp Fusion API key for restaurant data |
| `EVENTBRITE_API_KEY` | No | Eventbrite API key (deprecated API) |
| `FLASK_ENV` | No | Set to `development` for debug mode |

### Obtaining API Keys

- **Yelp**: https://www.yelp.com/developers/v3/manage_app (Free, 500 calls/day)

## Project Structure

```
austin_events/
├── app.py                 # Flask application entry point
├── config.py              # Configuration and environment variables
├── requirements.txt       # Python dependencies
├── Dockerfile             # Container image definition
├── docker-compose.yml     # Container orchestration
│
├── sources/               # Data source modules
│   ├── __init__.py
│   ├── eventbrite.py      # Eventbrite API client
│   ├── yelp.py            # Yelp Fusion API client
│   ├── rss_feeds.py       # RSS feed parser (Do512, Chronicle)
│   └── nightlife.py       # Nightlife venue scrapers
│
├── templates/
│   └── index.html         # Main page template (Jinja2)
│
├── static/
│   └── style.css          # Application styles
│
├── cache/                 # Cached API responses (auto-generated)
│
├── .github/
│   └── workflows/
│       └── ci-cd.yml      # GitHub Actions CI/CD pipeline
│
└── docs/                  # Documentation
    └── images/
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main page with event list, map, and calendar |
| `/api/events` | GET | JSON API for all events |
| `/api/events?category=Music` | GET | Filter events by category |
| `/health` | GET | Health check endpoint |

## Data Sources

| Source | Type | Data Provided |
|--------|------|---------------|
| Do512 | Web Scrape | Austin-specific events, concerts, local shows |
| Austin Chronicle | RSS Feed | Art exhibits, live music, community events |
| Yelp Fusion | REST API | Top-rated restaurants and bars |
| EDM Train | Web Scrape | Electronic music events |
| Kingdom | Web Scrape | Nightclub events |
| Concourse Project | Web Scrape | Electronic music venue events |

## Development

### Running Tests

```bash
pip install pytest pytest-cov
pytest --cov=. --cov-report=html
```

### Code Linting

```bash
pip install flake8
flake8 . --max-line-length=127
```

### Building Docker Image

```bash
docker build -t austin-events .
docker run -p 5000:5000 austin-events
```

## Deployment

### AWS ECS

1. Push image to ECR
2. Create ECS cluster and task definition
3. Configure environment variables in task definition
4. Deploy service with load balancer

### Azure App Service

1. Push image to Azure Container Registry
2. Create App Service with container deployment
3. Configure environment variables in App Settings

See `.github/workflows/ci-cd.yml` for deployment configuration.

## Future Enhancements

- [ ] Marker clustering for dense event areas
- [ ] Heatmap visualization of event density
- [ ] Spatial search (events within X miles)
- [ ] GeoJSON export endpoint
- [ ] User favorites and notifications
- [ ] PostGIS integration for spatial queries

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Leaflet.js](https://leafletjs.com/) - Interactive maps
- [OpenStreetMap](https://www.openstreetmap.org/) - Map tiles
- [Do512](https://do512.com/) - Austin events data
- [Flask](https://flask.palletsprojects.com/) - Web framework
