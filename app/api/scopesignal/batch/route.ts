import { NextRequest, NextResponse } from 'next/server'
import { spawn } from 'child_process'
import path from 'path'
import fs from 'fs'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { updates } = body

    if (!updates || !Array.isArray(updates)) {
      return NextResponse.json(
        { error: 'Missing or invalid updates array' },
        { status: 400 }
      )
    }

    // Create a temporary file for batch processing
    const timestamp = Date.now()
    const tempFile = path.join('/tmp', `batch-${timestamp}.json`)
    fs.writeFileSync(tempFile, JSON.stringify(updates))

    try {
      const result = await processBatch(tempFile)
      return NextResponse.json(result)
    } finally {
      // Clean up temp file
      if (fs.existsSync(tempFile)) {
        fs.unlinkSync(tempFile)
      }
    }
  } catch (error: any) {
    console.error('Batch processing error:', error)
    return NextResponse.json(
      { error: error.message || 'Internal server error' },
      { status: 500 }
    )
  }
}

function processBatch(inputFile: string): Promise<any> {
  return new Promise((resolve, reject) => {
    const projectRoot = path.join(process.cwd())
    const timestamp = Date.now()
    const outputFile = path.join('/tmp', `output-${timestamp}.json`)

    const python = spawn('python', [
      '-m',
      'cli',
      'batch',
      inputFile,
      '--output',
      outputFile,
    ], {
      cwd: projectRoot,
      env: { ...process.env }
    })

    let stderr = ''

    python.stderr.on('data', (data) => {
      stderr += data.toString()
    })

    python.on('close', (code) => {
      if (code !== 0) {
        reject(new Error(`Python process exited with code ${code}: ${stderr}`))
        return
      }

      try {
        if (fs.existsSync(outputFile)) {
          const result = JSON.parse(fs.readFileSync(outputFile, 'utf-8'))
          fs.unlinkSync(outputFile)
          resolve(result)
        } else {
          reject(new Error('Output file not created'))
        }
      } catch (error: any) {
        reject(new Error(`Failed to read output: ${error.message}`))
      }
    })

    python.on('error', (error) => {
      reject(new Error(`Failed to start Python process: ${error.message}`))
    })
  })
}
