'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Shield, AlertTriangle, CheckCircle, TrendingUp } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

export default function ViolationSentinelDashboard() {
  const [stats, setStats] = useState({
    totalViolations: 234,
    critical: 12,
    resolved: 189,
    pending: 33,
  })

  const chartData = [
    { name: 'Mon', violations: 12 },
    { name: 'Tue', violations: 19 },
    { name: 'Wed', violations: 8 },
    { name: 'Thu', violations: 15 },
    { name: 'Fri', violations: 22 },
    { name: 'Sat', violations: 7 },
    { name: 'Sun', violations: 5 },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center space-x-4"
      >
        <div className="w-12 h-12 gradient-violation rounded-lg flex items-center justify-center">
          <Shield className="w-6 h-6 text-white" />
        </div>
        <div>
          <h1 className="text-3xl font-bold">ViolationSentinel</h1>
          <p className="text-slate-400">Compliance Enforcement Dashboard</p>
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
            <span className="text-sm text-slate-400">Total Violations</span>
            <TrendingUp className="w-4 h-4 text-blue-400" />
          </div>
          <div className="text-2xl font-bold">{stats.totalViolations}</div>
        </div>

        <div className="glass rounded-lg p-4 pulse-glow border-red-500/30">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-slate-400">Critical</span>
            <AlertTriangle className="w-4 h-4 text-red-400" />
          </div>
          <div className="text-2xl font-bold text-red-400">{stats.critical}</div>
        </div>

        <div className="glass rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-slate-400">Resolved</span>
            <CheckCircle className="w-4 h-4 text-green-400" />
          </div>
          <div className="text-2xl font-bold text-green-400">{stats.resolved}</div>
        </div>

        <div className="glass rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-slate-400">Pending</span>
            <AlertTriangle className="w-4 h-4 text-yellow-400" />
          </div>
          <div className="text-2xl font-bold text-yellow-400">{stats.pending}</div>
        </div>
      </motion.div>

      {/* Chart */}
      <motion.div
        className="glass rounded-lg p-6"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <h2 className="text-xl font-bold mb-4">Weekly Violations Trend</h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="name" stroke="#94a3b8" />
            <YAxis stroke="#94a3b8" />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#1e293b', 
                border: '1px solid #334155',
                borderRadius: '8px'
              }}
            />
            <Bar dataKey="violations" fill="#8b5cf6" />
          </BarChart>
        </ResponsiveContainer>
      </motion.div>

      {/* Recent Violations */}
      <motion.div
        className="glass rounded-lg p-6"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <h2 className="text-xl font-bold mb-4">Recent Violations</h2>
        <div className="space-y-3">
          {[
            { id: 1, type: 'Safety', severity: 'critical', location: 'Building A' },
            { id: 2, type: 'Environmental', severity: 'high', location: 'Facility 12' },
            { id: 3, type: 'Data Privacy', severity: 'medium', location: 'Server Room' },
          ].map((violation, index) => (
            <motion.div
              key={violation.id}
              className="glass rounded-lg p-4 hover:bg-white/5 transition-colors"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 + index * 0.1 }}
            >
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-semibold">{violation.type} Violation</h3>
                  <p className="text-sm text-slate-400">{violation.location}</p>
                </div>
                <span className={`text-xs px-2 py-1 rounded ${
                  violation.severity === 'critical' ? 'bg-red-500/20 text-red-400' :
                  violation.severity === 'high' ? 'bg-orange-500/20 text-orange-400' :
                  'bg-yellow-500/20 text-yellow-400'
                }`}>
                  {violation.severity.toUpperCase()}
                </span>
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </div>
  )
}
