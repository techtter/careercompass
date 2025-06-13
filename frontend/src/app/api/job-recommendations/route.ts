import { NextRequest, NextResponse } from 'next/server';

interface JobRequest {
    skills: string[];
    experience: string;
    lastTwoJobs: string[];
    location?: string;
}

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
}

export async function POST(request: NextRequest) {
    try {
        const body: JobRequest = await request.json();
        const { skills, experience, lastTwoJobs, location } = body;

        // Get authorization token
        const authHeader = request.headers.get('authorization');
        if (!authHeader) {
            return NextResponse.json({ error: 'Authorization header required' }, { status: 401 });
        }

        // Call the backend API to get job recommendations
        const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
        const response = await fetch(`${backendUrl}/api/job-recommendations`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': authHeader,
            },
            body: JSON.stringify({
                skills,
                experience,
                lastTwoJobs,
                location
            })
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
            message: data.message || 'Job recommendations retrieved successfully'
        });

    } catch (error) {
        console.error('Job recommendations error:', error);
        return NextResponse.json({ 
            error: 'Failed to process job recommendations request',
            details: error instanceof Error ? error.message : 'Unknown error'
        }, { status: 500 });
    }
} 