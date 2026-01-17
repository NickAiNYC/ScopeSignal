'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { Shield, Heart, Brain, Construction, ArrowRight } from 'lucide-react'

const modules = [
  {
    name: 'ViolationSentinel',
    path: '/violation-sentinel',
    icon: Shield,
    gradient: 'gradient-violation',
    description: 'Compliance Enforcement Dashboard',
    color: 'text-purple-400',
  },
  {
    name: 'Regula',
    path: '/regula',
    icon: Heart,
    gradient: 'gradient-regula',
    description: 'Healthcare Revenue Recovery Dashboard',
    color: 'text-pink-400',
  },
  {
    name: 'AI-PulsePoint',
    path: '/ai-pulsepoint',
    icon: Brain,
    gradient: 'gradient-aipulsepoint',
    description: 'AI Model Intelligence Dashboard',
    color: 'text-cyan-400',
  },
  {
    name: 'ScopeSignal',
    path: '/scopesignal',
    icon: Construction,
    gradient: 'gradient-scopesignal',
    description: 'Construction Opportunity Radar',
    color: 'text-green-400',
  },
]

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
}

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 },
}

export default function ModuleGrid() {
  return (
    <motion.div
      className="grid grid-cols-1 md:grid-cols-2 gap-6"
      variants={container}
      initial="hidden"
      animate="show"
    >
      {modules.map((module) => {
        const Icon = module.icon
        
        return (
          <motion.div
            key={module.path}
            variants={item}
            whileHover={{ scale: 1.02, y: -5 }}
            whileTap={{ scale: 0.98 }}
          >
            <Link href={module.path}>
              <div className={`${module.gradient} rounded-xl p-6 h-full min-h-[200px] flex flex-col justify-between relative overflow-hidden group`}>
                {/* Background Pattern */}
                <div className="absolute inset-0 opacity-10">
                  <div className="absolute inset-0" style={{
                    backgroundImage: 'radial-gradient(circle at 2px 2px, white 1px, transparent 0)',
                    backgroundSize: '40px 40px',
                  }} />
                </div>

                {/* Content */}
                <div className="relative z-10">
                  <div className="flex items-start justify-between mb-4">
                    <Icon className="w-12 h-12 text-white" />
                    <motion.div
                      className="opacity-0 group-hover:opacity-100 transition-opacity"
                      initial={{ x: -10 }}
                      whileHover={{ x: 0 }}
                    >
                      <ArrowRight className="w-6 h-6 text-white" />
                    </motion.div>
                  </div>
                  
                  <h3 className="text-2xl font-bold text-white mb-2">
                    {module.name}
                  </h3>
                  
                  <p className="text-white/80 text-sm">
                    {module.description}
                  </p>
                </div>

                {/* Status Indicator */}
                <div className="relative z-10 flex items-center space-x-2 mt-4">
                  <div className="w-2 h-2 bg-white rounded-full animate-pulse" />
                  <span className="text-white/70 text-xs">Active</span>
                </div>
              </div>
            </Link>
          </motion.div>
        )
      })}
    </motion.div>
  )
}
