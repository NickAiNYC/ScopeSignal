'use client'

import { useEffect, useRef } from 'react'
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import 'leaflet.markercluster/dist/MarkerCluster.css'
import 'leaflet.markercluster/dist/MarkerCluster.Default.css'
import { CheckCircle, AlertTriangle, XCircle, TrendingUp } from 'lucide-react'

// Fix for default marker icons in React-Leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
})

interface ProjectLocation {
  id: string
  title: string
  classification: 'CLOSED' | 'SOFT_OPEN' | 'CONTESTABLE'
  trade: 'Electrical' | 'HVAC' | 'Plumbing'
  latitude: number
  longitude: number
  feasibility_score: number
  confidence: number
  agency: string
  location: string
  posted_date: string
  can_bid: boolean
}

interface ProjectMapContentProps {
  projects: ProjectLocation[]
  showHeatMap: boolean
  showMarkers: boolean
  onProjectClick?: (project: ProjectLocation) => void
}

// Custom marker icons based on classification
const createCustomIcon = (classification: string, trade: string) => {
  const color = classification === 'CONTESTABLE' 
    ? '#10b981' // green
    : classification === 'SOFT_OPEN' 
    ? '#eab308' // yellow
    : '#ef4444' // red

  const tradeEmoji = trade === 'Electrical' 
    ? '⚡' 
    : trade === 'HVAC' 
    ? '❄️' 
    : '🔧'

  return L.divIcon({
    html: `
      <div style="
        background-color: ${color};
        width: 30px;
        height: 30px;
        border-radius: 50%;
        border: 3px solid white;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
      ">
        ${tradeEmoji}
      </div>
    `,
    className: 'custom-marker-icon',
    iconSize: [30, 30],
    iconAnchor: [15, 15],
    popupAnchor: [0, -15]
  })
}

// Heat map layer component
function HeatMapLayer({ projects }: { projects: ProjectLocation[] }) {
  const map = useMap()
  const heatLayerRef = useRef<any>(null)

  useEffect(() => {
    // Dynamically import leaflet.heat
    import('leaflet.heat').then((module: any) => {
      // Remove existing heat layer
      if (heatLayerRef.current) {
        map.removeLayer(heatLayerRef.current)
      }

      // Prepare heat map data
      const heatData = projects.map(project => {
        // Intensity based on classification
        let intensity = 0.3
        if (project.classification === 'SOFT_OPEN') intensity = 0.6
        if (project.classification === 'CONTESTABLE') intensity = 1.0
        
        // Also factor in feasibility score
        intensity *= (project.feasibility_score / 100)

        return [project.latitude, project.longitude, intensity]
      })

      // Get the heatLayer function from the module
      const heatLayerFn = module.default || module
      
      // Create heat layer with custom gradient
      const heatLayer = heatLayerFn(heatData, {
        radius: 25,
        blur: 15,
        maxZoom: 17,
        max: 1.0,
        gradient: {
          0.0: '#ef4444',  // Red for low intensity (CLOSED)
          0.5: '#eab308',  // Yellow for medium (SOFT_OPEN)
          1.0: '#10b981'   // Green for high intensity (CONTESTABLE)
        }
      })

      heatLayer.addTo(map)
      heatLayerRef.current = heatLayer
    }).catch(err => {
      console.warn('Failed to load heat map layer:', err)
    })

    // Cleanup
    return () => {
      if (heatLayerRef.current) {
        map.removeLayer(heatLayerRef.current)
      }
    }
  }, [projects, map])

  return null
}

