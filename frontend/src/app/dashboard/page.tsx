"use client";

import { useState, useEffect } from "react";
import { useAuth, useUser, SignOutButton } from "@clerk/nextjs";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Label } from "@/components/ui/Label";
import { ThemeToggle } from "@/components/ui/ThemeToggle";
import Link from "next/link";
import SkillsWordCloud from "@/components/ui/SkillsWordCloud";
import WelcomeSection from "@/components/ui/WelcomeSection";
import { getCachedJobs, cacheJobs, shouldRefreshJobCache, refreshUserJobCache } from '@/utils/jobCache';
import { useUserProfile } from "@/contexts/UserProfileContext";
import dynamic from 'next/dynamic';

const CardBackgroundAnimation = dynamic(() => import('@/components/ui/CardBackgroundAnimation'), {
  ssr: false
});

// Add Clerk type declaration for TypeScript
declare global {
    interface Window {
        Clerk?: {
            user?: {
                id: string;
            };
        };
    }
}

interface UserProfile {
  firstName: string;
  lastName: string;
  email?: string | null;
  phone?: string | null;
  location?: string | null;
  experienceYears: number;
  skills: string[];
  lastThreeJobTitles: string[];
  experienceSummary: string;
  companies: string[];
  education: string[];
  certifications: string[];
  raw_text?: string | null;  // For storing the actual CV content
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
    daysAgo?: number;
    is_real_job?: boolean;
    match_score?: number;
}

