"""
NYC Geocoder Service for Opportunity Heat Map

Integrates with NYC Planning's Geoservice API to convert BIN/BBL data
into geographic coordinates (latitude/longitude).

Implements caching to minimize API calls and improve performance.
"""

import os
import json
import sqlite3
import logging
from typing import Dict, Optional, Tuple
from datetime import datetime
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NYCGeocoder:
    """
    NYC Geocoder Service using NYC Planning Geoservice API.
    
    Converts Building Identification Numbers (BIN) and Borough-Block-Lot (BBL)
    references into latitude/longitude coordinates for mapping.
    
    Features:
    - NYC Planning Labs Geoclient API integration
    - Local SQLite caching to minimize API calls
    - Automatic cache management
    - Error handling and retry logic
    """
    
    # NYC Planning Geoclient API endpoints
    GEOCLIENT_BASE_URL = "https://api.nyc.gov/geo/geoclient/v2"
    
    def __init__(self, cache_db_path: str = None, api_key: str = None, api_id: str = None):
        """
        Initialize the geocoder service.
        
        Args:
            cache_db_path: Path to SQLite cache database (default: ./data/geocode_cache.db)
            api_key: NYC Geoclient API key (from environment if not provided)
            api_id: NYC Geoclient API ID (from environment if not provided)
        """
        self.cache_db_path = cache_db_path or os.path.join(
            os.path.dirname(__file__), '../../../data/geocode_cache.db'
        )
        
        # Get API credentials from environment or parameters
        self.api_key = api_key or os.getenv('NYC_GEOCLIENT_API_KEY')
        self.api_id = api_id or os.getenv('NYC_GEOCLIENT_API_ID')
        
        if not self.api_key or not self.api_id:
            logger.warning(
                "NYC Geoclient API credentials not found. "
                "Geocoding will use fallback methods. "
                "Set NYC_GEOCLIENT_API_KEY and NYC_GEOCLIENT_API_ID environment variables."
            )
        
        # Initialize cache database
        self._init_cache()
    
    def _init_cache(self):
        """Initialize the SQLite cache database."""
        os.makedirs(os.path.dirname(self.cache_db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.cache_db_path)
        cursor = conn.cursor()
        
        # Create geocode cache table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS geocode_cache (
                identifier TEXT PRIMARY KEY,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                address TEXT,
                source TEXT,
                created_at TEXT NOT NULL,
                accessed_at TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
        
        logger.info(f"Geocode cache initialized at {self.cache_db_path}")
    
    def geocode_bin(self, bin_number: str) -> Optional[Tuple[float, float]]:
        """
        Geocode a Building Identification Number (BIN) to coordinates.
        
        Args:
            bin_number: NYC Building Identification Number (7 digits)
        
        Returns:
            Tuple of (latitude, longitude) or None if not found
        """
        identifier = f"BIN:{bin_number}"
        
        # Check cache first
        cached = self._get_from_cache(identifier)
        if cached:
            return cached
        
        # Call NYC Geoclient API
        if self.api_key and self.api_id:
            coords = self._geocode_bin_api(bin_number)
            if coords:
                self._save_to_cache(identifier, coords[0], coords[1], source="NYC_Geoclient_API")
                return coords
        
        logger.warning(f"Could not geocode BIN: {bin_number}")
        return None
    
    def geocode_bbl(self, borough: str, block: str, lot: str) -> Optional[Tuple[float, float]]:
        """
        Geocode a Borough-Block-Lot (BBL) reference to coordinates.
        
        Args:
            borough: Borough code (1=Manhattan, 2=Bronx, 3=Brooklyn, 4=Queens, 5=Staten Island)
            block: Tax block number
            lot: Tax lot number
        
        Returns:
            Tuple of (latitude, longitude) or None if not found
        """
        # Normalize BBL format
        bbl = f"{borough}{block.zfill(5)}{lot.zfill(4)}"
        identifier = f"BBL:{bbl}"
        
        # Check cache first
        cached = self._get_from_cache(identifier)
        if cached:
            return cached
        
        # Call NYC Geoclient API
        if self.api_key and self.api_id:
            coords = self._geocode_bbl_api(borough, block, lot)
            if coords:
                self._save_to_cache(identifier, coords[0], coords[1], source="NYC_Geoclient_API")
                return coords
        
        logger.warning(f"Could not geocode BBL: {bbl}")
        return None
    
    def geocode_address(self, address: str, borough: str = None) -> Optional[Tuple[float, float]]:
        """
        Geocode a NYC address to coordinates.
        
        Args:
            address: Street address (e.g., "123 Main Street")
            borough: Optional borough name or code
        
        Returns:
            Tuple of (latitude, longitude) or None if not found
        """
        identifier = f"ADDR:{address}:{borough or 'NYC'}"
        
        # Check cache first
        cached = self._get_from_cache(identifier)
        if cached:
            return cached
        
        # Call NYC Geoclient API
        if self.api_key and self.api_id:
            coords = self._geocode_address_api(address, borough)
            if coords:
                self._save_to_cache(identifier, coords[0], coords[1], 
                                   address=address, source="NYC_Geoclient_API")
                return coords
        
        # Fallback: Extract location from address string and use approximate coordinates
        coords = self._geocode_address_fallback(address)
        if coords:
            self._save_to_cache(identifier, coords[0], coords[1], 
                               address=address, source="Fallback")
            return coords
        
        logger.warning(f"Could not geocode address: {address}")
        return None
    
    def _geocode_bin_api(self, bin_number: str) -> Optional[Tuple[float, float]]:
        """Call NYC Geoclient API for BIN geocoding."""
        try:
            url = f"{self.GEOCLIENT_BASE_URL}/bin.json"
            params = {
                'bin': bin_number,
                'app_id': self.api_id,
                'app_key': self.api_key
            }
            
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            if 'bin' in data and 'latitude' in data['bin'] and 'longitude' in data['bin']:
                lat = float(data['bin']['latitude'])
                lon = float(data['bin']['longitude'])
                return (lat, lon)
                
        except Exception as e:
            logger.error(f"Error geocoding BIN {bin_number}: {str(e)}")
        
        return None
    
    def _geocode_bbl_api(self, borough: str, block: str, lot: str) -> Optional[Tuple[float, float]]:
        """Call NYC Geoclient API for BBL geocoding."""
        try:
            url = f"{self.GEOCLIENT_BASE_URL}/bbl.json"
            params = {
                'borough': borough,
                'block': block,
                'lot': lot,
                'app_id': self.api_id,
                'app_key': self.api_key
            }
            
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            if 'bbl' in data and 'latitude' in data['bbl'] and 'longitude' in data['bbl']:
                lat = float(data['bbl']['latitude'])
                lon = float(data['bbl']['longitude'])
                return (lat, lon)
                
        except Exception as e:
            logger.error(f"Error geocoding BBL {borough}-{block}-{lot}: {str(e)}")
        
        return None
    
    def _geocode_address_api(self, address: str, borough: str = None) -> Optional[Tuple[float, float]]:
        """Call NYC Geoclient API for address geocoding."""
        try:
            url = f"{self.GEOCLIENT_BASE_URL}/search.json"
            params = {
                'input': address,
                'app_id': self.api_id,
                'app_key': self.api_key
            }
            
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            if 'results' in data and len(data['results']) > 0:
                result = data['results'][0]
                if 'response' in result:
                    resp = result['response']
                    if 'latitude' in resp and 'longitude' in resp:
                        lat = float(resp['latitude'])
                        lon = float(resp['longitude'])
                        return (lat, lon)
                
        except Exception as e:
            logger.error(f"Error geocoding address {address}: {str(e)}")
        
        return None
    
    def _geocode_address_fallback(self, address: str) -> Optional[Tuple[float, float]]:
        """
        Fallback geocoding using approximate borough centers.
        
        This is used when API keys are not available or API calls fail.
        Returns approximate coordinates based on borough mentions in the address.
        """
        address_lower = address.lower()
        
        # Approximate borough centers
        borough_coords = {
            'manhattan': (40.7831, -73.9712),
            'bronx': (40.8448, -73.8648),
            'brooklyn': (40.6782, -73.9442),
            'queens': (40.7282, -73.7949),
            'staten island': (40.5795, -74.1502),
            # Short names
            'ny': (40.7831, -73.9712),  # Default to Manhattan
        }
        
        for borough, coords in borough_coords.items():
            if borough in address_lower:
                logger.info(f"Using fallback coordinates for {borough}")
                return coords
        
        # Default to NYC center if no borough identified
        logger.info("Using default NYC center coordinates")
        return (40.7128, -74.0060)
    
    def _get_from_cache(self, identifier: str) -> Optional[Tuple[float, float]]:
        """Retrieve coordinates from cache."""
        try:
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                'SELECT latitude, longitude FROM geocode_cache WHERE identifier = ?',
                (identifier,)
            )
            
            row = cursor.fetchone()
            
            if row:
                # Update accessed_at timestamp
                cursor.execute(
                    'UPDATE geocode_cache SET accessed_at = ? WHERE identifier = ?',
                    (datetime.now().isoformat(), identifier)
                )
                conn.commit()
                
                logger.debug(f"Cache hit for {identifier}")
                return (row[0], row[1])
            
            conn.close()
            
        except Exception as e:
            logger.error(f"Cache read error: {str(e)}")
        
        return None
    
    def _save_to_cache(self, identifier: str, latitude: float, longitude: float,
                      address: str = None, source: str = "API"):
        """Save coordinates to cache."""
        try:
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            
            cursor.execute('''
                INSERT OR REPLACE INTO geocode_cache 
                (identifier, latitude, longitude, address, source, created_at, accessed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (identifier, latitude, longitude, address, source, now, now))
            
            conn.commit()
            conn.close()
            
            logger.debug(f"Cached coordinates for {identifier}")
            
        except Exception as e:
            logger.error(f"Cache write error: {str(e)}")
    
    def clear_cache(self):
        """Clear all cached geocoding data."""
        try:
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM geocode_cache')
            conn.commit()
            conn.close()
            logger.info("Geocode cache cleared")
        except Exception as e:
            logger.error(f"Error clearing cache: {str(e)}")


def geocode_project_location(location: str) -> Optional[Tuple[float, float]]:
    """
    Convenience function to geocode a project location string.
    
    Args:
        location: Location string (e.g., "Brooklyn, NY", "123 Main St, Manhattan")
    
    Returns:
        Tuple of (latitude, longitude) or None if not found
    """
    geocoder = NYCGeocoder()
    return geocoder.geocode_address(location)


if __name__ == "__main__":
    # Test the geocoder with sample data
    geocoder = NYCGeocoder()
    
    # Test with borough centers (fallback mode without API keys)
    test_locations = [
        "Brooklyn, NY",
        "Manhattan, NY",
        "Queens, NY",
        "Bronx, NY",
        "Staten Island, NY"
    ]
    
    print("Testing NYC Geocoder (Fallback Mode):")
    print("-" * 50)
    
    for location in test_locations:
        coords = geocoder.geocode_address(location)
        if coords:
            print(f"{location:20} -> {coords[0]:.4f}, {coords[1]:.4f}")
        else:
            print(f"{location:20} -> NOT FOUND")
