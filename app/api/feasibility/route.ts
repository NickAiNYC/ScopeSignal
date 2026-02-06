import { NextRequest, NextResponse } from 'next/server'
import { spawn } from 'child_process'
import path from 'path'

/**
 * Feasibility Check API Endpoint
 * 
 * Combines opportunity classification with compliance checks to produce
 * a feasibility score indicating whether a user can bid on an opportunity.
 * 
 * POST /api/feasibility
 * Body: {
 *   update_text: string,
 *   trade: "Electrical" | "HVAC" | "Plumbing",
 *   agency: string (e.g., "SCA", "DDC"),
 *   user_insurance: { general_liability: number, auto_liability: number, ... },
 *   user_licenses: [{ type: string, status: string, expiry: string, ... }]
 * }
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { update_text, trade, agency, user_insurance, user_licenses } = body

    // Validate required fields
    if (!update_text || !trade || !agency) {
      return NextResponse.json(
        { error: 'Missing required fields: update_text, trade, and agency' },
        { status: 400 }
      )
    }

    if (!user_insurance || !user_licenses) {
      return NextResponse.json(
        { error: 'Missing user compliance data: user_insurance and user_licenses' },
        { status: 400 }
      )
    }

    // Call the Python feasibility checker
    const result = await checkFeasibility(
      update_text,
      trade,
      agency,
      user_insurance,
      user_licenses
    )
    
    return NextResponse.json(result)
  } catch (error: any) {
    console.error('Feasibility check error:', error)
    return NextResponse.json(
      { error: error.message || 'Internal server error' },
      { status: 500 }
    )
  }
}

function checkFeasibility(
  updateText: string,
  trade: string,
  agency: string,
  userInsurance: any,
  userLicenses: any[]
): Promise<any> {
  return new Promise((resolve, reject) => {
    const projectRoot = path.join(process.cwd())
    
    // Prepare input data as JSON
    const inputData = JSON.stringify({
      update_text: updateText,
      trade: trade,
      agency: agency,
      user_insurance: userInsurance,
      user_licenses: userLicenses
    })

    // Call Python script to check feasibility
    const python = spawn('python', [
      '-c',
      `
import sys
import json
sys.path.insert(0, '.')
from packages.agents.opportunity import classify_opportunity
from packages.compliance import check_feasibility

# Read input
input_data = json.loads(sys.stdin.read())

# Step 1: Classify opportunity
classification, _ = classify_opportunity(
    input_data['update_text'],
    input_data['trade'],
    with_proof=True,
    agency=input_data['agency']
)

# Step 2: Check feasibility
feasibility = check_feasibility(
    classification,
    input_data['user_insurance'],
    input_data['user_licenses'],
    input_data['agency']
)

# Output combined result
result = {
    'classification': classification,
    'feasibility': feasibility
}
print(json.dumps(result))
      `
    ], {
      cwd: projectRoot,
      env: { ...process.env }
    })

    let stdout = ''
    let stderr = ''

    // Send input data to Python
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
