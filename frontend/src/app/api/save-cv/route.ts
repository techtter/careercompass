import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { user_id, filename, file_type, raw_text, parsed_data } = body;

    // Validate required fields
    if (!user_id || !filename || !file_type || !raw_text || !parsed_data) {
      return NextResponse.json(
        { error: 'Missing required fields' },
        { status: 400 }
      );
    }

    // Call the backend API
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
    const response = await fetch(`${backendUrl}/api/save-cv`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id,
        filename,
        file_type,
        raw_text,
        parsed_data
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Backend save-cv error:', errorText);
      return NextResponse.json(
        { error: 'Failed to save CV to backend' },
        { status: 500 }
      );
    }

    const result = await response.json();
    return NextResponse.json(result);

  } catch (error) {
    console.error('Save CV error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
} 