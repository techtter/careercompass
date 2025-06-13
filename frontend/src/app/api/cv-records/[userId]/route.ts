import { NextRequest, NextResponse } from 'next/server';
import { auth } from '@clerk/nextjs/server';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ userId: string }> }
) {
  try {
    // Check if we're in development mode (no Clerk authentication required)
    const isDevelopment = process.env.NODE_ENV === 'development';
    
    if (!isDevelopment) {
      // Authenticate the user in production
      const { userId: authUserId, getToken } = await auth();
      if (!authUserId) {
        return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
      }

      // Get the Clerk token for backend authentication
      const token = await getToken();
      if (!token) {
        return NextResponse.json({ error: 'No authentication token' }, { status: 401 });
      }
    }

    // Await params to get userId
    const { userId } = await params;
    
    if (!userId) {
      return NextResponse.json({ error: 'User ID is required' }, { status: 400 });
    }

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

    const response = await fetch(`${backendUrl}/api/cv-records/${userId}`, {
      method: 'GET',
      headers,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: 'Backend server error' }));
      return NextResponse.json({ 
        error: errorData.detail || errorData.message || 'Failed to fetch CV records' 
      }, { status: response.status });
    }

    const result = await response.json();
    return NextResponse.json(result);

  } catch (error) {
    console.error('CV records fetch error:', error);
    return NextResponse.json({ 
      error: error instanceof Error ? error.message : 'Failed to fetch CV records' 
    }, { status: 500 });
  }
} 