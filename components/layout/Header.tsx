'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Shield, Heart, Brain, Construction } from 'lucide-react'

const modules = [
  { name: 'ViolationSentinel', path: '/violation-sentinel', icon: Shield, color: 'text-purple-400' },
  { name: 'Regula', path: '/regula', icon: Heart, color: 'text-pink-400' },
  { name: 'AI-PulsePoint', path: '/ai-pulsepoint', icon: Brain, color: 'text-cyan-400' },
  { name: 'ScopeSignal', path: '/scopesignal', icon: Construction, color: 'text-green-400' },
]

export default function Header() {
  const pathname = usePathname()

  return (
    <motion.header
      className="glass border-b border-slate-800"
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <Link href="/">
            <motion.div
              className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-600"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              COMMAND CENTER
            </motion.div>
          </Link>

          {/* Navigation */}
          <nav className="flex items-center space-x-6">
            {modules.map((module) => {
              const Icon = module.icon
              const isActive = pathname === module.path
              
              return (
                <Link key={module.path} href={module.path}>
                  <motion.div
                    className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all ${
                      isActive 
                        ? 'bg-white/10 backdrop-blur-md' 
                        : 'hover:bg-white/5'
                    }`}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    <Icon className={`w-5 h-5 ${module.color}`} />
                    <span className="text-sm font-medium">{module.name}</span>
                  </motion.div>
                </Link>
              )
            })}
          </nav>
        </div>
      </div>
    </motion.header>
  )
}