export default function Dashboard() {
    const { getToken, isLoaded, isSignedIn } = useAuth();
    const { user } = useUser();
    const router = useRouter();
    const { userProfile: contextUserProfile, updateProfile, refreshProfile } = useUserProfile();
    
    // State management
    const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
    const [parsedResumeData, setParsedResumeData] = useState<UserProfile | null>(null);
    const [originalCvText, setOriginalCvText] = useState<string>(''); // Add state for original CV text
    const [uploadedFile, setUploadedFile] = useState<File | null>(null);
    const [isExistingUser, setIsExistingUser] = useState(false);
    const [isLoadingProfile, setIsLoadingProfile] = useState(true);
    const [savedCvId, setSavedCvId] = useState<string>('');
    const [lastUpdated, setLastUpdated] = useState<string>('');
    const [parseSuccessMessage, setParseSuccessMessage] = useState("");
    const [parseErrorMessage, setParseErrorMessage] = useState("");
    const [isUploading, setIsUploading] = useState(false);
    const [isParsingProgress, setIsParsingProgress] = useState(false);
    const [parsingProgress, setParsingProgress] = useState(0);
    const [parsingStep, setParsingStep] = useState("");
    const [isSavingProfile, setIsSavingProfile] = useState(false);
    const [jobRecommendations, setJobRecommendations] = useState<JobRecommendation[]>([]);
    const [loadingJobs, setLoadingJobs] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [showFileUpload, setShowFileUpload] = useState(false);
    const [showProfileSection, setShowProfileSection] = useState(false);
    const [isEditingProfile, setIsEditingProfile] = useState(false);
    const [editableProfile, setEditableProfile] = useState<UserProfile | null>(null);

    useEffect(() => {
        const fetchUserProfile = async () => {
            try {
                setIsLoadingProfile(true);
                setError(null);

                // Get user ID from Clerk - no fallback to dummy data
                let userId: string | null = null;
                try {
                    // Only try Clerk if it's available and configured
                    if (typeof window !== 'undefined' && window.Clerk?.user?.id) {
                        userId = window.Clerk.user.id;
                    } else if (isLoaded && isSignedIn && user?.id) {
                        userId = user.id;
                    }
                } catch (clerkError) {
                    console.log("Clerk not available, no user authentication");
                }

                // If no authenticated user, show upload interface
                if (!userId) {
                    setIsExistingUser(false);
                    setShowFileUpload(true);
                    setParseSuccessMessage("");
                    setIsLoadingProfile(false);
                    return;
                }

                // First check if we have profile from context
                if (contextUserProfile && contextUserProfile.skills?.length > 0) {
                    console.log('Using profile from context:', contextUserProfile);
                    // Convert context profile to dashboard profile format
                    const dashboardProfile: UserProfile = {
                        firstName: contextUserProfile.firstName,
                        lastName: contextUserProfile.lastName,
                        email: contextUserProfile.email,
                        phone: null,
                        location: contextUserProfile.location,
                        experienceYears: contextUserProfile.experienceYears,
                        skills: contextUserProfile.skills,
                        lastThreeJobTitles: contextUserProfile.lastThreeJobTitles,
                        experienceSummary: contextUserProfile.experience || '',
                        companies: [],
                        education: contextUserProfile.education,
                        certifications: contextUserProfile.certifications,
                        raw_text: null
                    };
                    setUserProfile(dashboardProfile);
                    setIsExistingUser(true);
                    setShowFileUpload(false);
                    
                    // Still fetch job recommendations and CV metadata from backend
                    try {
                        const response = await fetch(`/api/user-profile/${userId}`);
                        if (response.ok) {
                            const data = await response.json();
                            if (data.job_recommendations) {
                                setJobRecommendations(data.job_recommendations);
                            }
                            if (data.cv_record_id) {
                                setSavedCvId(data.cv_record_id);
                                setLastUpdated(data.last_updated);
                                setParseSuccessMessage(data.message);
                            }
                        }
                    } catch (error) {
                        console.log('Could not fetch additional data from backend');
                    }
                    
                    setIsLoadingProfile(false);
                    return;
                }

                console.log('Fetching profile for user:', userId);

                // Call the user profile API
                const response = await fetch(`/api/user-profile/${userId}`);
                
                if (!response.ok) {
                    throw new Error(`Failed to fetch user profile: ${response.status}`);
                }

                const data = await response.json();
                console.log('User profile response:', data);

                if (data.user_exists) {
                    setUserProfile(data.user_profile);
                    setJobRecommendations(data.job_recommendations || []);
                    setSavedCvId(data.cv_record_id);
                    setLastUpdated(data.last_updated);
                    setIsExistingUser(true);
                    setShowFileUpload(false);
                    setParseSuccessMessage(data.message);
                    
                    // Update context with the fetched profile
                    updateProfile(data.user_profile);
                    
                    // Save to localStorage for jobs page
                    localStorage.setItem('userProfile', JSON.stringify(data.user_profile));
                } else {
                    setIsExistingUser(false);
                    setShowFileUpload(true);
                    setParseSuccessMessage("");
                }
            } catch (error) {
                console.error('Error fetching user profile:', error);
                setError(error instanceof Error ? error.message : 'Failed to load profile');
                setShowFileUpload(true);
                setIsExistingUser(false);
                setParseErrorMessage('Failed to load user profile. Please try uploading your CV.');
            } finally {
                setIsLoadingProfile(false);
            }
        };

        fetchUserProfile();
    }, [isLoaded, isSignedIn, user?.id, contextUserProfile]);

    // Handle file upload and automatic parsing
    const handleFileUploadAndParse = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (!file) return;

        // Validate file type
        const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 
                             'application/msword', 'text/plain'];
        if (!allowedTypes.includes(file.type)) {
            setParseErrorMessage('Please upload a PDF, DOC, DOCX, or TXT file.');
            return;
        }

        // Validate file size (10MB limit)
        if (file.size > 10 * 1024 * 1024) {
            setParseErrorMessage('File size must be less than 10MB.');
            return;
        }

        setUploadedFile(file);
        setParseSuccessMessage("");
        setParseErrorMessage("");
        setIsParsingProgress(true);
        setParsingProgress(0);
        setParsingStep("Uploading file...");

        try {
            // Simulate progress steps
            setParsingProgress(20);
            setParsingStep("Processing document...");

            const formData = new FormData();
            formData.append('file', file);

            const token = await getToken();
            
            setParsingProgress(40);
            setParsingStep("Extracting text content...");

            const response = await fetch('/api/parse-resume', {
                method: 'POST',
                headers: {
                    Authorization: `Bearer ${token}`,
                },
                body: formData,
            });

            setParsingProgress(70);
            setParsingStep("Analyzing with AI...");

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to parse resume');
            }

            const result = await response.json();
            
            setParsingProgress(90);
            setParsingStep("Finalizing results...");

            // Set the parsed data and store original CV text
            setParsedResumeData(result.parsed_data);
            setUserProfile(result.parsed_data); // Update userProfile to show the profile section
            setOriginalCvText(result.file_info?.raw_text || ''); // Store original CV text
            
            // Save to localStorage for jobs page
            localStorage.setItem('userProfile', JSON.stringify(result.parsed_data));
            
            // Update UI state to show profile and hide upload
            setIsExistingUser(true);
            setShowFileUpload(false);
            setShowProfileSection(true);
            
            setParsingProgress(100);
            setParsingStep("Complete!");

            // Show success message
            setParseSuccessMessage(`✅ Resume parsed successfully! Extracted profile for: ${result.parsed_data.firstName || 'User'} ${result.parsed_data.lastName || ''}`);
            
            // Fetch job recommendations after successful resume parsing
            await fetchJobRecommendations(result.parsed_data);
            
            // Save the CV data to backend
            try {
                await handleSaveCV();
            } catch (saveError) {
                console.error('Error saving CV:', saveError);
                // Don't fail the whole process if save fails
            }
            
            // Clear progress after a short delay
            setTimeout(() => {
                setIsParsingProgress(false);
                setParsingProgress(0);
                setParsingStep("");
            }, 1500);
            
        } catch (error) {
            console.error('Error parsing resume:', error);
            setParseErrorMessage(error instanceof Error ? error.message : 'Error parsing resume. Please try again.');
            setIsParsingProgress(false);
            setParsingProgress(0);
            setParsingStep("");
        }
    };

    // Update existing user's CV with automatic parsing
    const handleUpdateCV = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (!file || !user?.id) return;

        // Validate file type
        const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 
                             'application/msword', 'text/plain'];
        if (!allowedTypes.includes(file.type)) {
            setParseErrorMessage('Please upload a PDF, DOC, DOCX, or TXT file.');
            return;
        }

        // Validate file size (10MB limit)
        if (file.size > 10 * 1024 * 1024) {
            setParseErrorMessage('File size must be less than 10MB.');
            return;
        }

        setIsParsingProgress(true);
        setParsingProgress(0);
        setParsingStep("Uploading updated CV...");
        setParseSuccessMessage("");
        setParseErrorMessage("");
        
        try {
            setParsingProgress(20);
            setParsingStep("Processing document...");

            const formData = new FormData();
            formData.append('file', file);

            setParsingProgress(40);
            setParsingStep("Extracting updated information...");

            const response = await fetch(`/api/update-cv/${user.id}`, {
                method: 'PUT',
                body: formData,
            });

            setParsingProgress(70);
            setParsingStep("Analyzing changes...");

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to update CV');
            }

            const result = await response.json();
            
            setParsingProgress(90);
            setParsingStep("Updating profile...");
            
            // Update user profile with new data and store original CV text
            setUserProfile(result.parsed_data);
            setOriginalCvText(result.file_info?.raw_text || ''); // Store original CV text
            setSavedCvId(result.cv_record_id);
            
            // Save updated profile to localStorage
            localStorage.setItem('userProfile', JSON.stringify(result.parsed_data));
            
            setParsingProgress(100);
            setParsingStep("Complete!");
            
            // Show success message
            setParseSuccessMessage(`✅ CV updated successfully! Profile updated for: ${result.parsed_data.firstName || 'User'} ${result.parsed_data.lastName || ''}`);
            
            // Fetch new job recommendations based on updated profile
            await fetchJobRecommendations(result.parsed_data);
            
            // Clear progress and hide upload section after a short delay
            setTimeout(() => {
                setIsParsingProgress(false);
                setParsingProgress(0);
                setParsingStep("");
                setShowFileUpload(false);
            }, 1500);
            
        } catch (error) {
            console.error('Error updating CV:', error);
            setParseErrorMessage(error instanceof Error ? error.message : 'Error updating CV. Please try again.');
            setIsParsingProgress(false);
            setParsingProgress(0);
            setParsingStep("");
        }
    };

    // Fetch job recommendations based on user profile
    const fetchJobRecommendations = async (profile: UserProfile, forceRefresh: boolean = false) => {
        if (!user?.id) {
            console.log('No user ID available for job recommendations');
            return;
        }

        // Check if we should force refresh cache
        if (forceRefresh || shouldRefreshJobCache(user.id)) {
            console.log('🔄 Force refreshing job cache...');
        } else {
            // Try to get cached jobs first
            const cachedJobs = getCachedJobs(user.id, profile);
            if (cachedJobs && cachedJobs.length > 0) {
                setJobRecommendations(cachedJobs);
                console.log(`🎯 FRONTEND CACHE HIT: Loaded ${cachedJobs.length} cached job recommendations`);
                return;
            }
        }

        console.log('🔍 FRONTEND CACHE MISS: Fetching fresh jobs from API...');
        setLoadingJobs(true);
        
        try {
            const token = await getToken();
            
            // For existing users, use the user profile endpoint which includes job recommendations
            if (user?.id && isExistingUser) {
                const response = await fetch(`/api/user-profile/${user.id}`, {
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
                    setJobRecommendations(data.job_recommendations);
                    console.log(`✅ Loaded ${data.job_recommendations.length} job recommendations from saved profile`);
                    
                    // Cache the jobs for future use
                    cacheJobs(user.id, data.job_recommendations, profile, 30);
                    
                    // Check if Netherlands jobs are prioritized
                    const netherlandsJobs = data.job_recommendations.filter((job: any) => 
                        job.country === 'Netherlands' || job.location?.includes('Netherlands')
                    );
                    if (netherlandsJobs.length > 0) {
                        console.log(`🇳🇱 Found ${netherlandsJobs.length} Netherlands jobs prioritized`);
                    }
                } else {
                    console.log('No job recommendations available for saved profile');
                    setJobRecommendations([]);
                }
            } else {
                // For new users with parsed data, use the direct job recommendations endpoint
                const response = await fetch('/api/job-recommendations', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`,
                    },
                    body: JSON.stringify({
                        skills: profile.skills,
                        experience: `${profile.experienceYears} years`,
                        lastTwoJobs: profile.lastThreeJobTitles.slice(0, 2),
                        location: profile.location
                    })
                });

                if (!response.ok) {
                    const errorText = await response.text();
                    console.error('Failed to fetch job recommendations:', errorText);
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();
                
                if (data.jobs && Array.isArray(data.jobs)) {
                    setJobRecommendations(data.jobs);
                    console.log(`✅ Loaded ${data.jobs.length} job recommendations for new profile`);
                    
                    // Cache the jobs for future use (use temporary user ID for new users)
                    const tempUserId = user?.id || 'temp_user';
                    cacheJobs(tempUserId, data.jobs, profile, 30);
                } else {
                    console.log('No job recommendations available');
                    setJobRecommendations([]);
                }
            }
        } catch (error) {
            console.error('Error fetching job recommendations:', error);
            setJobRecommendations([]);
        } finally {
            setLoadingJobs(false);
        }
    };

    // Handle profile editing
    const handleEditProfile = () => {
        setEditableProfile({ ...userProfile! });
        setIsEditingProfile(true);
    };

    const handleCancelEdit = () => {
        setEditableProfile(null);
        setIsEditingProfile(false);
    };

    const handleSaveProfile = async () => {
        if (!editableProfile || !user?.id) return;

        setIsSavingProfile(true);
        setParseSuccessMessage("");
        setParseErrorMessage("");
        
        try {
            const token = await getToken();
            
            // Prepare comprehensive profile data including CV content
            const profileData = {
                firstName: editableProfile.firstName,
                lastName: editableProfile.lastName,
                email: editableProfile.email,
                phone: editableProfile.phone,
                location: editableProfile.location,
                experienceYears: editableProfile.experienceYears,
                experienceSummary: editableProfile.experienceSummary,
                skills: editableProfile.skills,
                lastThreeJobTitles: editableProfile.lastThreeJobTitles,
                companies: editableProfile.companies,
                education: editableProfile.education,
                certifications: editableProfile.certifications,
                // Include the original CV content if available
                raw_text: userProfile?.raw_text || null
            };
            
            // Use the enhanced user profile update API
            const response = await fetch(`/api/user-profile/${user.id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${token}`,
                },
                body: JSON.stringify(profileData),
            });

            if (!response.ok) {
                throw new Error('Failed to save complete profile');
            }

            const result = await response.json();
            
            // Update user profile with edited data
            setUserProfile(editableProfile);
            setEditableProfile(null);
            setIsEditingProfile(false);
            setLastUpdated(new Date().toISOString());
            setParseSuccessMessage('✅ Complete profile saved successfully! All details including skills, experience, education, certifications, and CV have been saved to the database.');
            
            // Save to localStorage
            localStorage.setItem('userProfile', JSON.stringify(editableProfile));
            
            // Fetch new job recommendations based on updated profile
            await fetchJobRecommendations(editableProfile);
            
        } catch (error) {
            console.error('Error saving complete profile:', error);
            setParseErrorMessage('Error saving complete profile. Please try again.');
        } finally {
            setIsSavingProfile(false);
        }
    };

    // Save CV to database
    const handleSaveCV = async () => {
        const profileData = parsedResumeData || userProfile;
        if (!profileData) return;

        setIsSavingProfile(true);
        setParseSuccessMessage("");
        setParseErrorMessage("");
        
        try {
            const token = await getToken();
            const response = await fetch('/api/save-cv', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${token}`,
                },
                body: JSON.stringify({
                    user_id: user?.id || 'user_1',
                    filename: uploadedFile?.name || 'profile_data.txt',
                    file_type: uploadedFile?.type || 'text/plain',
                    raw_text: originalCvText || `${profileData.firstName} ${profileData.lastName}\n${profileData.email || ''}\n\nExperience: ${profileData.experienceYears} years\n\nSkills: ${profileData.skills.join(', ')}\n\nEducation: ${profileData.education.join(', ')}\n\nSummary: ${profileData.experienceSummary}`,
                    parsed_data: profileData,
                }),
            });

            if (!response.ok) {
                throw new Error('Failed to save CV');
            }

            const result = await response.json();
            
            // After successful save, update state
            setSavedCvId(result.cv_record_id);
            setLastUpdated(new Date().toISOString());
            setParseSuccessMessage('✅ Profile saved successfully! Welcome to Career Compass AI!');
            
        } catch (error) {
            console.error('Error saving CV:', error);
            setParseErrorMessage('Error saving profile. Please try again.');
        } finally {
            setIsSavingProfile(false);
        }
    };

    if (!isLoaded || !isSignedIn) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="text-lg">Loading...</div>
            </div>
        );
    }

    // Show loading state while checking user profile
    if (isLoadingProfile) {
        return (
            <div className="min-h-screen bg-white dark:bg-gray-900">
                <div className="container mx-auto px-4 py-8">
                    <div className="flex items-center justify-center min-h-96">
                        <div className="text-center">
                            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                            <div className="text-lg text-gray-600 dark:text-gray-300">Loading your profile...</div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-white dark:bg-gray-900">
            <div className="container mx-auto px-4 py-8">
                {/* Welcome Section with AI Animation and Controls */}
                <WelcomeSection firstName={userProfile?.firstName} />

                {/* Main Content */}
                {error ? (
                    <div className="text-red-600 dark:text-red-400">{error}</div>
                ) : (
                    <>
                        {/* Profile Section */}
                        {userProfile && (
                            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6 mb-8">
                                {/* Profile Header with Action Buttons */}
                                <div className="flex justify-between items-center mb-4">
                                    <h2 className="text-xl font-semibold flex items-center space-x-2">
                                        <svg className="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                                        </svg>
                                        <span>Your Profile</span>
                                    </h2>
                                    <div className="flex space-x-3">
                                        {/* Save Profile to Database Button */}
                                        <Button 
                                            onClick={handleSaveCV} 
                                            disabled={isSavingProfile}
                                            className="flex items-center space-x-2 bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white border-0 hover:scale-105 transition-all duration-300 shadow-md hover:shadow-lg"
                                            size="sm"
                                        >
                                            {isSavingProfile ? (
                                                <>
                                                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                                                    <span>Saving...</span>
                                                </>
                                            ) : (
                                                <>
                                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3-3m0 0l-3 3m3-3v12" />
                                                    </svg>
                                                    <span>Save to Database</span>
                                                </>
                                            )}
                                        </Button>
                                        
                                        {/* Edit Profile Button */}
                                        <Button 
                                            onClick={handleEditProfile} 
                                            variant="outline" 
                                            size="sm"
                                            className="flex items-center space-x-2 border-blue-200 dark:border-blue-700 text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 hover:border-blue-300 dark:hover:border-blue-600 hover:scale-105 transition-all duration-300 shadow-md hover:shadow-lg"
                                        >
                                            <svg className="w-4 h-4 transition-transform duration-300 group-hover:rotate-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                                            </svg>
                                            <span>Edit Profile</span>
                                        </Button>
                                    </div>
                                </div>

                                {/* Success/Error Messages for Save Operations */}
                                {parseSuccessMessage && (
                                    <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-md p-4 mb-4">
                                        <div className="flex items-center space-x-2">
                                            <svg className="w-5 h-5 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                            </svg>
                                            <p className="text-green-800 dark:text-green-200">{parseSuccessMessage}</p>
                                        </div>
                                    </div>
                                )}
                                
                                {parseErrorMessage && (
                                    <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md p-4 mb-4">
                                        <div className="flex items-center space-x-2">
                                            <svg className="w-5 h-5 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                            </svg>
                                            <p className="text-red-800 dark:text-red-200">{parseErrorMessage}</p>
                                        </div>
                                    </div>
                                )}

                                {/* Profile Content - Show edit form when editing */}
                                {isEditingProfile && editableProfile ? (
                                    <div className="space-y-6">
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                            {/* Personal Information */}
                                            <div className="space-y-4">
                                                <div>
                                                    <Label htmlFor="firstName">First Name</Label>
                                                    <Input
                                                        id="firstName"
                                                        value={editableProfile.firstName}
                                                        onChange={(e) => setEditableProfile({
                                                            ...editableProfile,
                                                            firstName: e.target.value
                                                        })}
                                                    />
                                                </div>
                                                <div>
                                                    <Label htmlFor="lastName">Last Name</Label>
                                                    <Input
                                                        id="lastName"
                                                        value={editableProfile.lastName}
                                                        onChange={(e) => setEditableProfile({
                                                            ...editableProfile,
                                                            lastName: e.target.value
                                                        })}
                                                    />
                                                </div>
                                                <div>
                                                    <Label htmlFor="email">Email</Label>
                                                    <Input
                                                        id="email"
                                                        type="email"
                                                        value={editableProfile.email || ''}
                                                        onChange={(e) => setEditableProfile({
                                                            ...editableProfile,
                                                            email: e.target.value
                                                        })}
                                                    />
                                                </div>
                                                <div>
                                                    <Label htmlFor="phone">Phone</Label>
                                                    <Input
                                                        id="phone"
                                                        value={editableProfile.phone || ''}
                                                        onChange={(e) => setEditableProfile({
                                                            ...editableProfile,
                                                            phone: e.target.value
                                                        })}
                                                    />
                                                </div>
                                                <div>
                                                    <Label htmlFor="location">Location</Label>
                                                    <Input
                                                        id="location"
                                                        value={editableProfile.location || ''}
                                                        onChange={(e) => setEditableProfile({
                                                            ...editableProfile,
                                                            location: e.target.value
                                                        })}
                                                    />
                                                </div>
                                                <div>
                                                    <Label htmlFor="experienceYears">Years of Experience</Label>
                                                    <Input
                                                        id="experienceYears"
                                                        type="number"
                                                        value={editableProfile.experienceYears}
                                                        onChange={(e) => setEditableProfile({
                                                            ...editableProfile,
                                                            experienceYears: parseInt(e.target.value) || 0
                                                        })}
                                                    />
                                                </div>
                                            </div>

                                            {/* Professional Information */}
                                            <div className="space-y-4">
                                                <div>
                                                    <Label htmlFor="experienceSummary">Experience Summary</Label>
                                                    <textarea
                                                        id="experienceSummary"
                                                        className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                                                        rows={4}
                                                        value={editableProfile.experienceSummary}
                                                        onChange={(e) => setEditableProfile({
                                                            ...editableProfile,
                                                            experienceSummary: e.target.value
                                                        })}
                                                    />
                                                </div>
                                                <div>
                                                    <Label htmlFor="skills">Skills (comma-separated)</Label>
                                                    <textarea
                                                        id="skills"
                                                        className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                                                        rows={3}
                                                        value={editableProfile.skills.join(', ')}
                                                        onChange={(e) => setEditableProfile({
                                                            ...editableProfile,
                                                            skills: e.target.value.split(',').map(s => s.trim()).filter(s => s)
                                                        })}
                                                    />
                                                </div>
                                                <div>
                                                    <Label htmlFor="jobTitles">Recent Job Titles (comma-separated)</Label>
                                                    <textarea
                                                        id="jobTitles"
                                                        className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                                                        rows={2}
                                                        value={editableProfile.lastThreeJobTitles.join(', ')}
                                                        onChange={(e) => setEditableProfile({
                                                            ...editableProfile,
                                                            lastThreeJobTitles: e.target.value.split(',').map(s => s.trim()).filter(s => s)
                                                        })}
                                                    />
                                                </div>
                                                <div>
                                                    <Label htmlFor="companies">Companies (comma-separated)</Label>
                                                    <textarea
                                                        id="companies"
                                                        className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                                                        rows={2}
                                                        value={editableProfile.companies.join(', ')}
                                                        onChange={(e) => setEditableProfile({
                                                            ...editableProfile,
                                                            companies: e.target.value.split(',').map(s => s.trim()).filter(s => s)
                                                        })}
                                                    />
                                                </div>
                                            </div>
                                        </div>

                                        {/* Update CV Section */}
                                        <div className="border-t pt-6">
                                            <h3 className="text-lg font-semibold mb-4 flex items-center space-x-2">
                                                <svg className="w-5 h-5 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                                                </svg>
                                                <span>Update CV</span>
                                            </h3>
                                            <div className="space-y-4">
                                                {!isParsingProgress ? (
                                                    <Input
                                                        type="file"
                                                        accept=".pdf,.doc,.docx,.txt"
                                                        onChange={handleUpdateCV}
                                                        className="mb-4"
                                                        disabled={isParsingProgress}
                                                    />
                                                ) : (
                                                    <div className="mb-4 p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-200 dark:border-purple-800">
                                                        <div className="flex items-center space-x-3 mb-3">
                                                            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-purple-600"></div>
                                                            <span className="text-purple-800 dark:text-purple-200 font-medium">{parsingStep}</span>
                                                        </div>
                                                        
                                                        {/* Animated Progress Bar */}
                                                        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 mb-2">
                                                            <div 
                                                                className="bg-gradient-to-r from-purple-500 to-pink-600 h-3 rounded-full transition-all duration-500 ease-out relative overflow-hidden"
                                                                style={{ width: `${parsingProgress}%` }}
                                                            >
                                                                {/* Animated shine effect */}
                                                                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-pulse"></div>
                                                            </div>
                                                        </div>
                                                        
                                                        <div className="flex justify-between text-sm text-purple-700 dark:text-purple-300">
                                                            <span>Updating your profile...</span>
                                                            <span>{parsingProgress}%</span>
                                                        </div>
                                                    </div>
                                                )}
                                                <p className="text-sm text-gray-600 dark:text-gray-400">
                                                    Upload a new CV to automatically update your profile information
                                                </p>
                                            </div>
                                        </div>

                                        {/* Action Buttons */}
                                        <div className="flex space-x-4 pt-4">
                                            <Button 
                                                onClick={handleSaveProfile} 
                                                disabled={isSavingProfile}
                                                className="flex items-center space-x-2"
                                            >
                                                {isSavingProfile ? (
                                                    <>
                                                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                                                        <span>Saving...</span>
                                                    </>
                                                ) : (
                                                    <>
                                                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                                        </svg>
                                                        <span>Save Changes</span>
                                                    </>
                                                )}
                                            </Button>
                                            <Button 
                                                onClick={handleCancelEdit} 
                                                variant="outline"
                                                className="flex items-center space-x-2"
                                            >
                                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                                </svg>
                                                <span>Cancel</span>
                                            </Button>
                                        </div>

                                        {/* Success/Error Messages */}
                                        {parseSuccessMessage && (
                                            <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-md p-4">
                                                <p className="text-green-800 dark:text-green-200">{parseSuccessMessage}</p>
                                            </div>
                                        )}
                                        {parseErrorMessage && (
                                            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md p-4">
                                                <p className="text-red-800 dark:text-red-200">{parseErrorMessage}</p>
                                            </div>
                                        )}
                                    </div>
                                ) : (
                                    // Regular profile view
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                        {/* Personal Information and Skills */}
                                        <div className="space-y-4">
                                            <div>
                                                <Label>Name</Label>
                                                <p className="text-gray-600 dark:text-gray-400">
                                                    {userProfile.firstName} {userProfile.lastName}
                                                </p>
                                            </div>
                                            <div>
                                                <Label>Email</Label>
                                                <p className="text-gray-600 dark:text-gray-400">
                                                    {userProfile.email || 'Not specified'}
                                                </p>
                                            </div>
                                            <div>
                                                <Label>Phone</Label>
                                                <p className="text-gray-600 dark:text-gray-400">
                                                    {userProfile.phone || 'Not specified'}
                                                </p>
                                            </div>
                                            <div>
                                                <Label>Location</Label>
                                                <p className="text-gray-600 dark:text-gray-400">
                                                    {userProfile.location || 'Not specified'}
                                                </p>
                                            </div>
                                            <div>
                                                <Label>Experience</Label>
                                                <p className="text-gray-600 dark:text-gray-400">
                                                    {userProfile.experienceYears} years
                                                </p>
                                            </div>
                                            <div>
                                                <Label className="font-bold text-lg flex items-center space-x-2 mb-4">
                                                    <svg className="w-5 h-5 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                                                    </svg>
                                                    <span>Technical Skills</span>
                                                </Label>
                                                <SkillsWordCloud skills={userProfile.skills} />
                                            </div>
                                        </div>

                                        {/* Professional Information and Job Recommendations */}
                                        <div className="space-y-4">
                                            <div>
                                                <Label>Recent Job Titles</Label>
                                                <ul className="list-disc list-inside text-gray-600 dark:text-gray-400">
                                                    {userProfile.lastThreeJobTitles?.slice(0, 3).map((title, index) => (
                                                        <li key={index}>{title}</li>
                                                    )) || <p>No recent job titles</p>}
                                                </ul>
                                            </div>
                                            <div>
                                                <Label>Recent Companies</Label>
                                                <ul className="list-disc list-inside text-gray-600 dark:text-gray-400">
                                                    {userProfile.companies?.slice(0, 4).map((company, index) => (
                                                        <li key={index}>{company}</li>
                                                    )) || <p>No company history</p>}
                                                </ul>
                                            </div>
                                            {/* Job Recommendations */}
                                            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4">
                                                <div className="flex justify-between items-center mb-3">
                                                    <Label className="text-xl font-semibold flex items-center space-x-2">
                                                        <svg className="w-6 h-6 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2-2v2m8 0H8m8 0v2a2 2 0 01-2 2H10a2 2 0 01-2-2V6m8 0H8m0 0v.01M8 6v6h8V6M8 6H6a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V8a2 2 0 00-2-2h-2" />
                                                        </svg>
                                                        <span>Job Recommendations</span>
                                                    </Label>
                                                    <Link href="/jobs">
                                                        <Button 
                                                            variant="outline" 
                                                            size="sm"
                                                            className="flex items-center space-x-2 border-purple-200 dark:border-purple-700 text-purple-600 dark:text-purple-400 hover:bg-purple-50 dark:hover:bg-purple-900/20 hover:border-purple-300 dark:hover:border-purple-600 hover:scale-105 transition-all duration-300 shadow-md hover:shadow-lg"
                                                        >
                                                            <span>View All Jobs</span>
                                                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                                                            </svg>
                                                        </Button>
                                                    </Link>
                                                </div>
                                                {loadingJobs ? (
                                                    <div className="flex items-center justify-center h-24">
                                                        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                                                    </div>
                                                ) : jobRecommendations.length > 0 ? (
                                                    <div className="space-y-3 mt-3">
                                                        {jobRecommendations.slice(0, 3).map((job) => (
                                                            <div key={job.id} className="border dark:border-gray-700 rounded-lg p-3 hover:shadow-md transition-shadow">
                                                                <h3 className="font-medium text-sm">{job.title}</h3>
                                                                <p className="text-xs text-gray-600 dark:text-gray-400">{job.company}</p>
                                                                <p className="text-xs text-gray-500 dark:text-gray-500">{job.location}</p>
                                                                <a 
                                                                    href={job.applyUrl} 
                                                                    target="_blank" 
                                                                    rel="noopener noreferrer"
                                                                    className="text-blue-600 dark:text-blue-400 text-xs hover:underline mt-1 inline-block"
                                                                >
                                                                    View Job →
                                                                </a>
                                                            </div>
                                                        ))}
                                                    </div>
                                                ) : (
                                                    <p className="text-gray-600 dark:text-gray-400 text-sm">No job recommendations available.</p>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                )}
                            </div>
                        )}

                        {/* File Upload Section */}
                        {showFileUpload && (
                            <div className="mt-8 bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6">
                                <h2 className="text-xl font-semibold mb-4 flex items-center space-x-2">
                                    <svg className="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                                    </svg>
                                    <span>Upload Your CV</span>
                                </h2>
                                
                                {!isParsingProgress ? (
                                    <Input
                                        type="file"
                                        accept=".pdf,.doc,.docx,.txt"
                                        onChange={handleFileUploadAndParse}
                                        className="mb-4"
                                        disabled={isParsingProgress}
                                    />
                                ) : (
                                    <div className="mb-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                                        <div className="flex items-center space-x-3 mb-3">
                                            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
                                            <span className="text-blue-800 dark:text-blue-200 font-medium">{parsingStep}</span>
                                        </div>
                                        
                                        {/* Animated Progress Bar */}
                                        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 mb-2">
                                            <div 
                                                className="bg-gradient-to-r from-blue-500 to-purple-600 h-3 rounded-full transition-all duration-500 ease-out relative overflow-hidden"
                                                style={{ width: `${parsingProgress}%` }}
                                            >
                                                {/* Animated shine effect */}
                                                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-pulse"></div>
                                            </div>
                                        </div>
                                        
                                        <div className="flex justify-between text-sm text-blue-700 dark:text-blue-300">
                                            <span>Processing your CV...</span>
                                            <span>{parsingProgress}%</span>
                                        </div>
                                    </div>
                                )}
                                
                                {parseErrorMessage && (
                                    <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md p-4 mb-4">
                                        <div className="flex items-center space-x-2">
                                            <svg className="w-5 h-5 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                            </svg>
                                            <p className="text-red-800 dark:text-red-200">{parseErrorMessage}</p>
                                        </div>
                                    </div>
                                )}
                                
                                {parseSuccessMessage && (
                                    <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-md p-4 mb-4">
                                        <div className="flex items-center space-x-2">
                                            <svg className="w-5 h-5 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                            </svg>
                                            <p className="text-green-800 dark:text-green-200">{parseSuccessMessage}</p>
                                        </div>
                                    </div>
                                )}
                                
                                <p className="text-sm text-gray-600 dark:text-gray-400">
                                    Supported formats: PDF, DOC, DOCX, TXT (Max 10MB)
                                </p>
                            </div>
                        )}

                        {/* Feature Cards */}
                        <div className="mt-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                            {/* Career Path Generator Card */}
                            <Link href="/career-path" className="block bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-lg hover:shadow-xl p-6 transition-all duration-300 hover:scale-105 hover:border-blue-300 dark:hover:border-blue-600 relative overflow-hidden group">
                                <CardBackgroundAnimation />
                                <div className="flex flex-col items-center text-center relative z-10">
                                    <div className="w-12 h-12 mb-4 text-blue-600 dark:text-blue-400 transition-all duration-300 group-hover:scale-125 group-hover:text-blue-700 dark:group-hover:text-blue-300">
                                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 3v11.25A2.25 2.25 0 006 16.5h2.25M3.75 3h-1.5m1.5 0h16.5m0 0h1.5m-1.5 0v11.25A2.25 2.25 0 0118 16.5h-2.25m-7.5 0h7.5m-7.5 0l-1 3m8.5-3l1 3m0 0l.5 1.5m-.5-1.5h-9.5m0 0l-.5 1.5m.75-9l3-3 2.148 2.148A12.061 12.061 0 0116.5 7.605" />
                                        </svg>
                                    </div>
                                    <h3 className="text-lg font-semibold mb-2 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors duration-300">Career Path Generator</h3>
                                    <p className="text-sm text-gray-600 dark:text-gray-400 group-hover:text-gray-700 dark:group-hover:text-gray-300 transition-colors duration-300">
                                        Map your career journey and discover potential paths based on your skills and goals.
                                    </p>
                                </div>
                            </Link>

                            {/* Skill Gap Analysis Card */}
                            <Link href="/skill-gap-analysis" className="block bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-lg hover:shadow-xl p-6 transition-all duration-300 hover:scale-105 hover:border-green-300 dark:hover:border-green-600 relative overflow-hidden group">
                                <CardBackgroundAnimation />
                                <div className="flex flex-col items-center text-center relative z-10">
                                    <div className="w-12 h-12 mb-4 text-green-600 dark:text-green-400 transition-all duration-300 group-hover:scale-125 group-hover:text-green-700 dark:group-hover:text-green-300">
                                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" d="M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0112 15a9.065 9.065 0 00-6.23-.693L5 14.5m14.8.8l1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0112 21c-2.773 0-5.491-.235-8.135-.687-1.718-.293-2.3-2.379-1.067-3.61L5 14.5" />
                                        </svg>
                                    </div>
                                    <h3 className="text-lg font-semibold mb-2 group-hover:text-green-600 dark:group-hover:text-green-400 transition-colors duration-300">Skill Gap Analysis</h3>
                                    <p className="text-sm text-gray-600 dark:text-gray-400 group-hover:text-gray-700 dark:group-hover:text-gray-300 transition-colors duration-300">
                                        Identify skill gaps and get personalized recommendations for your target roles.
                                    </p>
                                </div>
                            </Link>

                            {/* Resume Optimization Card */}
                            <Link href="/resume-optimization" className="block bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-lg hover:shadow-xl p-6 transition-all duration-300 hover:scale-105 hover:border-purple-300 dark:hover:border-purple-600 relative overflow-hidden group">
                                <CardBackgroundAnimation />
                                <div className="flex flex-col items-center text-center relative z-10">
                                    <div className="w-12 h-12 mb-4 text-purple-600 dark:text-purple-400 transition-all duration-300 group-hover:scale-125 group-hover:text-purple-700 dark:group-hover:text-purple-300">
                                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" d="M11.35 3.836c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 00.75-.75 2.25 2.25 0 00-.1-.664m-5.8 0A2.251 2.251 0 0113.5 2.25H15c1.012 0 1.867.668 2.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m8.9-4.414c.376.023.75.05 1.124.08 1.131.094 1.976 1.057 1.976 2.192V16.5A2.25 2.25 0 0118 18.75h-2.25m-7.5-10.5H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V18.75m-7.5-10.5h6.375c.621 0 1.125.504 1.125 1.125v9.375m-8.25-3l1.5 1.5 3-3.75" />
                                        </svg>
                                    </div>
                                    <h3 className="text-lg font-semibold mb-2 group-hover:text-purple-600 dark:group-hover:text-purple-400 transition-colors duration-300">Resume Optimization</h3>
                                    <p className="text-sm text-gray-600 dark:text-gray-400 group-hover:text-gray-700 dark:group-hover:text-gray-300 transition-colors duration-300">
                                        Get AI-powered suggestions to enhance your resume and increase interview chances.
                                    </p>
                                </div>
                            </Link>

                            {/* Job Recommendations Card */}
                            <Link href="/jobs" className="block bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-lg hover:shadow-xl p-6 transition-all duration-300 hover:scale-105 hover:border-orange-300 dark:hover:border-orange-600 relative overflow-hidden group">
                                <CardBackgroundAnimation />
                                <div className="flex flex-col items-center text-center relative z-10">
                                    <div className="w-12 h-12 mb-4 text-orange-600 dark:text-orange-400 transition-all duration-300 group-hover:scale-125 group-hover:text-orange-700 dark:group-hover:text-orange-300">
                                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" d="M20.25 14.15v4.25c0 1.094-.787 2.036-1.872 2.18-2.087.277-4.216.42-6.378.42s-4.291-.143-6.378-.42c-1.085-.144-1.872-1.086-1.872-2.18v-4.25m16.5 0a2.18 2.18 0 00.75-1.661V8.706c0-1.081-.768-2.015-1.837-2.175a48.114 48.114 0 00-3.413-.387m4.5 8.006c-.194.165-.42.295-.673.38A23.978 23.978 0 0112 15.75c-2.648 0-5.195-.429-7.577-1.22a2.016 2.016 0 01-.673-.38m0 0A2.18 2.18 0 013 12.489V8.706c0-1.081.768-2.015 1.837-2.175a48.111 48.111 0 013.413-.387m7.5 0V5.25A2.25 2.25 0 0013.5 3h-3a2.25 2.25 0 00-2.25 2.25v.894m7.5 0a48.667 48.667 0 00-7.5 0M12 12.75h.008v.008H12v-.008z" />
                                        </svg>
                                    </div>
                                    <h3 className="text-lg font-semibold mb-2 group-hover:text-orange-600 dark:group-hover:text-orange-400 transition-colors duration-300">Job Recommendations</h3>
                                    <p className="text-sm text-gray-600 dark:text-gray-400 group-hover:text-gray-700 dark:group-hover:text-gray-300 transition-colors duration-300">
                                        Discover AI-matched job opportunities tailored to your skills and experience.
                                    </p>
                                </div>
                            </Link>
                        </div>
                    </>
                )}
            </div>
        </div>
    );
}