'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Brain, Zap, Activity, AlertCircle } from 'lucide-react'
import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ResponsiveContainer } from 'recharts'

export default function AIPulsePointDashboard() {
  const [stats] = useState({
    totalModels: 24,
    anomalies: 3,
    accuracy: 98.5,
    activeMonitoring: 18,
  })

  const radarData = [
    { metric: 'Accuracy', value: 98 },
    { metric: 'Speed', value: 85 },
    { metric: 'Reliability', value: 92 },
    { metric: 'Efficiency', value: 88 },
    { metric: 'Scalability', value: 90 },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center space-x-4"
      >
        <div className="w-12 h-12 gradient-aipulsepoint rounded-lg flex items-center justify-center">
          <Brain className="w-6 h-6 text-white" />
        </div>
        <div>
          <h1 className="text-3xl font-bold">AI-PulsePoint</h1>
          <p className="text-slate-400">AI Model Intelligence Dashboard</p>
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
            <span className="text-sm text-slate-400">Total Models</span>
            <Brain className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-bold">{stats.totalModels}</div>
        </div>

        <div className="glass rounded-lg p-4 pulse-glow border-red-500/30">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-slate-400">Anomalies Detected</span>
            <AlertCircle className="w-4 h-4 text-red-400" />
          </div>
          <div className="text-2xl font-bold text-red-400">{stats.anomalies}</div>
        </div>

        <div className="glass rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-slate-400">Avg Accuracy</span>
            <Zap className="w-4 h-4 text-green-400" />
          </div>
          <div className="text-2xl font-bold text-green-400">{stats.accuracy}%</div>
        </div>

        <div className="glass rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-slate-400">Active Monitoring</span>
            <Activity className="w-4 h-4 text-blue-400" />
          </div>
          <div className="text-2xl font-bold text-blue-400">{stats.activeMonitoring}</div>
        </div>
      </motion.div>

      {/* Radar Chart */}
      <motion.div
        className="glass rounded-lg p-6"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <h2 className="text-xl font-bold mb-4">Model Performance Metrics</h2>
        <ResponsiveContainer width="100%" height={400}>
          <RadarChart data={radarData}>
            <PolarGrid stroke="#334155" />
            <PolarAngleAxis dataKey="metric" stroke="#94a3b8" />
            <PolarRadiusAxis stroke="#94a3b8" />
            <Radar 
              name="Performance" 
              dataKey="value" 
              stroke="#06b6d4" 
              fill="#06b6d4" 
              fillOpacity={0.6} 
            />
          </RadarChart>
        </ResponsiveContainer>
      </motion.div>

      {/* Model Status */}
      <motion.div
        className="glass rounded-lg p-6"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <h2 className="text-xl font-bold mb-4">Active AI Models</h2>
        <div className="space-y-3">
          {[
            { id: 1, name: 'Classification Model v3.2', status: 'healthy', accuracy: 98.2 },
            { id: 2, name: 'Anomaly Detection v2.1', status: 'warning', accuracy: 94.5 },
            { id: 3, name: 'Prediction Engine v4.0', status: 'healthy', accuracy: 99.1 },
          ].map((model, index) => (
            <motion.div
              key={model.id}
              className="glass rounded-lg p-4 hover:bg-white/5 transition-colors"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 + index * 0.1 }}
            >
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-semibold">{model.name}</h3>
                  <p className="text-sm text-slate-400">Accuracy: {model.accuracy}%</p>
                </div>
                <div className="flex items-center space-x-2">
                  <div className={`w-2 h-2 rounded-full ${
                    model.status === 'healthy' ? 'bg-green-400 animate-pulse' : 'bg-yellow-400 animate-pulse'
                  }`} />
                  <span className={`text-xs px-2 py-1 rounded ${
                    model.status === 'healthy' ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'
                  }`}>
                    {model.status.toUpperCase()}
                  </span>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </div>
  )
}
