'use client'

import { motion } from 'framer-motion'
import DashboardLayout from '@/components/layout/DashboardLayout'
import RegulaDashboard from '@/components/modules/RegulaDashboard'

export default function RegulaPage() {
  return (
    <DashboardLayout>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <RegulaDashboard />
      </motion.div>
    </DashboardLayout>
  )
}
