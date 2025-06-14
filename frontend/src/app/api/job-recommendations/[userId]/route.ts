import { NextRequest, NextResponse } from 'next/server';

interface JobRecommendation {
    id: string;
    title: string;
    company: string;
    location: string;
    country: string;
    salary?: string;
    description: string;
    applyUrl: string;
    source: string;
    postedDate?: string;
    daysAgo?: number;
    is_real_job?: boolean;
    match_score?: number;
}

export async function GET(
    request: NextRequest,
    { params }: { params: { userId: string } }
) {
    try {
        const { userId } = params;

        if (!userId) {
            return NextResponse.json({ error: 'User ID is required' }, { status: 400 });
        }

        // Get authorization token
        const authHeader = request.headers.get('authorization');
        if (!authHeader) {
            return NextResponse.json({ error: 'Authorization header required' }, { status: 401 });
        }

        // Call the backend API to get job recommendations based on saved user profile
        const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
        const response = await fetch(`${backendUrl}/api/job-recommendations/${userId}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': authHeader,
            }
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error('Backend job recommendations error:', errorText);
            return NextResponse.json({ 
                error: 'Failed to fetch job recommendations',
                details: errorText 
            }, { status: response.status });
        }

        const data = await response.json();
        
        return NextResponse.json({
            jobs: data.jobs || [],
            total: data.total || 0,
            message: data.message || 'Job recommendations retrieved successfully',
            user_location: data.user_location,
            user_country: data.user_country,
            profile_source: data.profile_source
        });

    } catch (error) {
        console.error('Job recommendations error:', error);
        return NextResponse.json({ 
            error: 'Failed to process job recommendations request',
            details: error instanceof Error ? error.message : 'Unknown error'
        }, { status: 500 });
    }
} 