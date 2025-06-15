"use client";

import React, { useState, useEffect } from 'react';
import { useAuth, useUser } from '@clerk/nextjs';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Label } from '@/components/ui/Label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ThemeToggle } from '@/components/ui/ThemeToggle';
import JobAIAnimation from '@/components/ui/JobAIAnimation';
import { useUserProfile } from '@/contexts/UserProfileContext';
import Link from 'next/link';

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

interface UserProfile {
    firstName: string;
    lastName: string;
    skills: string[];
    experienceYears: number;
    lastThreeJobTitles: string[];
    location?: string;
}

export default function JobsPage() {
    const { getToken, isLoaded, isSignedIn } = useAuth();
    const { user } = useUser();
    const router = useRouter();
    const { userProfile: contextUserProfile } = useUserProfile();
    
    const [jobs, setJobs] = useState<JobRecommendation[]>([]);
    const [filteredJobs, setFilteredJobs] = useState<JobRecommendation[]>([]);
    const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [locationFilter, setLocationFilter] = useState('');
    const [sourceFilter, setSourceFilter] = useState('');
    const [currentPage, setCurrentPage] = useState(1);
    const [error, setError] = useState('');

    const jobsPerPage = 10;

    useEffect(() => {
        if (isLoaded && isSignedIn) {
            fetchAllJobs();
        }
    }, [isLoaded, isSignedIn]);

    useEffect(() => {
        filterJobs();
    }, [jobs, searchTerm, locationFilter, sourceFilter]);

    const fetchAllJobs = async () => {
        setLoading(true);
        try {
            // First check if we have profile from context
            if (contextUserProfile) {
                console.log('Using profile from context for jobs page:', contextUserProfile);
                // Convert context profile to jobs page profile format
                const jobsProfile: UserProfile = {
                    firstName: contextUserProfile.firstName,
                    lastName: contextUserProfile.lastName,
                    skills: contextUserProfile.skills,
                    experienceYears: contextUserProfile.experienceYears,
                    lastThreeJobTitles: contextUserProfile.lastThreeJobTitles,
                    location: contextUserProfile.location
                };
                setUserProfile(jobsProfile);
            }

            const token = await getToken();
            
            // Use the user profile endpoint which includes job recommendations
            const response = await fetch(`/api/user-profile/${user?.id}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                }
            });

            if (!response.ok) {
                const errorText = await response.text();
                console.error('Failed to fetch user profile with jobs:', errorText);
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            if (data.user_exists && data.job_recommendations) {
                setJobs(data.job_recommendations);
                // Store user profile data for AI animation if not already set from context
                if (data.user_profile && !contextUserProfile) {
                    setUserProfile(data.user_profile);
                }
                console.log(`✅ Loaded ${data.job_recommendations.length} job recommendations from saved profile`);
                
                // Check if Netherlands jobs are prioritized
                const netherlandsJobs = data.job_recommendations.filter((job: any) => 
                    job.country === 'Netherlands' || job.location?.includes('Netherlands')
                );
                if (netherlandsJobs.length > 0) {
                    console.log(`🇳🇱 Found ${netherlandsJobs.length} Netherlands jobs prioritized`);
                }
            } else {
                console.log('No job recommendations available for user profile');
                setJobs([]);
            }
        } catch (error) {
            console.error('Error fetching job recommendations:', error);
            setJobs([]);
        } finally {
            setLoading(false);
        }
    };

    const filterJobs = () => {
        let filtered = jobs;

        if (searchTerm) {
            filtered = filtered.filter(job => 
                job.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                job.company.toLowerCase().includes(searchTerm.toLowerCase()) ||
                job.description.toLowerCase().includes(searchTerm.toLowerCase())
            );
        }

        if (locationFilter) {
            filtered = filtered.filter(job => 
                job.location.toLowerCase().includes(locationFilter.toLowerCase()) ||
                job.country.toLowerCase().includes(locationFilter.toLowerCase())
            );
        }

        if (sourceFilter) {
            filtered = filtered.filter(job => job.source === sourceFilter);
        }

        setFilteredJobs(filtered);
        setCurrentPage(1); // Reset to first page when filtering
    };

    const handleRefresh = () => {
        fetchAllJobs();
    };

    // Pagination
    const totalPages = Math.ceil(filteredJobs.length / jobsPerPage);
    const startIndex = (currentPage - 1) * jobsPerPage;
    const paginatedJobs = filteredJobs.slice(startIndex, startIndex + jobsPerPage);

    // Get unique sources for filter dropdown
    const uniqueSources = Array.from(new Set(jobs.map(job => job.source)));

    if (!isLoaded || !isSignedIn) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="text-lg">Loading...</div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
            {/* Header */}
            <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
                <div className="container mx-auto px-4 py-4 flex justify-between items-center">
                    <div className="flex items-center space-x-4">
                        <Link href="/dashboard">
                            <Button variant="outline" size="sm">
                                ← Back to Dashboard
                            </Button>
                        </Link>
                        <div className="flex items-center space-x-3">
                            {/* Beautiful Compass Logo */}
                            <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-lg flex items-center justify-center shadow-lg">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                    <circle cx="12" cy="12" r="10" stroke="white" strokeWidth="2" fill="none"/>
                                    <path d="m9 12 2 2 4-4" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                                    <path d="M12 2v2" stroke="white" strokeWidth="2" strokeLinecap="round"/>
                                    <path d="M12 20v2" stroke="white" strokeWidth="2" strokeLinecap="round"/>
                                    <path d="M2 12h2" stroke="white" strokeWidth="2" strokeLinecap="round"/>
                                    <path d="M20 12h2" stroke="white" strokeWidth="2" strokeLinecap="round"/>
                                    <path d="M4.93 4.93l1.41 1.41" stroke="white" strokeWidth="2" strokeLinecap="round"/>
                                    <path d="M17.66 17.66l1.41 1.41" stroke="white" strokeWidth="2" strokeLinecap="round"/>
                                    <path d="M19.07 4.93l-1.41 1.41" stroke="white" strokeWidth="2" strokeLinecap="round"/>
                                    <path d="M6.34 17.66l-1.41 1.41" stroke="white" strokeWidth="2" strokeLinecap="round"/>
                                </svg>
                            </div>
                            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Job Recommendations</h1>
                        </div>
                    </div>
                    <div className="flex items-center space-x-4">
                        <Button 
                            onClick={handleRefresh} 
                            variant="outline" 
                            size="sm" 
                            className="mr-4 flex items-center space-x-2 border-blue-200 dark:border-blue-700 text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 hover:border-blue-300 dark:hover:border-blue-600 hover:scale-105 transition-all duration-300 shadow-md hover:shadow-lg"
                        >
                            <svg 
                                className="w-4 h-4 transition-transform duration-300 hover:rotate-180" 
                                fill="none" 
                                stroke="currentColor" 
                                viewBox="0 0 24 24" 
                                xmlns="http://www.w3.org/2000/svg"
                            >
                                <path 
                                    strokeLinecap="round" 
                                    strokeLinejoin="round" 
                                    strokeWidth={2} 
                                    d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" 
                                />
                            </svg>
                            <span>Refresh Jobs</span>
                        </Button>
                        <span className="text-gray-600 dark:text-gray-300">Welcome, {user?.firstName || "User"}!</span>
                        <ThemeToggle />
                    </div>
                </div>
            </header>

            <div className="container mx-auto px-4 py-8">
                
                {/* AI Job Matching Animation */}
                <div className="mb-8">
                    <div className="text-center mb-4">
                        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                            🤖 AI-Powered Job Matching
                        </h2>
                        <p className="text-gray-600 dark:text-gray-300">
                            Our AI is continuously analyzing your profile and finding the perfect career opportunities for your growth
                        </p>
                    </div>
                    <JobAIAnimation userProfile={userProfile} jobs={jobs} />
                </div>
                
                {/* Search and Filters */}
                <Card className="mb-8">
                    <CardHeader>
                        <CardTitle>Search & Filter Jobs</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="grid md:grid-cols-4 gap-4">
                            <div>
                                <Label htmlFor="search">Search Jobs</Label>
                                <Input
                                    id="search"
                                    type="text"
                                    placeholder="Search by title, company, or description..."
                                    value={searchTerm}
                                    onChange={(e) => setSearchTerm(e.target.value)}
                                    className="mt-1"
                                />
                            </div>
                            <div>
                                <Label htmlFor="location">Location</Label>
                                <Input
                                    id="location"
                                    type="text"
                                    placeholder="Filter by location..."
                                    value={locationFilter}
                                    onChange={(e) => setLocationFilter(e.target.value)}
                                    className="mt-1"
                                />
                            </div>
                            <div>
                                <Label htmlFor="source">Job Source</Label>
                                <select
                                    id="source"
                                    value={sourceFilter}
                                    onChange={(e) => setSourceFilter(e.target.value)}
                                    className="mt-1 block w-full rounded-xl border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                                >
                                    <option value="">All Sources</option>
                                    {uniqueSources.map(source => (
                                        <option key={source} value={source}>{source}</option>
                                    ))}
                                </select>
                            </div>
                            <div className="flex items-end">
                                <Button 
                                    onClick={() => {
                                        setSearchTerm('');
                                        setLocationFilter('');
                                        setSourceFilter('');
                                    }}
                                    variant="outline"
                                    className="w-full"
                                >
                                    Clear Filters
                                </Button>
                            </div>
                        </div>
                        
                        <div className="mt-4 text-sm text-gray-600 dark:text-gray-300">
                            Showing {filteredJobs.length} of {jobs.length} job recommendations
                        </div>
                    </CardContent>
                </Card>

                {/* Job Results */}
                {loading ? (
                    <div className="flex flex-col items-center justify-center h-64">
                        <div className="text-center mb-6">
                            <div className="relative">
                                <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-600/30 border-t-blue-600 mx-auto"></div>
                                <div className="absolute inset-0 flex items-center justify-center">
                                    <span className="text-blue-600 font-bold text-xs">AI</span>
                                </div>
                            </div>
                            <p className="text-gray-600 dark:text-gray-300 mt-4 font-medium">AI is finding your perfect job matches...</p>
                            <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">Analyzing your skills and preferences</p>
                        </div>
                        <div className="flex items-center space-x-4">
                            <div className="flex items-center space-x-2">
                                <div className="w-2 h-2 bg-blue-500 rounded-full animate-ping"></div>
                                <span className="text-xs text-gray-600 dark:text-gray-400">Scanning job market</span>
                            </div>
                            <div className="flex items-center space-x-2">
                                <div className="w-2 h-2 bg-purple-500 rounded-full animate-ping" style={{animationDelay: '0.3s'}}></div>
                                <span className="text-xs text-gray-600 dark:text-gray-400">Matching skills</span>
                            </div>
                            <div className="flex items-center space-x-2">
                                <div className="w-2 h-2 bg-green-500 rounded-full animate-ping" style={{animationDelay: '0.6s'}}></div>
                                <span className="text-xs text-gray-600 dark:text-gray-400">Ranking opportunities</span>
                            </div>
                        </div>
                    </div>
                ) : error ? (
                    <Card>
                        <CardContent className="text-center py-12">
                            <div className="text-6xl mb-4">❌</div>
                            <p className="text-red-600 dark:text-red-400 mb-2">{error}</p>
                            <Link href="/dashboard">
                                <Button>Go to Dashboard</Button>
                            </Link>
                        </CardContent>
                    </Card>
                ) : filteredJobs.length === 0 ? (
                    <Card>
                        <CardContent className="text-center py-12">
                            <div className="text-6xl mb-4">🔍</div>
                            {jobs.length === 0 ? (
                                <>
                                    <p className="text-gray-600 dark:text-gray-300 mb-2">No jobs found currently</p>
                                    <p className="text-gray-500 dark:text-gray-400 text-sm">We couldn't find any job openings matching your profile right now. Please check back later or try updating your resume with additional skills.</p>
                                </>
                            ) : (
                                <>
                                    <p className="text-gray-600 dark:text-gray-300 mb-2">No jobs found matching your search criteria</p>
                                    <p className="text-gray-500 dark:text-gray-400 text-sm">Try adjusting your search filters or refresh the page</p>
                                </>
                            )}
                        </CardContent>
                    </Card>
                ) : (
                    <>
                        {/* Job Listings */}
                        <div className="space-y-6">
                            {paginatedJobs.map((job) => (
                                <Card key={job.id} className="hover:shadow-lg transition-shadow">
                                    <CardContent className="p-6">
                                        <div className="flex justify-between items-start">
                                            <div className="flex-1">
                                                <div className="flex items-center space-x-2 mb-2">
                                                    <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100">{job.title}</h3>
                                                    <div className="flex items-center space-x-1 bg-blue-100 dark:bg-blue-900/30 px-2 py-1 rounded-full">
                                                        <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                                                        <span className="text-xs text-blue-700 dark:text-blue-300 font-medium">AI Matched</span>
                                                    </div>
                                                </div>
                                                <p className="text-lg text-gray-700 dark:text-gray-300 font-medium mb-2">{job.company}</p>
                                                
                                                <div className="flex items-center text-sm text-gray-600 dark:text-gray-400 mb-3">
                                                    <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                                        <path fillRule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd" />
                                                    </svg>
                                                    <span className="mr-4">{job.location}, {job.country}</span>
                                                    
                                                    {job.salary && (
                                                        <>
                                                            <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                                                <path d="M8.433 7.418c.155-.103.346-.196.567-.267v1.698a2.305 2.305 0 01-.567-.267C8.07 8.34 8 8.114 8 8c0-.114.07-.34.433-.582zM11 12.849v-1.698c.22.071.412.164.567.267.364.243.433.468.433.582 0 .114-.07.34-.433.582a2.305 2.305 0 01-.567.267z" />
                                                                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-13a1 1 0 10-2 0v.092a4.535 4.535 0 00-1.676.662C6.602 6.234 6 7.009 6 8c0 .99.602 1.765 1.324 2.246.48.32 1.054.545 1.676.662v1.941c-.391-.127-.68-.317-.843-.504a1 1 0 10-1.51 1.31c.562.649 1.413 1.076 2.353 1.253V15a1 1 0 102 0v-.092a4.535 4.535 0 001.676-.662C13.398 13.766 14 12.991 14 12c0-.99-.602-1.765-1.324-2.246A4.535 4.535 0 0011 9.092V7.151c.391.127.68.317.843.504a1 1 0 101.511-1.31c-.563-.649-1.413-1.076-2.354-1.253V5z" clipRule="evenodd" />
                                                            </svg>
                                                            <span className="text-green-600 dark:text-green-400 font-medium">{job.salary}</span>
                                                        </>
                                                    )}
                                                </div>
                                                
                                                <p className="text-gray-600 dark:text-gray-300 mb-4 leading-relaxed">{job.description}</p>
                                                
                                                                                <div className="flex items-center justify-between">
                                    <div className="flex items-center space-x-3">
                                        <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
                                            {job.source}
                                        </span>
                                        {/* Real Job Indicator */}
                                        {job.is_real_job !== undefined && (
                                            <span className={`text-xs px-2 py-1 rounded font-medium ${
                                                job.is_real_job 
                                                    ? 'bg-green-100 text-green-700 border border-green-200' 
                                                    : 'bg-amber-100 text-amber-700 border border-amber-200'
                                            }`}>
                                                {job.is_real_job ? '🌐 Live Job' : '🎭 Demo Data'}
                                            </span>
                                        )}
                                        {/* Match Score */}
                                        {job.match_score !== undefined && (
                                            <span className={`text-xs px-2 py-1 rounded font-medium ${
                                                job.match_score >= 80 ? 'bg-green-100 text-green-700' :
                                                job.match_score >= 60 ? 'bg-blue-100 text-blue-700' :
                                                'bg-gray-100 text-gray-600'
                                            }`}>
                                                ⭐ {job.match_score}% Match
                                            </span>
                                        )}
                                        {job.daysAgo !== undefined && (
                                            <span className={`text-xs px-2 py-1 rounded font-medium ${
                                                job.daysAgo <= 3 ? 'bg-green-100 text-green-700' :
                                                job.daysAgo <= 7 ? 'bg-blue-100 text-blue-700' :
                                                job.daysAgo <= 14 ? 'bg-yellow-100 text-yellow-700' :
                                                'bg-gray-100 text-gray-600'
                                            }`}>
                                                {job.daysAgo === 0 ? 'Posted Today' : 
                                                 job.daysAgo === 1 ? 'Posted 1 day ago' : 
                                                 `Posted ${job.daysAgo} days ago`}
                                            </span>
                                        )}
                                        {job.postedDate && (
                                            <span className="text-xs text-gray-500">
                                                {new Date(job.postedDate).toLocaleDateString()}
                                            </span>
                                        )}
                                    </div>
                                </div>
                                            </div>
                                            
                                            <div className="ml-6">
                                                <a
                                                    href={job.applyUrl}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-xl font-medium transition-colors inline-flex items-center"
                                                >
                                                    Apply Job
                                                    <svg className="w-4 h-4 ml-2" fill="currentColor" viewBox="0 0 20 20">
                                                        <path fillRule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clipRule="evenodd" />
                                                    </svg>
                                                </a>
                                            </div>
                                        </div>
                                    </CardContent>
                                </Card>
                            ))}
                        </div>

                        {/* Pagination */}
                        {totalPages > 1 && (
                            <div className="flex justify-center items-center space-x-2 mt-8">
                                <Button
                                    onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                                    disabled={currentPage === 1}
                                    variant="outline"
                                >
                                    Previous
                                </Button>
                                
                                <div className="flex space-x-1">
                                    {Array.from({ length: totalPages }, (_, i) => i + 1).map(page => (
                                        <Button
                                            key={page}
                                            onClick={() => setCurrentPage(page)}
                                            variant={currentPage === page ? "default" : "outline"}
                                            size="sm"
                                        >
                                            {page}
                                        </Button>
                                    ))}
                                </div>
                                
                                <Button
                                    onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
                                    disabled={currentPage === totalPages}
                                    variant="outline"
                                >
                                    Next
                                </Button>
                            </div>
                        )}
                    </>
                )}
            </div>
        </div>
    );
} 