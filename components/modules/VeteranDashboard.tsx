'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Construction, CheckCircle, AlertTriangle, XCircle, Filter, TrendingUp, Map as MapIcon } from 'lucide-react'
import ProjectMap, { ProjectLocation } from './ProjectMap'

interface ProjectUpdate {
  id: string
  title: string
  agency: string
  classification: 'CLOSED' | 'SOFT_OPEN' | 'CONTESTABLE'
  confidence: number
  trade: string
  location: string
  latitude?: number
  longitude?: number
  feasibility_score: number
  can_bid: boolean
  compliance_readiness: {
    insurance: boolean
    license: boolean
  }
  blockers: string[]
  posted_date: string
}

export default function VeteranDashboard() {
  const [projects, setProjects] = useState<ProjectUpdate[]>([])
  const [filteredProjects, setFilteredProjects] = useState<ProjectUpdate[]>([])
  const [showMap, setShowMap] = useState(true)
  const [filters, setFilters] = useState({
    opportunityLevel: 'ALL',
    complianceReady: false,
    trade: 'ALL'
  })
  const [stats, setStats] = useState({
    total: 0,
    contestable: 0,
    softOpen: 0,
    closed: 0,
    compliant: 0
  })

  useEffect(() => {
    // Simulate loading project data
    // In production, this would fetch from API endpoints
    const mockProjects: ProjectUpdate[] = [
      {
        id: '1',
        title: 'SCA PS 123 HVAC System Upgrade',
        agency: 'SCA',
        classification: 'CONTESTABLE',
        confidence: 85,
        trade: 'HVAC',
        location: 'Brooklyn, NY',
        latitude: 40.6782,
        longitude: -73.9442,
        feasibility_score: 85.0,
        can_bid: true,
        compliance_readiness: {
          insurance: true,
          license: true
        },
        blockers: [],
        posted_date: '2026-02-05'
      },
      {
        id: '2',
        title: 'DDC Electrical Work - Amendment 3',
        agency: 'DDC',
        classification: 'SOFT_OPEN',
        confidence: 65,
        trade: 'Electrical',
        location: 'Manhattan, NY',
        latitude: 40.7831,
        longitude: -73.9712,
        feasibility_score: 39.0,
        can_bid: true,
        compliance_readiness: {
          insurance: true,
          license: true
        },
        blockers: [],
        posted_date: '2026-02-04'
      },
      {
        id: '3',
        title: 'HPD Housing Plumbing Modifications',
        agency: 'HPD',
        classification: 'CONTESTABLE',
        confidence: 78,
        trade: 'Plumbing',
        location: 'Queens, NY',
        latitude: 40.7282,
        longitude: -73.7949,
        feasibility_score: 15.6,
        can_bid: false,
        compliance_readiness: {
          insurance: false,
          license: true
        },
        blockers: ['Insurance: Insufficient limits: umbrella: need $2M, have $1M'],
        posted_date: '2026-02-05'
      },
      {
        id: '4',
        title: 'SCA School Renovation - Electrical Scope',
        agency: 'SCA',
        classification: 'CLOSED',
        confidence: 92,
        trade: 'Electrical',
        location: 'Bronx, NY',
        latitude: 40.8448,
        longitude: -73.8648,
        feasibility_score: 0.0,
        can_bid: false,
        compliance_readiness: {
          insurance: true,
          license: true
        },
        blockers: ['Opportunity is CLOSED or not trade-relevant'],
        posted_date: '2026-02-03'
      },
      {
        id: '5',
        title: 'DEP Water Treatment HVAC Update',
        agency: 'DEP',
        classification: 'SOFT_OPEN',
        confidence: 70,
        trade: 'HVAC',
        location: 'Staten Island, NY',
        latitude: 40.5795,
        longitude: -74.1502,
        feasibility_score: 42.0,
        can_bid: true,
        compliance_readiness: {
          insurance: true,
          license: true
        },
        blockers: [],
        posted_date: '2026-02-06'
      }
    ]

    setProjects(mockProjects)
    setFilteredProjects(mockProjects)
    
    // Calculate stats
    setStats({
      total: mockProjects.length,
      contestable: mockProjects.filter(p => p.classification === 'CONTESTABLE').length,
      softOpen: mockProjects.filter(p => p.classification === 'SOFT_OPEN').length,
      closed: mockProjects.filter(p => p.classification === 'CLOSED').length,
      compliant: mockProjects.filter(p => p.can_bid).length
    })
  }, [])

  useEffect(() => {
    // Apply filters
    let filtered = [...projects]

    if (filters.opportunityLevel !== 'ALL') {
      filtered = filtered.filter(p => p.classification === filters.opportunityLevel)
    }

    if (filters.complianceReady) {
      filtered = filtered.filter(p => p.can_bid)
    }

    if (filters.trade !== 'ALL') {
      filtered = filtered.filter(p => p.trade === filters.trade)
    }

    setFilteredProjects(filtered)
  }, [filters, projects])

  const getClassificationBadge = (classification: string) => {
    switch (classification) {
      case 'CONTESTABLE':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded text-xs font-medium bg-green-400/10 text-green-400">
            <CheckCircle className="w-3 h-3 mr-1" />
            CONTESTABLE
          </span>
        )
      case 'SOFT_OPEN':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded text-xs font-medium bg-yellow-400/10 text-yellow-400">
            <AlertTriangle className="w-3 h-3 mr-1" />
            SOFT OPEN
          </span>
        )
      case 'CLOSED':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded text-xs font-medium bg-red-400/10 text-red-400">
            <XCircle className="w-3 h-3 mr-1" />
            CLOSED
          </span>
        )
    }
  }

  const getComplianceIndicator = (project: ProjectUpdate) => {
    if (project.can_bid) {
      return (
        <div className="flex items-center text-green-400">
          <CheckCircle className="w-5 h-5 mr-2" />
          <span className="text-sm font-medium">Ready to Bid</span>
        </div>
      )
    } else {
      return (
        <div className="flex items-center text-red-400">
          <XCircle className="w-5 h-5 mr-2" />
          <span className="text-sm font-medium">Not Compliant</span>
        </div>
      )
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
            <h1 className="text-3xl font-bold">Veteran Dashboard</h1>
            <p className="text-slate-400">NYC Project Opportunities + Compliance Status</p>
          </div>
        </div>
      </motion.div>

      {/* Stats Grid */}
      <motion.div
        className="grid grid-cols-1 md:grid-cols-5 gap-4"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <div className="glass rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-slate-400">Total Updates</span>
            <TrendingUp className="w-4 h-4 text-blue-400" />
          </div>
          <div className="text-2xl font-bold">{stats.total}</div>
        </div>

        <div className="glass rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-slate-400">Contestable</span>
            <CheckCircle className="w-4 h-4 text-green-400" />
          </div>
          <div className="text-2xl font-bold text-green-400">{stats.contestable}</div>
        </div>

        <div className="glass rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-slate-400">Soft Open</span>
            <AlertTriangle className="w-4 h-4 text-yellow-400" />
          </div>
          <div className="text-2xl font-bold text-yellow-400">{stats.softOpen}</div>
        </div>

        <div className="glass rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-slate-400">Closed</span>
            <XCircle className="w-4 h-4 text-red-400" />
          </div>
          <div className="text-2xl font-bold text-red-400">{stats.closed}</div>
        </div>

        <div className="glass rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-slate-400">Bid Ready</span>
            <CheckCircle className="w-4 h-4 text-green-400" />
          </div>
          <div className="text-2xl font-bold text-green-400">{stats.compliant}</div>
        </div>
      </motion.div>

      {/* Filters */}
      <motion.div
        className="glass rounded-lg p-4"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <div className="flex items-center space-x-4">
          <Filter className="w-5 h-5 text-slate-400" />
          <span className="text-sm font-medium text-slate-400">Filters:</span>
          
          <select
            className="bg-slate-800 border border-slate-700 rounded px-3 py-1 text-sm"
            value={filters.opportunityLevel}
            onChange={(e) => setFilters({...filters, opportunityLevel: e.target.value})}
          >
            <option value="ALL">All Levels</option>
            <option value="CONTESTABLE">Contestable Only</option>
            <option value="SOFT_OPEN">Soft Open Only</option>
            <option value="CLOSED">Closed Only</option>
          </select>

          <select
            className="bg-slate-800 border border-slate-700 rounded px-3 py-1 text-sm"
            value={filters.trade}
            onChange={(e) => setFilters({...filters, trade: e.target.value})}
          >
            <option value="ALL">All Trades</option>
            <option value="Electrical">Electrical</option>
            <option value="HVAC">HVAC</option>
            <option value="Plumbing">Plumbing</option>
          </select>

          <label className="flex items-center space-x-2 text-sm">
            <input
              type="checkbox"
              className="rounded"
              checked={filters.complianceReady}
              onChange={(e) => setFilters({...filters, complianceReady: e.target.checked})}
            />
            <span>Show Only Compliant</span>
          </label>

          <label className="flex items-center space-x-2 text-sm ml-4">
            <input
              type="checkbox"
              className="rounded"
              checked={showMap}
              onChange={(e) => setShowMap(e.target.checked)}
            />
            <span className="flex items-center gap-1">
              <MapIcon className="w-4 h-4" />
              Show Map
            </span>
          </label>

          <span className="text-sm text-slate-400 ml-auto">
            Showing {filteredProjects.length} of {projects.length} projects
          </span>
        </div>
      </motion.div>

      {/* NYC Opportunity Heat Map */}
      {showMap && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <ProjectMap 
            projects={filteredProjects.filter(p => p.latitude && p.longitude).map(p => ({
              id: p.id,
              title: p.title,
              classification: p.classification,
              trade: p.trade as 'Electrical' | 'HVAC' | 'Plumbing',
              latitude: p.latitude!,
              longitude: p.longitude!,
              feasibility_score: p.feasibility_score,
              confidence: p.confidence,
              agency: p.agency,
              location: p.location,
              posted_date: p.posted_date,
              can_bid: p.can_bid
            }))}
          />
        </motion.div>
      )}

      {/* Projects List */}
      <motion.div
        className="space-y-3"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: showMap ? 0.4 : 0.3 }}
      >
        {filteredProjects.map((project, index) => (
          <motion.div
            key={project.id}
            className="glass rounded-lg p-5 hover:bg-white/5 transition-colors"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 + index * 0.05 }}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-3 mb-3">
                  <h3 className="text-lg font-semibold">{project.title}</h3>
                  {getClassificationBadge(project.classification)}
                  <span className="text-xs px-2 py-1 rounded bg-blue-400/10 text-blue-400">
                    {project.agency}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-4 mb-3">
                  <div>
                    <p className="text-sm text-slate-400">Trade</p>
                    <p className="text-sm font-medium">{project.trade}</p>
                  </div>
                  <div>
                    <p className="text-sm text-slate-400">Location</p>
                    <p className="text-sm font-medium">{project.location}</p>
                  </div>
                  <div>
                    <p className="text-sm text-slate-400">Confidence</p>
                    <p className="text-sm font-medium">{project.confidence}%</p>
                  </div>
                  <div>
                    <p className="text-sm text-slate-400">Feasibility Score</p>
                    <p className="text-sm font-medium">{project.feasibility_score}</p>
                  </div>
                </div>

                <div className="flex items-center space-x-4 mb-2">
                  {getComplianceIndicator(project)}
                  
                  <div className="flex items-center space-x-2 text-sm">
                    <span className={project.compliance_readiness.insurance ? 'text-green-400' : 'text-red-400'}>
                      {project.compliance_readiness.insurance ? '✓' : '✗'} Insurance
                    </span>
                    <span className={project.compliance_readiness.license ? 'text-green-400' : 'text-red-400'}>
                      {project.compliance_readiness.license ? '✓' : '✗'} License
                    </span>
                  </div>
                </div>

                {project.blockers.length > 0 && (
                  <div className="mt-2 p-2 bg-red-400/10 rounded text-sm text-red-400">
                    <strong>Blockers:</strong> {project.blockers.join('; ')}
                  </div>
                )}
              </div>

              <div className="ml-4 text-right">
                <p className="text-xs text-slate-500">{project.posted_date}</p>
                {project.can_bid && project.classification === 'CONTESTABLE' && (
                  <div className="mt-2">
                    <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse mx-auto" />
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        ))}

        {filteredProjects.length === 0 && (
          <div className="glass rounded-lg p-12 text-center">
            <p className="text-slate-400">No projects match your filters</p>
          </div>
        )}
      </motion.div>
    </div>
  )
}
