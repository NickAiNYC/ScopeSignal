'use client'

import { useEffect, useState } from 'react'
import dynamic from 'next/dynamic'
import { Layers, MapPin } from 'lucide-react'

// Types for our project data
export interface ProjectLocation {
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

interface ProjectMapProps {
  projects: ProjectLocation[]
  selectedTrades?: ('Electrical' | 'HVAC' | 'Plumbing')[]
  onProjectClick?: (project: ProjectLocation) => void
}

// Dynamically import the actual map component to avoid SSR issues
const DynamicMapContent = dynamic(
  () => import('./ProjectMapContent'),
  { 
    ssr: false,
    loading: () => (
      <div className="w-full h-full flex items-center justify-center bg-slate-900/50 rounded-lg">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-slate-400">Loading Map...</p>
        </div>
      </div>
    )
  }
)

export default function ProjectMap({ projects, selectedTrades, onProjectClick }: ProjectMapProps) {
  const [enabledTrades, setEnabledTrades] = useState<Set<string>>(
    new Set(['Electrical', 'HVAC', 'Plumbing'])
  )
  const [showHeatMap, setShowHeatMap] = useState(true)
  const [showMarkers, setShowMarkers] = useState(true)

  // Filter projects based on enabled trades
  const filteredProjects = projects.filter(project => 
    enabledTrades.has(project.trade)
  )

  const toggleTrade = (trade: string) => {
    const newEnabledTrades = new Set(enabledTrades)
    if (newEnabledTrades.has(trade)) {
      newEnabledTrades.delete(trade)
    } else {
      newEnabledTrades.add(trade)
    }
    setEnabledTrades(newEnabledTrades)
  }

  // Stats for the legend
  const stats = {
    contestable: filteredProjects.filter(p => p.classification === 'CONTESTABLE').length,
    softOpen: filteredProjects.filter(p => p.classification === 'SOFT_OPEN').length,
    closed: filteredProjects.filter(p => p.classification === 'CLOSED').length,
  }

  return (
    <div className="space-y-4">
      {/* Control Panel */}
      <div className="glass rounded-lg p-4">
        <div className="flex items-center justify-between flex-wrap gap-4">
          {/* Trade Toggles */}
          <div className="flex items-center space-x-4">
            <Layers className="w-5 h-5 text-slate-400" />
            <span className="text-sm font-medium text-slate-400">Trade Layers:</span>
            
            <button
              onClick={() => toggleTrade('Electrical')}
              className={`px-3 py-1.5 rounded text-sm font-medium transition-colors ${
                enabledTrades.has('Electrical')
                  ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/50'
                  : 'bg-slate-800 text-slate-500 border border-slate-700'
              }`}
            >
              ⚡ Electrical
            </button>

            <button
              onClick={() => toggleTrade('HVAC')}
              className={`px-3 py-1.5 rounded text-sm font-medium transition-colors ${
                enabledTrades.has('HVAC')
                  ? 'bg-blue-500/20 text-blue-400 border border-blue-500/50'
                  : 'bg-slate-800 text-slate-500 border border-slate-700'
              }`}
            >
              ❄️ HVAC
            </button>

            <button
              onClick={() => toggleTrade('Plumbing')}
              className={`px-3 py-1.5 rounded text-sm font-medium transition-colors ${
                enabledTrades.has('Plumbing')
                  ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/50'
                  : 'bg-slate-800 text-slate-500 border border-slate-700'
              }`}
            >
              🔧 Plumbing
            </button>
          </div>

          {/* View Toggles */}
          <div className="flex items-center space-x-2">
            <label className="flex items-center space-x-2 text-sm cursor-pointer">
              <input
                type="checkbox"
                checked={showHeatMap}
                onChange={(e) => setShowHeatMap(e.target.checked)}
                className="rounded"
              />
              <span className="text-slate-300">Heat Map</span>
            </label>

            <label className="flex items-center space-x-2 text-sm cursor-pointer">
              <input
                type="checkbox"
                checked={showMarkers}
                onChange={(e) => setShowMarkers(e.target.checked)}
                className="rounded"
              />
              <span className="text-slate-300">Markers</span>
            </label>
          </div>

          {/* Project Count */}
          <div className="flex items-center space-x-2">
            <MapPin className="w-4 h-4 text-slate-400" />
            <span className="text-sm text-slate-400">
              Showing {filteredProjects.length} of {projects.length} projects
            </span>
          </div>
        </div>
      </div>

      {/* Legend */}
      <div className="glass rounded-lg p-4">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div className="flex items-center space-x-6">
            <span className="text-sm font-medium text-slate-400">Opportunity Level:</span>
            
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 rounded-full bg-green-500"></div>
              <span className="text-sm text-slate-300">Contestable ({stats.contestable})</span>
            </div>

            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 rounded-full bg-yellow-500"></div>
              <span className="text-sm text-slate-300">Soft Open ({stats.softOpen})</span>
            </div>

            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 rounded-full bg-red-500"></div>
              <span className="text-sm text-slate-300">Closed ({stats.closed})</span>
            </div>
          </div>
        </div>
      </div>

      {/* Map Container */}
      <div className="glass rounded-lg overflow-hidden" style={{ height: '600px' }}>
        <DynamicMapContent 
          projects={filteredProjects}
          showHeatMap={showHeatMap}
          showMarkers={showMarkers}
          onProjectClick={onProjectClick}
        />
      </div>
    </div>
  )
}
