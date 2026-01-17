'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Construction, TrendingUp, AlertCircle, MapPin } from 'lucide-react'
import ThreeVisualization from '@/components/visualizations/ThreeVisualization'
import RealtimeDataFeed from '@/components/ui/RealtimeDataFeed'

interface Opportunity {
  id: string
  title: string
  classification: string
  confidence: number
  location: string
  trade: string
  status: string
}

export default function ScopeSignalDashboard() {
  const [opportunities, setOpportunities] = useState<Opportunity[]>([])
  const [stats, setStats] = useState({
    total: 0,
    contestable: 0,
    softOpen: 0,
    closed: 0,
  })

  useEffect(() => {
    // Simulate loading data - in production, this would fetch from the Python backend
    const mockOpportunities: Opportunity[] = [
      {
        id: '1',
        title: 'DDC School Addition - HVAC Work',
        classification: 'CONTESTABLE',
        confidence: 85,
        location: 'Brooklyn, NY',
        trade: 'HVAC',
        status: 'active',
      },
      {
        id: '2',
        title: 'HPD Housing Project - Electrical',
        classification: 'SOFT_OPEN',
        confidence: 72,
        location: 'Manhattan, NY',
        trade: 'Electrical',
        status: 'active',
      },
      {
        id: '3',
        title: 'SCA Renovation - Plumbing Amendment',
        classification: 'CLOSED',
        confidence: 94,
        location: 'Queens, NY',
        trade: 'Plumbing',
        status: 'closed',
      },
    ]

    setOpportunities(mockOpportunities)
    setStats({
      total: mockOpportunities.length,
      contestable: mockOpportunities.filter(o => o.classification === 'CONTESTABLE').length,
      softOpen: mockOpportunities.filter(o => o.classification === 'SOFT_OPEN').length,
      closed: mockOpportunities.filter(o => o.classification === 'CLOSED').length,
    })
  }, [])

  const getClassificationColor = (classification: string) => {
    switch (classification) {
      case 'CONTESTABLE':
        return 'text-green-400 bg-green-400/10'
      case 'SOFT_OPEN':
        return 'text-yellow-400 bg-yellow-400/10'
      case 'CLOSED':
        return 'text-red-400 bg-red-400/10'
      default:
        return 'text-slate-400 bg-slate-400/10'
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div className="flex items-center space-x-4">
          <div className="w-12 h-12 gradient-scopesignal rounded-lg flex items-center justify-center">
            <Construction className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold">ScopeSignal</h1>
            <p className="text-slate-400">Construction Opportunity Radar</p>
          </div>
        </div>
      </motion.div>

      {/* Stats Grid */}
      <motion.div
        className="grid grid-cols-1 md:grid-cols-4 gap-4"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <div className="glass rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-slate-400">Total Projects</span>
            <TrendingUp className="w-4 h-4 text-blue-400" />
          </div>
          <div className="text-2xl font-bold">{stats.total}</div>
        </div>

        <div className="glass rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-slate-400">Contestable</span>
            <AlertCircle className="w-4 h-4 text-green-400" />
          </div>
          <div className="text-2xl font-bold text-green-400">{stats.contestable}</div>
        </div>

        <div className="glass rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-slate-400">Soft Open</span>
            <AlertCircle className="w-4 h-4 text-yellow-400" />
          </div>
          <div className="text-2xl font-bold text-yellow-400">{stats.softOpen}</div>
        </div>

        <div className="glass rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-slate-400">Closed</span>
            <AlertCircle className="w-4 h-4 text-red-400" />
          </div>
          <div className="text-2xl font-bold text-red-400">{stats.closed}</div>
        </div>
      </motion.div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 3D Visualization */}
        <motion.div
          className="glass rounded-lg p-6"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
        >
          <h2 className="text-xl font-bold mb-4">Geographic Distribution</h2>
          <div className="h-[400px] bg-slate-900 rounded-lg overflow-hidden">
            <ThreeVisualization data={opportunities} />
          </div>
        </motion.div>

        {/* Real-time Data Feed */}
        <motion.div
          className="glass rounded-lg p-6"
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
        >
          <h2 className="text-xl font-bold mb-4">Live Opportunities</h2>
          <RealtimeDataFeed />
        </motion.div>
      </div>

      {/* Opportunities List */}
      <motion.div
        className="glass rounded-lg p-6"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <h2 className="text-xl font-bold mb-4">Recent Classifications</h2>
        <div className="space-y-3">
          {opportunities.map((opp, index) => (
            <motion.div
              key={opp.id}
              className="glass rounded-lg p-4 hover:bg-white/5 transition-colors"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 + index * 0.1 }}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <h3 className="font-semibold">{opp.title}</h3>
                    <span className={`text-xs px-2 py-1 rounded ${getClassificationColor(opp.classification)}`}>
                      {opp.classification}
                    </span>
                  </div>
                  <div className="flex items-center space-x-4 text-sm text-slate-400">
                    <div className="flex items-center space-x-1">
                      <MapPin className="w-4 h-4" />
                      <span>{opp.location}</span>
                    </div>
                    <span>•</span>
                    <span>{opp.trade}</span>
                    <span>•</span>
                    <span>Confidence: {opp.confidence}%</span>
                  </div>
                </div>
                <div className="flex items-center">
                  {opp.classification === 'CONTESTABLE' && (
                    <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                  )}
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </div>
  )
}
