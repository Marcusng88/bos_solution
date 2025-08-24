import { NextRequest, NextResponse } from 'next/server'
import { promises as fs } from 'fs'
import path from 'path'

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const fileName = searchParams.get('file')
    
    if (!fileName) {
      return NextResponse.json({ error: 'File name is required' }, { status: 400 })
    }
    
    // Security check: only allow specific file types and prevent directory traversal
    const allowedExtensions = ['.txt', '.html', '.pdf', '.json']
    const fileExt = path.extname(fileName).toLowerCase()
    
    if (!allowedExtensions.includes(fileExt)) {
      return NextResponse.json({ error: 'Invalid file type' }, { status: 400 })
    }
    
    // Prevent directory traversal attacks
    if (fileName.includes('..') || fileName.includes('/') || fileName.includes('\\')) {
      return NextResponse.json({ error: 'Invalid file path' }, { status: 400 })
    }
    
    // Construct the file path - assuming files are generated in the backend directory
    // You may need to adjust this path based on your setup
    const backendDir = path.join(process.cwd(), '..', 'backend')
    const filePath = path.join(backendDir, fileName)
    
    // Check if file exists
    try {
      await fs.access(filePath)
    } catch {
      return NextResponse.json({ error: 'File not found' }, { status: 404 })
    }
    
    // Read the file
    const fileBuffer = await fs.readFile(filePath)
    
    // Determine content type based on file extension
    let contentType = 'application/octet-stream'
    switch (fileExt) {
      case '.txt':
        contentType = 'text/plain'
        break
      case '.html':
        contentType = 'text/html'
        break
      case '.pdf':
        contentType = 'application/pdf'
        break
      case '.json':
        contentType = 'application/json'
        break
    }
    
    // Return the file as a download
    return new NextResponse(fileBuffer, {
      headers: {
        'Content-Type': contentType,
        'Content-Disposition': `attachment; filename="${fileName}"`,
      },
    })
    
  } catch (error) {
    console.error('Download error:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}
