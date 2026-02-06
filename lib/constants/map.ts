/**
 * Constants for NYC Opportunity Heat Map
 */

// NYC Center Coordinates (default map view)
export const NYC_CENTER_LAT = 40.7128
export const NYC_CENTER_LNG = -74.0060
export const NYC_CENTER: [number, number] = [NYC_CENTER_LAT, NYC_CENTER_LNG]

// NYC Borough Center Coordinates (for geocoding fallback)
export const BOROUGH_COORDS = {
  MANHATTAN: [40.7831, -73.9712] as [number, number],
  BRONX: [40.8448, -73.8648] as [number, number],
  BROOKLYN: [40.6782, -73.9442] as [number, number],
  QUEENS: [40.7282, -73.7949] as [number, number],
  STATEN_ISLAND: [40.5795, -74.1502] as [number, number],
}

// Opportunity Level Colors
export const OPPORTUNITY_COLORS = {
  CONTESTABLE: '#10b981', // Green
  SOFT_OPEN: '#eab308',   // Yellow
  CLOSED: '#ef4444',      // Red
} as const

// Map Configuration
export const MAP_CONFIG = {
  DEFAULT_ZOOM: 11,
  MIN_ZOOM: 10,
  MAX_ZOOM: 18,
  CLUSTER_RADIUS: 50,
  HEAT_RADIUS: 25,
  HEAT_BLUR: 15,
} as const
