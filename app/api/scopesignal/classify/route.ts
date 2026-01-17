import { NextRequest, NextResponse } from 'next/server'
import { spawn } from 'child_process'
import path from 'path'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { update_text, trade } = body

    if (!update_text || !trade) {
      return NextResponse.json(
        { error: 'Missing required fields: update_text and trade' },
        { status: 400 }
      )
    }

    // Call the Python classifier
    const result = await classifyUpdate(update_text, trade)
    
    return NextResponse.json(result)
  } catch (error: any) {
    console.error('Classification error:', error)
    return NextResponse.json(
      { error: error.message || 'Internal server error' },
      { status: 500 }
    )
  }
}

function classifyUpdate(updateText: string, trade: string): Promise<any> {
  return new Promise((resolve, reject) => {
    const projectRoot = path.join(process.cwd())
    
    // Call the Python CLI
    const python = spawn('python', [
      '-m',
      'cli',
      'classify',
      updateText,
      '--trade',
      trade,
      '--json'
    ], {
      cwd: projectRoot,
      env: { ...process.env }
    })

    let stdout = ''
    let stderr = ''

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