// Marker cluster layer component
function MarkerClusterLayer({ 
  projects, 
  onProjectClick 
}: { 
  projects: ProjectLocation[]
  onProjectClick?: (project: ProjectLocation) => void 
}) {
  const map = useMap()
  const clusterGroupRef = useRef<any>(null)

  useEffect(() => {
    // Dynamically import marker cluster
    import('leaflet.markercluster').then(() => {
      // Remove existing cluster
      if (clusterGroupRef.current) {
        map.removeLayer(clusterGroupRef.current)
      }

      // Create marker cluster group
      const markers = (L as any).markerClusterGroup({
        maxClusterRadius: 50,
        spiderfyOnMaxZoom: true,
        showCoverageOnHover: false,
        zoomToBoundsOnClick: true,
        iconCreateFunction: function(cluster: any) {
          const count = cluster.getChildCount()
          const size = count < 10 ? 'small' : count < 50 ? 'medium' : 'large'
          
          return L.divIcon({
            html: `
              <div style="
                background-color: rgba(59, 130, 246, 0.8);
                color: white;
                border-radius: 50%;
                border: 3px solid white;
                box-shadow: 0 2px 8px rgba(0,0,0,0.3);
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
                width: ${size === 'small' ? '40px' : size === 'medium' ? '50px' : '60px'};
                height: ${size === 'small' ? '40px' : size === 'medium' ? '50px' : '60px'};
                font-size: ${size === 'small' ? '12px' : size === 'medium' ? '14px' : '16px'};
              ">
                ${count}
              </div>
            `,
            className: 'marker-cluster-custom',
            iconSize: L.point(40, 40)
          })
        }
      })

      // Add markers to cluster
      projects.forEach(project => {
        const icon = createCustomIcon(project.classification, project.trade)
        const marker = L.marker([project.latitude, project.longitude], { icon })

        // Create popup content
        const popupContent = `
          <div style="min-width: 250px; font-family: system-ui, -apple-system, sans-serif;">
            <div style="margin-bottom: 8px;">
              <strong style="font-size: 14px; color: #1e293b;">${project.title}</strong>
            </div>
            
            <div style="display: flex; gap: 8px; margin-bottom: 8px;">
              <span style="
                padding: 2px 8px;
                border-radius: 4px;
                font-size: 11px;
                font-weight: 500;
                background-color: ${project.classification === 'CONTESTABLE' ? '#d1fae5' : project.classification === 'SOFT_OPEN' ? '#fef3c7' : '#fee2e2'};
                color: ${project.classification === 'CONTESTABLE' ? '#065f46' : project.classification === 'SOFT_OPEN' ? '#92400e' : '#991b1b'};
              ">
                ${project.classification}
              </span>
              <span style="
                padding: 2px 8px;
                border-radius: 4px;
                font-size: 11px;
                font-weight: 500;
                background-color: #dbeafe;
                color: #1e40af;
              ">
                ${project.agency}
              </span>
            </div>

            <div style="margin-bottom: 8px; color: #64748b; font-size: 12px;">
              <div><strong>Trade:</strong> ${project.trade}</div>
              <div><strong>Location:</strong> ${project.location}</div>
              <div><strong>Confidence:</strong> ${project.confidence}%</div>
              <div><strong>Feasibility Score:</strong> ${project.feasibility_score.toFixed(1)}</div>
            </div>

            <div style="
              padding: 8px;
              border-radius: 4px;
              background-color: ${project.can_bid ? '#d1fae5' : '#fee2e2'};
              margin-bottom: 8px;
            ">
              <div style="
                display: flex;
                align-items: center;
                gap: 4px;
                color: ${project.can_bid ? '#065f46' : '#991b1b'};
                font-size: 12px;
                font-weight: 500;
              ">
                ${project.can_bid ? '✓' : '✗'} ${project.can_bid ? 'Ready to Bid' : 'Not Compliant'}
              </div>
            </div>

            ${project.can_bid ? `
              <button 
                onclick="alert('Starting compliance outreach for: ${project.title.replace(/'/g, "\\'")}');window.location.href='/veteran-dashboard'"
                style="
                  width: 100%;
                  padding: 8px;
                  background-color: #3b82f6;
                  color: white;
                  border: none;
                  border-radius: 6px;
                  font-size: 12px;
                  font-weight: 600;
                  cursor: pointer;
                  transition: background-color 0.2s;
                "
                onmouseover="this.style.backgroundColor='#2563eb'"
                onmouseout="this.style.backgroundColor='#3b82f6'"
              >
                🚀 Start Compliance Outreach
              </button>
            ` : ''}

            <div style="margin-top: 8px; color: #94a3b8; font-size: 11px; text-align: center;">
              Posted: ${project.posted_date}
            </div>
          </div>
        `

        marker.bindPopup(popupContent, {
          maxWidth: 300,
          className: 'custom-popup'
        })

        if (onProjectClick) {
          marker.on('click', () => onProjectClick(project))
        }

        markers.addLayer(marker)
      })

      markers.addTo(map)
      clusterGroupRef.current = markers
    })

    // Cleanup
    return () => {
      if (clusterGroupRef.current) {
        map.removeLayer(clusterGroupRef.current)
      }
    }
  }, [projects, map, onProjectClick])

  return null
}

export default function ProjectMapContent({ 
  projects, 
  showHeatMap, 
  showMarkers,
  onProjectClick 
}: ProjectMapContentProps) {
  // NYC center coordinates
  const nycCenter: [number, number] = [40.7128, -74.0060]

  return (
    <MapContainer
      center={nycCenter}
      zoom={11}
      style={{ width: '100%', height: '100%' }}
      className="z-0"
    >
      {/* Dark mode tile layer - using CartoDB Dark Matter */}
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
        url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
      />

      {/* Heat map layer */}
      {showHeatMap && projects.length > 0 && (
        <HeatMapLayer projects={projects} />
      )}

      {/* Marker cluster layer */}
      {showMarkers && projects.length > 0 && (
        <MarkerClusterLayer projects={projects} onProjectClick={onProjectClick} />
      )}
    </MapContainer>
  )
}
