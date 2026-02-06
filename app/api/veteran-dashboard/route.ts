import { NextRequest, NextResponse } from 'next/server'
import { spawn } from 'child_process'
import path from 'path'

/**
 * Veteran Dashboard API Endpoint
 * 
 * Fetches and processes NYC project updates with full feasibility scoring.
 * Returns projects filtered and enhanced with compliance readiness indicators.
 * 
 * GET /api/veteran-dashboard?trade=Electrical&opportunityLevel=CONTESTABLE&complianceReady=true
 * 
 * Query Parameters:
 * - trade: "Electrical" | "HVAC" | "Plumbing" | "ALL" (optional)
 * - opportunityLevel: "CLOSED" | "SOFT_OPEN" | "CONTESTABLE" | "ALL" (optional)
 * - complianceReady: boolean (optional)
 */
export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams
    const trade = searchParams.get('trade') || 'ALL'
    const opportunityLevel = searchParams.get('opportunityLevel') || 'ALL'
    const complianceReady = searchParams.get('complianceReady') === 'true'

    // In production, this would fetch user's actual insurance and license data
    // For now, use mock data
    const mockUserData = {
      insurance: {
        general_liability: 2.0,
        auto_liability: 1.0,
        umbrella: 5.0,
        workers_comp: 1.0
      },
      licenses: [
        {
          type: 'Master Electrician',
          number: 'ME123456',
          status: 'active',
          expiry: '2027-12-31'
        },
        {
          type: 'HVAC License',
          number: 'HVAC789',
          status: 'active',
          expiry: '2027-06-30'
        },
        {
          type: 'Master Plumber',
          number: 'MP456789',
          status: 'active',
          expiry: '2027-09-30'
        }
      ]
    }

    // Fetch projects (in production, this would query a database)
    const projects = await getProjectsWithFeasibility(
      mockUserData.insurance,
      mockUserData.licenses,
      trade,
      opportunityLevel,
      complianceReady
    )
    
    return NextResponse.json({
      projects,
      filters: {
        trade,
        opportunityLevel,
        complianceReady
      }
    })
  } catch (error: any) {
    console.error('Veteran dashboard error:', error)
    return NextResponse.json(
      { error: error.message || 'Internal server error' },
      { status: 500 }
    )
  }
}

/**
 * POST endpoint to process batch opportunities with user data
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { opportunities, user_insurance, user_licenses } = body

    if (!opportunities || !user_insurance || !user_licenses) {
      return NextResponse.json(
        { error: 'Missing required fields: opportunities, user_insurance, user_licenses' },
        { status: 400 }
      )
    }

    const results = await processBatchFeasibility(
      opportunities,
      user_insurance,
      user_licenses
    )
    
    return NextResponse.json({ results })
  } catch (error: any) {
    console.error('Batch feasibility error:', error)
    return NextResponse.json(
      { error: error.message || 'Internal server error' },
      { status: 500 }
    )
  }
}

async function getProjectsWithFeasibility(
  userInsurance: any,
  userLicenses: any[],
  trade: string,
  opportunityLevel: string,
  complianceReady: boolean
): Promise<any[]> {
  return new Promise((resolve, reject) => {
    const projectRoot = path.join(process.cwd())
    
    const inputData = JSON.stringify({
      user_insurance: userInsurance,
      user_licenses: userLicenses,
      filters: {
        trade,
        opportunity_level: opportunityLevel,
        compliance_ready: complianceReady
      }
    })

    const python = spawn('python', [
      '-c',
      `
import sys
import json
from datetime import datetime, timedelta
sys.path.insert(0, '.')
from packages.compliance import FeasibilityScorer

# Read input
input_data = json.loads(sys.stdin.read())

# Mock project data (in production, fetch from database)
mock_projects = [
    {
        "id": "1",
        "title": "SCA PS 123 HVAC System Upgrade",
        "agency": "SCA",
        "classification": "CONTESTABLE",
        "confidence": 85,
        "trade_relevant": True,
        "_metadata": {"trade": "HVAC"},
        "location": "Brooklyn, NY",
        "posted_date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    },
    {
        "id": "2",
        "title": "DDC Electrical Work - Amendment 3",
        "agency": "DDC",
        "classification": "SOFT_OPEN",
        "confidence": 65,
        "trade_relevant": True,
        "_metadata": {"trade": "Electrical"},
        "location": "Manhattan, NY",
        "posted_date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
    },
    {
        "id": "3",
        "title": "HPD Housing Plumbing Modifications",
        "agency": "HPD",
        "classification": "CONTESTABLE",
        "confidence": 78,
        "trade_relevant": True,
        "_metadata": {"trade": "Plumbing"},
        "location": "Queens, NY",
        "posted_date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    },
    {
        "id": "4",
        "title": "SCA School Renovation - Electrical Scope",
        "agency": "SCA",
        "classification": "CLOSED",
        "confidence": 92,
        "trade_relevant": False,
        "_metadata": {"trade": "Electrical"},
        "location": "Bronx, NY",
        "posted_date": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
    },
    {
        "id": "5",
        "title": "DEP Water Treatment HVAC Update",
        "agency": "DEP",
        "classification": "SOFT_OPEN",
        "confidence": 70,
        "trade_relevant": True,
        "_metadata": {"trade": "HVAC"},
        "location": "Staten Island, NY",
        "posted_date": datetime.now().strftime("%Y-%m-%d")
    }
]

# Calculate feasibility for each project
scorer = FeasibilityScorer()
results = []

for project in mock_projects:
    feasibility = scorer.calculate_feasibility(
        project,
        input_data['user_insurance'],
        input_data['user_licenses'],
        project['agency']
    )
    
    # Combine project and feasibility data
    result = {
        "id": project["id"],
        "title": project["title"],
        "agency": project["agency"],
        "classification": project["classification"],
        "confidence": project["confidence"],
        "trade": project["_metadata"]["trade"],
        "location": project["location"],
        "posted_date": project["posted_date"],
        "feasibility_score": feasibility["feasibility_score"],
        "can_bid": feasibility["can_bid"],
        "compliance_readiness": feasibility["compliance_readiness"],
        "blockers": feasibility["blockers"]
    }
    
    # Apply filters
    filters = input_data['filters']
    
    if filters['trade'] != 'ALL' and result['trade'] != filters['trade']:
        continue
    
    if filters['opportunity_level'] != 'ALL' and result['classification'] != filters['opportunity_level']:
        continue
    
    if filters['compliance_ready'] and not result['can_bid']:
        continue
    
    results.append(result)

print(json.dumps(results))
      `
    ], {
      cwd: projectRoot,
      env: { ...process.env }
    })

    let stdout = ''
    let stderr = ''

    python.stdin.write(inputData)
    python.stdin.end()

    python.stdout.on('data', (data) => {
      stdout += data.toString()
    })

    python.stderr.on('data', (data) => {
      stderr += data.toString()
    })

    python.on('close', (code) => {
      if (code !== 0) {
        reject(new Error(`Python process exited with code ${code}: ${stderr}`))
        return
      }

      try {
        const result = JSON.parse(stdout)
        resolve(result)
      } catch (error) {
        reject(new Error(`Failed to parse Python output: ${stdout}`))
      }
    })

    python.on('error', (error) => {
      reject(new Error(`Failed to start Python process: ${error.message}`))
    })
  })
}

async function processBatchFeasibility(
  opportunities: any[],
  userInsurance: any,
  userLicenses: any[]
): Promise<any[]> {
  // Similar to getProjectsWithFeasibility but for batch processing
  // Implementation would be similar but process provided opportunities
  return []
}
