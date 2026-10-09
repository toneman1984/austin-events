# Austin Events API Documentation

## Overview

The Austin Events API provides programmatic access to aggregated event data from multiple sources in Austin, TX.

## Base URL

```
http://localhost:5000
```

## Endpoints

### Get All Events

Retrieves all aggregated events for the next 2 weeks.

**Request**

```http
GET /api/events
```

**Query Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `category` | string | Filter by category (Music, Art, Food, Markets, Nightlife, Other) |

**Response**

```json
[
  {
    "id": "do512_12345",
    "title": "Live Music at Mohawk",
    "description": "Local bands showcase featuring Austin's best indie rock acts.",
    "date": "2026-10-15T20:00:00",
    "venue": "Mohawk Austin",
    "address": "912 Red River St, Austin, TX",
    "lat": 30.2685,
    "lng": -97.7365,
    "url": "https://do512.com/events/12345",
    "category": "Music",
    "source": "Do512"
  }
]
```

**Example Requests**

```bash
# Get all events
curl http://localhost:5000/api/events

# Get only Music events
curl http://localhost:5000/api/events?category=Music

# Get only Nightlife events
curl http://localhost:5000/api/events?category=Nightlife
```

### Health Check

Check if the API is running.

**Request**

```http
GET /health
```

**Response**

```json
{
  "status": "ok",
  "timestamp": "2026-10-08T16:30:00.000000"
}
```

## Event Object

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier (prefixed by source) |
| `title` | string | Event title |
| `description` | string | Brief description (max 200 chars) |
| `date` | string | ISO 8601 datetime |
| `venue` | string | Venue name |
| `address` | string | Full address |
| `lat` | float | Latitude coordinate |
| `lng` | float | Longitude coordinate |
| `url` | string | Link to event details |
| `category` | string | Event category |
| `source` | string | Data source name |

## Categories

- `Music` - Concerts, live music, DJ sets
- `Art` - Galleries, exhibits, art shows
- `Food` - Restaurants, food festivals, tastings
- `Markets` - Farmers markets, craft fairs, vintage markets
- `Nightlife` - Clubs, raves, late-night events
- `Other` - Uncategorized events

## Rate Limiting

The API implements a 1-hour cache to respect upstream API rate limits. Responses may be up to 1 hour old.

## Error Responses

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 404 | Endpoint not found |
| 500 | Server error |

## CORS

CORS is not enabled by default. For cross-origin requests, deploy behind a reverse proxy with CORS headers.
