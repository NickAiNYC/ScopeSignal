'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Activity, TrendingUp, TrendingDown } from 'lucide-react'

interface DataUpdate {
  id: string
  message: string
  timestamp: Date
  type: 'new' | 'update' | 'closed'
}

export default function RealtimeDataFeed() {
  const [updates, setUpdates] = useState<DataUpdate[]>([])
  const [isConnected, setIsConnected] = useState(true)

  useEffect(() => {
    // Simulate real-time updates
    const interval = setInterval(() => {
      const newUpdate: DataUpdate = {
        id: Math.random().toString(36).substring(7),
        message: getRandomUpdate(),
        timestamp: new Date(),
        type: ['new', 'update', 'closed'][Math.floor(Math.random() * 3)] as 'new' | 'update' | 'closed',
      }

      setUpdates((prev) => [newUpdate, ...prev].slice(0, 10))
    }, 5000)

    return () => clearInterval(interval)
  }, [])

  const getRandomUpdate = () => {
    const updates = [
      'New RFP posted - Bronx School Renovation',
      'Classification updated - Manhattan Housing Project',
      'Opportunity closed - Queens Infrastructure Work',
      'High confidence match - Brooklyn HVAC Installation',
      'Bid deadline approaching - Staten Island Project',
    ]
    return updates[Math.floor(Math.random() * updates.length)]
  }

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'new':
        return <TrendingUp className="w-4 h-4 text-green-400" />
      case 'closed':
        return <TrendingDown className="w-4 h-4 text-red-400" />
      default:
        return <Activity className="w-4 h-4 text-blue-400" />
    }
  }

  return (
    <div className="space-y-4">
      {/* Connection Status */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400 animate-pulse' : 'bg-red-400'}`} />
          <span className="text-sm text-slate-400">
            {isConnected ? 'Live Feed Active' : 'Disconnected'}
          </span>
        </div>
        <Activity className="w-5 h-5 text-slate-400" />
      </div>

      {/* Updates List */}
      <div className="space-y-2 max-h-[360px] overflow-y-auto">
        <AnimatePresence>
          {updates.map((update) => (
            <motion.div
              key={update.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              className="glass rounded-lg p-3 flex items-start space-x-3"
            >
              <div className="mt-1">{getTypeIcon(update.type)}</div>
              <div className="flex-1 min-w-0">
                <p className="text-sm text-slate-200">{update.message}</p>
                <p className="text-xs text-slate-400 mt-1">
                  {update.timestamp.toLocaleTimeString()}
                </p>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  )
}
