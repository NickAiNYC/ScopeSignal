'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Heart, DollarSign, TrendingUp, Users } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

export default function RegulaDashboard() {
  const [stats] = useState({
    totalRevenue: 2450000,
    recovered: 890000,
    inProgress: 450000,
    pending: 1110000,
  })

  const chartData = [
    { month: 'Jan', revenue: 65000 },
    { month: 'Feb', revenue: 82000 },
    { month: 'Mar', revenue: 75000 },
    { month: 'Apr', revenue: 95000 },
    { month: 'May', revenue: 110000 },
    { month: 'Jun', revenue: 128000 },
  ]

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
    }).format(value)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center space-x-4"
      >
        <div className="w-12 h-12 gradient-regula rounded-lg flex items-center justify-center">
          <Heart className="w-6 h-6 text-white" />
        </div>
        <div>
          <h1 className="text-3xl font-bold">Regula</h1>
          <p className="text-slate-400">Healthcare Revenue Recovery Dashboard</p>
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
            <span className="text-sm text-slate-400">Total Revenue at Risk</span>
            <DollarSign className="w-4 h-4 text-blue-400" />
          </div>
          <div className="text-2xl font-bold">{formatCurrency(stats.totalRevenue)}</div>
        </div>

        <div className="glass rounded-lg p-4 pulse-glow border-green-500/30">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-slate-400">Recovered</span>
            <TrendingUp className="w-4 h-4 text-green-400" />
          </div>
          <div className="text-2xl font-bold text-green-400">{formatCurrency(stats.recovered)}</div>
        </div>

        <div className="glass rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-slate-400">In Progress</span>
            <Users className="w-4 h-4 text-yellow-400" />
          </div>
          <div className="text-2xl font-bold text-yellow-400">{formatCurrency(stats.inProgress)}</div>
        </div>

        <div className="glass rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-slate-400">Pending</span>
            <DollarSign className="w-4 h-4 text-pink-400" />
          </div>
          <div className="text-2xl font-bold text-pink-400">{formatCurrency(stats.pending)}</div>
        </div>
      </motion.div>

      {/* Chart */}
      <motion.div
        className="glass rounded-lg p-6"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <h2 className="text-xl font-bold mb-4">Monthly Recovery Trend</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="month" stroke="#94a3b8" />
            <YAxis stroke="#94a3b8" />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#1e293b', 
                border: '1px solid #334155',
                borderRadius: '8px'
              }}
              formatter={(value: any) => formatCurrency(value)}
            />
            <Line type="monotone" dataKey="revenue" stroke="#f472b6" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </motion.div>

      {/* Revenue Leaks */}
      <motion.div
        className="glass rounded-lg p-6"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <h2 className="text-xl font-bold mb-4">Top Revenue Leak Sources</h2>
        <div className="space-y-3">
          {[
            { id: 1, source: 'Claim Denials', amount: 450000, percentage: 38 },
            { id: 2, source: 'Underpayments', amount: 320000, percentage: 27 },
            { id: 3, source: 'Coding Errors', amount: 280000, percentage: 24 },
          ].map((leak, index) => (
            <motion.div
              key={leak.id}
              className="glass rounded-lg p-4 hover:bg-white/5 transition-colors"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 + index * 0.1 }}
            >
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-semibold">{leak.source}</h3>
                <span className="text-pink-400 font-bold">{formatCurrency(leak.amount)}</span>
              </div>
              <div className="w-full bg-slate-700 rounded-full h-2">
                <div 
                  className="bg-pink-500 h-2 rounded-full"
                  style={{ width: `${leak.percentage}%` }}
                />
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </div>
  )
}
