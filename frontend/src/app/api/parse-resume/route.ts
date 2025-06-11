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

    // Get the uploaded file from form data
    const formData = await request.formData();
    const file = formData.get('file') as File;
    
    if (!file) {
      return NextResponse.json({ error: 'No file provided' }, { status: 400 });
    }

    // Create a new FormData to send to backend
    const backendFormData = new FormData();
    backendFormData.append('file', file);

    // Call the backend API
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
    const response = await fetch(`${backendUrl}/api/parse-resume`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: backendFormData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: 'Backend server error' }));
      return NextResponse.json({ 
        error: errorData.detail || 'Failed to parse resume' 
      }, { status: response.status });
    }

    const result = await response.json();
    
    // Parse the JSON response from AI if it's a string
    let parsedData;
    try {
      parsedData = typeof result.parsed_data === 'string' 
        ? JSON.parse(result.parsed_data) 
        : result.parsed_data;
    } catch (parseError) {
      console.error('Failed to parse AI response:', parseError);
      return NextResponse.json({ 
        error: 'Failed to parse resume data from AI response' 
      }, { status: 500 });
    }

    return NextResponse.json({
      success: true,
      parsed_data: parsedData,
      file_info: result.file_info
    });

  } catch (error) {
    console.error('Resume parsing error:', error);
    return NextResponse.json({ 
      error: error instanceof Error ? error.message : 'Failed to parse resume' 
    }, { status: 500 });
  }
} 