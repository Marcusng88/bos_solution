import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  try {
    // Get the X-User-ID header from the request
    const userId = request.headers.get('X-User-ID')
    
    if (!userId) {
      return NextResponse.json(
        { error: 'X-User-ID header is required' },
        { status: 401 }
      )
    }

    // Forward the request to the backend
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'https://bos-solution.onrender.com/api/v1'}/monitoring/alerts`, {
      headers: {
        'Content-Type': 'application/json',
        'X-User-ID': userId,
      },
    })

    if (!response.ok) {
      const errorText = await response.text()
      console.error('Backend API error:', response.status, errorText)
      return NextResponse.json(
        { error: `Backend API error: ${response.status}`, details: errorText },
        { status: response.status }
      )
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Error in monitoring alerts proxy:', error)
    return NextResponse.json(
      { error: 'Failed to fetch monitoring alerts' },
      { status: 500 }
    )
  }
}
