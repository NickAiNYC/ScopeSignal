import { NextRequest, NextResponse } from 'next/server'
import { spawn } from 'child_process'
import path from 'path'

/**
 * Geocoding API Endpoint
 * 
 * Converts NYC location strings, BINs, or BBLs to lat/lng coordinates.
 * Uses the Python geocoder service with caching.
 * 
 * GET /api/geocode?location=Brooklyn, NY
 * GET /api/geocode?bin=1234567
 * GET /api/geocode?bbl=3-12345-0001
 * 
 * POST /api/geocode/batch
 * Body: { locations: string[] }
 */
export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams
    const location = searchParams.get('location')
    const bin = searchParams.get('bin')
    const bbl = searchParams.get('bbl')

    if (!location && !bin && !bbl) {
      return NextResponse.json(
        { error: 'Missing required parameter: location, bin, or bbl' },
        { status: 400 }
      )
    }

    const coords = await geocodeLocation(location || bin || bbl || '', 
                                         bin ? 'bin' : bbl ? 'bbl' : 'location')
    
    if (!coords) {
      return NextResponse.json(
        { error: 'Could not geocode the provided location' },
        { status: 404 }
      )
    }

    return NextResponse.json({
      latitude: coords.latitude,
      longitude: coords.longitude,
      source: coords.source
    })
  } catch (error: any) {
    console.error('Geocoding error:', error)
    return NextResponse.json(
      { error: error.message || 'Internal server error' },
      { status: 500 }
    )
  }
}

/**
 * Batch geocoding endpoint
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { locations } = body

    if (!locations || !Array.isArray(locations)) {
      return NextResponse.json(
        { error: 'Missing or invalid locations array' },
        { status: 400 }
      )
    }

    const results = await Promise.all(
      locations.map(async (location: string) => {
        const coords = await geocodeLocation(location, 'location')
        return {
          location,
          ...coords
        }
      })
    )

    return NextResponse.json({ results })
  } catch (error: any) {
    console.error('Batch geocoding error:', error)
    return NextResponse.json(
      { error: error.message || 'Internal server error' },
      { status: 500 }
    )
  }
}

async function geocodeLocation(
  input: string, 
  type: 'location' | 'bin' | 'bbl'
): Promise<{ latitude: number; longitude: number; source: string } | null> {
  return new Promise((resolve, reject) => {
    const projectRoot = path.join(process.cwd())
    
    const inputData = JSON.stringify({
      input,
      type
    })

    const python = spawn('python', [
      '-c',
      `
import sys
import json
sys.path.insert(0, '.')
from packages.agents.opportunity.geocoder import NYCGeocoder

# Read input
input_data = json.loads(sys.stdin.read())

geocoder = NYCGeocoder()

if input_data['type'] == 'bin':
    coords = geocoder.geocode_bin(input_data['input'])
    source = 'BIN'
elif input_data['type'] == 'bbl':
    # Parse BBL format (borough-block-lot)
    parts = input_data['input'].split('-')
    if len(parts) == 3:
        coords = geocoder.geocode_bbl(parts[0], parts[1], parts[2])
    else:
        coords = None
    source = 'BBL'
else:
    coords = geocoder.geocode_address(input_data['input'])
    source = 'Address'

if coords:
    result = {
        'latitude': coords[0],
        'longitude': coords[1],
        'source': source
    }
    print(json.dumps(result))
else:
    print(json.dumps({'error': 'Could not geocode'}))
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
        if (result.error) {
          resolve(null)
        } else {
          resolve(result)
        }
      } catch (error) {
        reject(new Error(`Failed to parse Python output: ${stdout}`))
      }
    })

    python.on('error', (error) => {
      reject(new Error(`Failed to start Python process: ${error.message}`))
    })
  })
}
