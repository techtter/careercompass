import { NextRequest, NextResponse } from 'next/server';
import { auth } from '@clerk/nextjs/server';

export async function POST(request: NextRequest) {
  try {
    // Authenticate the user
    const { userId, getToken } = await auth();
    if (!userId) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    // Get the Clerk token for backend authentication
    const token = await getToken();
    if (!token) {
      return NextResponse.json({ error: 'No authentication token' }, { status: 401 });
    }

    // Get the request body
    const body = await request.json();

    // Call the backend API
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
    const response = await fetch(`${backendUrl}/api/skill-gap-analysis`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: 'Backend server error' }));
      return NextResponse.json({ 
        error: errorData.detail || 'Failed to analyze skill gap' 
      }, { status: response.status });
    }

    const result = await response.json();
    return NextResponse.json(result);

  } catch (error) {
    console.error('Skill gap analysis error:', error);
    return NextResponse.json({ 
      error: error instanceof Error ? error.message : 'Failed to analyze skill gap' 
    }, { status: 500 });
  }
} 