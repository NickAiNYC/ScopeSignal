'use client'

import { motion } from 'framer-motion'
import DashboardLayout from '@/components/layout/DashboardLayout'
import ScopeSignalDashboard from '@/components/modules/ScopeSignalDashboard'

export default function ScopeSignalPage() {
  return (
    <DashboardLayout>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <ScopeSignalDashboard />
      </motion.div>
    </DashboardLayout>
  )
}
