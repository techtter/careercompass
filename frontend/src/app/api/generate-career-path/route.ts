import { NextRequest, NextResponse } from 'next/server';
import { auth } from '@clerk/nextjs/server';

export async function POST(request: NextRequest) {
  try {
    // Check if we're in development mode (no Clerk authentication required)
    const isDevelopment = process.env.NODE_ENV === 'development';
    
    if (!isDevelopment) {
      // Authenticate the user in production
      const { userId, getToken } = await auth();
      if (!userId) {
        return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
      }

      // Get the Clerk token for backend authentication
      const token = await getToken();
      if (!token) {
        return NextResponse.json({ error: 'No authentication token' }, { status: 401 });
      }
    }

    // Get the request body
    const body = await request.json();

    // Call the backend API
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    // Add authorization header only in production
    if (!isDevelopment) {
      const { getToken } = await auth();
      const token = await getToken();
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
    }

    const response = await fetch(`${backendUrl}/api/generate-career-path`, {
      method: 'POST',
      headers,
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: 'Backend server error' }));
      return NextResponse.json({ 
        error: errorData.detail || 'Failed to generate career path' 
      }, { status: response.status });
    }

    const result = await response.json();
    return NextResponse.json(result);

  } catch (error) {
    console.error('Career path generation error:', error);
    return NextResponse.json({ 
      error: error instanceof Error ? error.message : 'Failed to generate career path' 
    }, { status: 500 });
  }
} 