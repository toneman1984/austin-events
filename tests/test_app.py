"""
Tests for the Austin Events application.
"""

import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, normalize_title, aggregate_events


@pytest.fixture
def client():
    """Create test client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestRoutes:
    """Test Flask routes."""

    def test_index_returns_200(self, client):
        """Test that index page loads successfully."""
        response = client.get('/')
        assert response.status_code == 200

    def test_index_contains_title(self, client):
        """Test that index page contains expected title."""
        response = client.get('/')
        assert b'Austin Events' in response.data

    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'ok'
        assert 'timestamp' in data

    def test_api_events_returns_json(self, client):
        """Test API events endpoint returns JSON."""
        response = client.get('/api/events')
        assert response.status_code == 200
        assert response.content_type == 'application/json'

    def test_api_events_category_filter(self, client):
        """Test API events filtering by category."""
        response = client.get('/api/events?category=Music')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)


class TestNormalization:
    """Test title normalization function."""

    def test_normalize_removes_special_chars(self):
        """Test that special characters are removed."""
        result = normalize_title("Test! Event @2026")
        assert '!' not in result
        assert '@' not in result

    def test_normalize_lowercase(self):
        """Test that titles are lowercased."""
        result = normalize_title("TEST EVENT")
        assert result == result.lower()

    def test_normalize_removes_common_words(self):
        """Test that common words are removed."""
        result = normalize_title("The Live Show Presents Music")
        assert 'the' not in result.split()
        assert 'live' not in result.split()
        assert 'presents' not in result.split()

    def test_normalize_truncates(self):
        """Test that long titles are truncated."""
        long_title = "A" * 100
        result = normalize_title(long_title)
        assert len(result) <= 40


class TestAggregation:
    """Test event aggregation."""

    def test_aggregate_returns_list(self):
        """Test that aggregate_events returns a list."""
        events = aggregate_events()
        assert isinstance(events, list)

    def test_events_have_required_fields(self):
        """Test that events have all required fields."""
        events = aggregate_events()
        required_fields = ['id', 'title', 'date', 'venue', 'category', 'source']

        for event in events[:5]:  # Check first 5 events
            for field in required_fields:
                assert field in event, f"Missing field: {field}"

    def test_events_sorted_by_date(self):
        """Test that events are sorted by date."""
        events = aggregate_events()
        if len(events) > 1:
            dates = [e['date'] for e in events]
            assert dates == sorted(dates)


class TestCategories:
    """Test event categorization."""

    def test_valid_categories(self):
        """Test that all events have valid categories."""
        valid_categories = {'Music', 'Art', 'Food', 'Markets', 'Nightlife', 'Other'}
        events = aggregate_events()

        for event in events:
            assert event['category'] in valid_categories
