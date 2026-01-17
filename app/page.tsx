'use client'

import { motion } from 'framer-motion'
import DashboardLayout from '@/components/layout/DashboardLayout'
import ModuleGrid from '@/components/layout/ModuleGrid'
import VoiceCommandButton from '@/components/voice/VoiceCommandButton'

export default function Home() {
  return (
    <DashboardLayout>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="space-y-8"
      >
        {/* Header Section */}
        <div className="text-center space-y-4">
          <motion.h1
            className="text-6xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-purple-500 to-pink-500"
            initial={{ scale: 0.9 }}
            animate={{ scale: 1 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            COMMAND CENTER 2026
          </motion.h1>
          <motion.p
            className="text-xl text-slate-400"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
          >
            Unified Intelligence Platform
          </motion.p>
        </div>

        {/* Module Grid */}
        <ModuleGrid />

        {/* Voice Command Button */}
        <VoiceCommandButton />

        {/* Status Bar */}
        <motion.div
          className="glass rounded-lg p-4 flex items-center justify-between"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
        >
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            <span className="text-sm text-slate-400">All Systems Operational</span>
          </div>
          <div className="text-sm text-slate-400">
            Real-time Data: <span className="text-green-400">Active</span>
          </div>
        </motion.div>
      </motion.div>
    </DashboardLayout>
  )
}
