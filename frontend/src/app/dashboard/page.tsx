"use client";

import { useState, useEffect } from "react";
import { useAuth, useUser, SignOutButton } from "@clerk/nextjs";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Label } from "@/components/ui/Label";
import Link from "next/link";
import SkillsWordCloud from "@/components/ui/SkillsWordCloud";

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
}

export default function Dashboard() {
    const { getToken } = useAuth();
    const { isLoaded, isSignedIn, user } = useUser();
    const router = useRouter();
    
    // State management
    const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
    const [parsedResumeData, setParsedResumeData] = useState<UserProfile | null>(null);  // For new users' parsed data
    const [tempProfile, setTempProfile] = useState<UserProfile | null>(null);  // For editing before save
    const [uploadedFile, setUploadedFile] = useState<File | null>(null);
    const [isLoadingProfile, setIsLoadingProfile] = useState(true);
    const [isExistingUser, setIsExistingUser] = useState(false);
    const [savedCvId, setSavedCvId] = useState<string | null>(null);
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
    }, [isLoaded, isSignedIn, user?.id]);

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

            // Set the parsed data
            setParsedResumeData(result.parsed_data);
            
            // Save to localStorage for jobs page
            localStorage.setItem('userProfile', JSON.stringify(result.parsed_data));
            
            setParsingProgress(100);
            setParsingStep("Complete!");

            // Show success message
            setParseSuccessMessage(`✅ Resume parsed successfully! Extracted profile for: ${result.parsed_data.firstName || 'User'} ${result.parsed_data.lastName || ''}`);
            
            // Fetch job recommendations after successful resume parsing
            await fetchJobRecommendations(result.parsed_data);
            
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
            
            // Update user profile with new data
            setUserProfile(result.parsed_data);
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
    const fetchJobRecommendations = async (profile: UserProfile) => {
        setLoadingJobs(true);
        try {
            const token = await getToken();
            
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
                    location: null
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            setJobRecommendations(data.jobs || []);

        } catch (error) {
            console.error('Error fetching job recommendations:', error);
            // Silently fail - don't show error to user for job recommendations
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
            const response = await fetch('/api/save-cv', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${token}`,
                },
                body: JSON.stringify({
                    user_id: user.id,
                    filename: 'profile_data.json',
                    file_type: 'application/json',
                    raw_text: JSON.stringify(editableProfile),
                    parsed_data: editableProfile,
                }),
            });

            if (!response.ok) {
                throw new Error('Failed to save profile');
            }

            const result = await response.json();
            
            // Update user profile with edited data
            setUserProfile(editableProfile);
            setEditableProfile(null);
            setIsEditingProfile(false);
            setSavedCvId(result.cv_record_id);
            setLastUpdated(new Date().toISOString());
            setParseSuccessMessage('✅ Profile updated successfully!');
            
            // Save to localStorage
            localStorage.setItem('userProfile', JSON.stringify(editableProfile));
            
            // Fetch new job recommendations based on updated profile
            await fetchJobRecommendations(editableProfile);
            
        } catch (error) {
            console.error('Error saving profile:', error);
            setParseErrorMessage('Error saving profile. Please try again.');
        } finally {
            setIsSavingProfile(false);
        }
    };

    // Save CV to database
    const handleSaveCV = async () => {
        if (!parsedResumeData) return;

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
                    filename: 'profile_data.json',
                    file_type: 'application/json',
                    raw_text: JSON.stringify(parsedResumeData),
                    parsed_data: parsedResumeData,
                }),
            });

            if (!response.ok) {
                throw new Error('Failed to save CV');
            }

            const result = await response.json();
            
            // After successful save, move parsed data to user profile and mark as existing user
            setUserProfile(parsedResumeData);
            setParsedResumeData(null);
            setIsExistingUser(true);
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
            <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
                <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
                    <div className="container mx-auto px-4 py-4 flex justify-between items-center">
                        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Career Compass AI</h1>
                        <div className="flex items-center space-x-4">
                            <SignOutButton>
                                <Button variant="outline" size="sm">
                                    Sign Out
                                </Button>
                            </SignOutButton>
                        </div>
                    </div>
                </header>
                <div className="flex items-center justify-center min-h-96">
                    <div className="text-center">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                        <div className="text-lg text-gray-600 dark:text-gray-300">Loading your profile...</div>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
            {/* Header */}
            <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
                <div className="container mx-auto px-4 py-4 flex justify-between items-center">
                    <div className="flex items-center space-x-3">
                        {/* Beautiful Compass Logo */}
                        <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-xl flex items-center justify-center shadow-lg">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
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
                        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Career Compass AI</h1>
                    </div>
                    <div className="flex items-center space-x-4">
                        <SignOutButton>
                            <Button variant="outline" size="sm">
                                Sign Out
                            </Button>
                        </SignOutButton>
                    </div>
                </div>
            </header>

            {/* Welcome Message Below Header */}
            {(isLoaded && isSignedIn && user) && (
                <div className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 border-b border-gray-200 dark:border-gray-700">
                    <div className="container mx-auto px-4 py-6">
                        <div className="flex items-center space-x-4">
                            {/* Profile Image */}
                            <div className="flex-shrink-0">
                                {user.imageUrl ? (
                                    <img 
                                        src={user.imageUrl} 
                                        alt={`${user.firstName || 'User'}'s profile`}
                                        className="w-16 h-16 rounded-full border-4 border-white dark:border-gray-700 shadow-md object-cover"
                                    />
                                ) : (
                                    <div className="w-16 h-16 rounded-full bg-blue-500 border-4 border-white dark:border-gray-700 shadow-md flex items-center justify-center">
                                        <span className="text-2xl font-bold text-white">
                                            {(user.firstName || 'U').charAt(0).toUpperCase()}
                                        </span>
                                    </div>
                                )}
                            </div>
                            
                            {/* Welcome Message */}
                            <div className="flex-1">
                                <h2 className="text-2xl font-bold text-gray-800 dark:text-white">
                                    Hey {user.firstName || 'there'}, Welcome!! 👋
                                </h2>
                                <p className="text-gray-600 dark:text-gray-300 mt-1">
                                    Ready to accelerate your career journey?
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            <div className="container mx-auto p-4 space-y-8">
                


                {/* Welcome Section for New Users */}
                {!isExistingUser && !parsedResumeData && (
                    <div className="text-center py-12">
                        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-8 max-w-2xl mx-auto">
                            <div className="mb-6">
                                <div className="w-20 h-20 bg-blue-100 dark:bg-blue-900/30 rounded-full flex items-center justify-center mx-auto mb-4">
                                    <svg className="w-10 h-10 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                    </svg>
                                </div>
                                <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">Welcome to Career Compass AI! 🎯</h2>
                                <p className="text-lg text-gray-600 dark:text-gray-300 mb-8">
                                    Let's get started by uploading your resume. Our AI will analyze it and help you find the perfect job opportunities!
                                </p>
                            </div>
                            
                            <div className="space-y-4">
                                <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                                    <h3 className="font-semibold text-blue-900 dark:text-blue-100 mb-2">What happens next?</h3>
                                    <ul className="text-sm text-blue-800 dark:text-blue-200 space-y-1 text-left">
                                        <li className="flex items-center"><span className="w-2 h-2 bg-blue-400 rounded-full mr-2"></span>Upload your resume (PDF, DOC, DOCX, or TXT)</li>
                                        <li className="flex items-center"><span className="w-2 h-2 bg-blue-400 rounded-full mr-2"></span>Our AI extracts your skills, experience, and education</li>
                                        <li className="flex items-center"><span className="w-2 h-2 bg-blue-400 rounded-full mr-2"></span>Review and save your profile</li>
                                        <li className="flex items-center"><span className="w-2 h-2 bg-blue-400 rounded-full mr-2"></span>Get personalized job recommendations!</li>
                                    </ul>
                                </div>
                                
                                <Button 
                                    onClick={() => document.getElementById('resume-upload')?.click()}
                                    className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 text-lg font-medium"
                                    disabled={isParsingProgress}
                                >
                                    {isParsingProgress ? (
                                        <>
                                            <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent mr-2"></div>
                                            Processing...
                                        </>
                                    ) : (
                                        "📤 Upload Your Resume"
                                    )}
                                </Button>
                            </div>
                        </div>
                    </div>
                )}

                {/* Hidden File Input (for new users) */}
                {!isExistingUser && (
                    <input
                        id="resume-upload"
                        type="file"
                        accept=".pdf,.doc,.docx,.txt"
                        onChange={handleFileUploadAndParse}
                        className="hidden"
                        disabled={isParsingProgress}
                    />
                )}

                {/* Progress Bar for new users */}
                {!isExistingUser && isParsingProgress && (
                    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
                        <div className="space-y-3">
                            <div className="flex items-center justify-between">
                                <span className="text-sm font-medium text-blue-700 dark:text-blue-400">{parsingStep}</span>
                                <span className="text-sm text-gray-500 dark:text-gray-400">{parsingProgress}%</span>
                            </div>
                            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                                <div 
                                    className="bg-blue-600 dark:bg-blue-500 h-2 rounded-full transition-all duration-500 ease-out"
                                    style={{ width: `${parsingProgress}%` }}
                                ></div>
                            </div>
                            <div className="flex items-center space-x-2 text-blue-600 dark:text-blue-400">
                                <div className="animate-spin rounded-full h-4 w-4 border-2 border-blue-600 dark:border-blue-400 border-t-transparent"></div>
                                <span className="text-sm">Processing your resume...</span>
                            </div>
                        </div>
                    </div>
                )}

                {/* File Info for new users */}
                {!isExistingUser && uploadedFile && !isParsingProgress && (
                    <div className="bg-white rounded-lg shadow-md p-6">
                        <div className="bg-gray-50 rounded-lg p-3">
                            <p className="text-sm text-gray-600">
                                <strong>Selected:</strong> {uploadedFile.name} ({(uploadedFile.size / 1024 / 1024).toFixed(2)} MB)
                            </p>
                        </div>
                    </div>
                )}

                {/* Error Messages for new users */}
                {!isExistingUser && parseErrorMessage && (
                    <div className="bg-white rounded-lg shadow-md p-6">
                        {/* Error Message */}
                        <div className="flex items-center space-x-2 text-red-700 bg-red-50 border border-red-200 rounded-md p-4">
                            <svg className="w-5 h-5 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                            </svg>
                            <span className="font-medium">{parseErrorMessage}</span>
                        </div>
                    </div>
                )}



                {/* Resume Preview Section - For parsed but unsaved resume data */}
                {!isExistingUser && parsedResumeData && (
                    <div className="space-y-6">
                        {/* Resume Preview Section */}
                        <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-blue-500">
                            <div className="flex justify-between items-center mb-6">
                                <h2 className="text-2xl font-bold text-gray-800">📄 Resume Preview</h2>
                                <Button 
                                    onClick={handleSaveCV}
                                    disabled={isSavingProfile}
                                    className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 font-medium"
                                >
                                    {isSavingProfile ? (
                                        <>
                                            <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent mr-2"></div>
                                            Saving...
                                        </>
                                    ) : (
                                        <>💾 Save as My Profile</>
                                    )}
                                </Button>
                            </div>
                            
                            <div className="bg-blue-50 border border-blue-200 rounded-md p-4 mb-6">
                                <div className="flex items-center space-x-2">
                                    <svg className="w-5 h-5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                                        <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                                    </svg>
                                    <span className="text-blue-800 font-medium">This is a preview of your parsed resume data. Click "Save as My Profile" to save it permanently.</span>
                                </div>
                            </div>

                            {/* Success/Error Messages */}
                            {parseSuccessMessage && (
                                <div className="flex items-center space-x-2 text-green-700 bg-green-50 border border-green-200 rounded-md p-4 mb-6">
                                    <svg className="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                                    </svg>
                                    <span className="font-medium">{parseSuccessMessage}</span>
                                </div>
                            )}
                            
                            {parseErrorMessage && (
                                <div className="flex items-center space-x-2 text-red-700 bg-red-50 border border-red-200 rounded-md p-4 mb-6">
                                    <svg className="w-5 h-5 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                                    </svg>
                                    <span className="font-medium">{parseErrorMessage}</span>
                                </div>
                            )}

                            {/* Profile Information Grid - Same as above but for preview */}
                            <div className="grid md:grid-cols-2 gap-8">
                                {/* Personal Information Section */}
                                <div className="space-y-6">
                                    <div>
                                        <h3 className="text-lg font-semibold text-gray-800 mb-4 border-b-2 border-blue-100 pb-2">
                                            📋 Personal Information
                                        </h3>
                                        <div className="space-y-3">
                                            <div className="flex items-center">
                                                <span className="font-medium text-gray-600 w-20">Name:</span>
                                                <span className="text-gray-900 text-lg font-medium ml-2">{parsedResumeData.firstName || ""} {parsedResumeData.lastName || ""}</span>
                                            </div>
                                            {parsedResumeData.email && (
                                                <div className="flex items-center">
                                                    <span className="font-medium text-gray-600 w-20">Email:</span>
                                                    <span className="text-gray-900 ml-2">{parsedResumeData.email}</span>
                                                </div>
                                            )}
                                            {parsedResumeData.phone && (
                                                <div className="flex items-center">
                                                    <span className="font-medium text-gray-600 w-20">Phone:</span>
                                                    <span className="text-gray-900 ml-2">{parsedResumeData.phone}</span>
                                                </div>
                                            )}
                                            {parsedResumeData.location && (
                                                <div className="flex items-center">
                                                    <span className="font-medium text-gray-600 w-20">Country:</span>
                                                    <span className="text-gray-900 ml-2 flex items-center">
                                                        <span className="mr-2">🌍</span>
                                                        {parsedResumeData.location}
                                                    </span>
                                                </div>
                                            )}
                                        </div>
                                    </div>

                                    {/* Experience Information */}
                                    <div>
                                        <h3 className="text-lg font-semibold text-gray-800 mb-4 border-b-2 border-green-100 pb-2">
                                            💼 Experience
                                        </h3>
                                        <div className="space-y-3">
                                            <div className="flex items-center">
                                                <span className="font-medium text-gray-600 w-24">Experience:</span>
                                                <span className="text-gray-900 text-lg font-medium ml-2">{parsedResumeData.experienceYears} years</span>
                                            </div>
                                            <div className="flex items-start">
                                                <span className="font-medium text-gray-600 w-24 mt-1">Companies:</span>
                                                <div className="ml-2 space-y-1">
                                                    {parsedResumeData.companies.map((company, index) => (
                                                        <div key={index} className="flex items-center space-x-2">
                                                            <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                                                            <span className="text-gray-900">{company}</span>
                                                        </div>
                                                    ))}
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                {/* Professional Information Section */}
                                <div className="space-y-6">
                                    {/* Last 3 Job Titles */}
                                    <div>
                                        <h3 className="text-lg font-semibold text-gray-800 mb-4 border-b-2 border-purple-100 pb-2">
                                            🎯 Recent Job Titles
                                        </h3>
                                        {parsedResumeData.lastThreeJobTitles && parsedResumeData.lastThreeJobTitles.length > 0 ? (
                                            <div className="space-y-2">
                                                {parsedResumeData.lastThreeJobTitles.map((job, index) => (
                                                    <div key={index} className="flex items-center space-x-2">
                                                        <div className="w-2 h-2 bg-purple-400 rounded-full"></div>
                                                        <span className="text-gray-900 font-medium">{job}</span>
                                                    </div>
                                                ))}
                                            </div>
                                        ) : (
                                            <p className="text-gray-500 italic">No job titles found</p>
                                        )}
                                    </div>

                                    {/* Education Section */}
                                    {parsedResumeData.education && parsedResumeData.education.length > 0 && (
                                        <div>
                                            <h3 className="text-lg font-semibold text-gray-800 mb-4 border-b-2 border-green-100 pb-2">
                                                🎓 Education
                                            </h3>
                                            <div className="space-y-2">
                                                {parsedResumeData.education.map((edu, index) => (
                                                    <div key={index} className="flex items-center space-x-2">
                                                        <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                                                        <span className="text-gray-900">{edu}</span>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    {/* Certifications Section */}
                                    {parsedResumeData.certifications && parsedResumeData.certifications.length > 0 && (
                                        <div>
                                            <h3 className="text-lg font-semibold text-gray-800 mb-4 border-b-2 border-yellow-100 pb-2">
                                                🏆 Certifications
                                            </h3>
                                            <div className="space-y-2">
                                                {parsedResumeData.certifications.map((cert, index) => (
                                                    <div key={index} className="flex items-center space-x-2">
                                                        <div className="w-2 h-2 bg-yellow-400 rounded-full"></div>
                                                        <span className="text-gray-900">{cert}</span>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    {/* Professional Summary */}
                                    {parsedResumeData.experienceSummary && (
                                        <div>
                                            <h3 className="text-lg font-semibold text-gray-800 mb-4 border-b-2 border-orange-100 pb-2">
                                                📝 Experience Summary
                                            </h3>
                                            <p className="text-gray-700 leading-relaxed">{parsedResumeData.experienceSummary}</p>
                                        </div>
                                    )}
                                </div>
                            </div>

                            {/* Skills Section - Full Width */}
                            <div className="mt-8 pt-6 border-t border-gray-200">
                                <h3 className="text-lg font-semibold text-gray-800 mb-4 border-b-2 border-blue-100 pb-2">
                                    🛠️ Skills Word Cloud
                                </h3>
                                <SkillsWordCloud skills={parsedResumeData.skills || []} />
                            </div>
                        </div>

                        {/* Job Recommendations for Preview - Optional */}
                        {jobRecommendations.length > 0 && (
                            <div className="bg-white rounded-lg shadow-md p-6">
                                <div className="flex justify-between items-center mb-6">
                                    <h2 className="text-2xl font-bold text-gray-800">💼 Potential Jobs for You</h2>
                                    <span className="text-sm text-gray-500 bg-gray-100 px-3 py-1 rounded-full">Preview</span>
                                </div>
                                
                                <div className="bg-amber-50 border border-amber-200 rounded-md p-4 mb-6">
                                    <div className="flex items-center space-x-2">
                                        <svg className="w-5 h-5 text-amber-600" fill="currentColor" viewBox="0 0 20 20">
                                            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                                        </svg>
                                        <span className="text-amber-800 font-medium">Save your profile to get full access to job recommendations and personalized features.</span>
                                    </div>
                                </div>
                                
                                <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                                    {jobRecommendations.slice(0, 3).map((job) => (
                                        <div key={job.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-lg transition-shadow opacity-75">
                                            <h3 className="font-semibold text-lg text-gray-900 mb-2">{job.title}</h3>
                                            <p className="text-gray-600 mb-2">{job.company}</p>
                                            <p className="text-gray-500 text-sm mb-3">{job.location}</p>
                                            {job.salary && (
                                                <p className="text-green-600 font-medium text-sm mb-3">{job.salary}</p>
                                            )}
                                            <p className="text-gray-700 text-sm mb-4 line-clamp-3">{job.description}</p>
                                            <div className="flex justify-between items-center">
                                                <span className="text-xs text-gray-500">
                                                    {job.daysAgo !== undefined ? `${job.daysAgo} days ago` : job.postedDate}
                                                </span>
                                                <a href={job.applyUrl} target="_blank" rel="noopener noreferrer">
                                                    <Button size="sm" className="bg-blue-600 hover:bg-blue-700">
                                                        Apply
                                                    </Button>
                                                </a>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                )}

                {/* Upload CV Section for Existing Users */}
                {isExistingUser && userProfile && (
                    <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-green-500">
                        <div className="flex justify-between items-center mb-6">
                            <div className="flex items-center space-x-4">
                                <div>
                                    <h2 className="text-2xl font-bold text-gray-800">👤 Your Profile</h2>
                                    {lastUpdated && (
                                        <p className="text-sm text-gray-500 mt-1">Last updated: {lastUpdated}</p>
                                    )}
                                </div>
                                <div className="flex space-x-2">
                                    <Button 
                                        onClick={handleEditProfile}
                                        className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 font-medium"
                                        disabled={isUploading || isEditingProfile}
                                    >
                                        ✏️ Edit Profile
                                    </Button>
                                    <Button 
                                        onClick={() => document.getElementById('cv-update-upload')?.click()}
                                        className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 font-medium"
                                        disabled={isUploading || isEditingProfile}
                                    >
                                        {isUploading ? (
                                            <>
                                                <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent mr-2"></div>
                                                Updating...
                                            </>
                                        ) : (
                                            <>📤 Update CV</>
                                        )}
                                    </Button>
                                </div>
                            </div>
                        </div>

                        {/* Hidden File Input for Existing Users */}
                        <input
                            id="cv-update-upload"
                            type="file"
                            accept=".pdf,.doc,.docx,.txt"
                            onChange={handleUpdateCV}
                            className="hidden"
                            disabled={isUploading}
                        />

                        {/* Success/Error Messages for Profile Updates */}
                        {parseSuccessMessage && (
                            <div className="flex items-center space-x-2 text-green-700 bg-green-50 border border-green-200 rounded-md p-4 mb-6">
                                <svg className="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                                </svg>
                                <span className="font-medium">{parseSuccessMessage}</span>
                            </div>
                        )}
                        
                        {parseErrorMessage && (
                            <div className="flex items-center space-x-2 text-red-700 bg-red-50 border border-red-200 rounded-md p-4 mb-6">
                                <svg className="w-5 h-5 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                                </svg>
                                <span className="font-medium">{parseErrorMessage}</span>
                            </div>
                        )}

                        {/* Editable Profile Form */}
                        {isEditingProfile && editableProfile && (
                            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
                                <div className="flex justify-between items-center mb-6">
                                    <h3 className="text-xl font-bold text-gray-800">✏️ Edit Your Profile</h3>
                                    <div className="flex space-x-2">
                                        <Button 
                                            onClick={handleSaveProfile}
                                            disabled={isSavingProfile}
                                            className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 font-medium"
                                        >
                                            {isSavingProfile ? (
                                                <>
                                                    <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent mr-2"></div>
                                                    Saving...
                                                </>
                                            ) : (
                                                <>💾 Save Profile</>
                                            )}
                                        </Button>
                                        <Button 
                                            onClick={handleCancelEdit}
                                            disabled={isSavingProfile}
                                            variant="outline"
                                            className="px-4 py-2 font-medium"
                                        >
                                            Cancel
                                        </Button>
                                    </div>
                                </div>
                                
                                <div className="grid md:grid-cols-2 gap-6">
                                    {/* Personal Information */}
                                    <div className="space-y-4">
                                        <h4 className="font-semibold text-gray-800 border-b pb-2">Personal Information</h4>
                                        <div className="space-y-3">
                                            <div>
                                                <Label htmlFor="firstName">First Name</Label>
                                                <Input
                                                    id="firstName"
                                                    value={editableProfile.firstName}
                                                    onChange={(e) => setEditableProfile({...editableProfile, firstName: e.target.value})}
                                                    className="mt-1"
                                                />
                                            </div>
                                            <div>
                                                <Label htmlFor="lastName">Last Name</Label>
                                                <Input
                                                    id="lastName"
                                                    value={editableProfile.lastName}
                                                    onChange={(e) => setEditableProfile({...editableProfile, lastName: e.target.value})}
                                                    className="mt-1"
                                                />
                                            </div>
                                            <div>
                                                <Label htmlFor="email">Email</Label>
                                                <Input
                                                    id="email"
                                                    type="email"
                                                    value={editableProfile.email || ''}
                                                    onChange={(e) => setEditableProfile({...editableProfile, email: e.target.value})}
                                                    className="mt-1"
                                                />
                                            </div>
                                            <div>
                                                <Label htmlFor="phone">Phone</Label>
                                                <Input
                                                    id="phone"
                                                    value={editableProfile.phone || ''}
                                                    onChange={(e) => setEditableProfile({...editableProfile, phone: e.target.value})}
                                                    className="mt-1"
                                                />
                                            </div>
                                            <div>
                                                <Label htmlFor="location">Country</Label>
                                                <Input
                                                    id="location"
                                                    value={editableProfile.location || ''}
                                                    onChange={(e) => setEditableProfile({...editableProfile, location: e.target.value})}
                                                    placeholder="e.g., Netherlands, United States, Germany"
                                                    className="mt-1"
                                                />
                                            </div>
                                        </div>
                                    </div>
                                    
                                    {/* Experience Information */}
                                    <div className="space-y-4">
                                        <h4 className="font-semibold text-gray-800 border-b pb-2">Experience</h4>
                                        <div className="space-y-3">
                                            <div>
                                                <Label htmlFor="experienceYears">Years of Experience</Label>
                                                <Input
                                                    id="experienceYears"
                                                    type="number"
                                                    value={editableProfile.experienceYears}
                                                    onChange={(e) => setEditableProfile({...editableProfile, experienceYears: parseInt(e.target.value) || 0})}
                                                    className="mt-1"
                                                />
                                            </div>
                                            <div>
                                                <Label htmlFor="experienceSummary">Experience Summary</Label>
                                                <textarea
                                                    id="experienceSummary"
                                                    value={editableProfile.experienceSummary}
                                                    onChange={(e) => setEditableProfile({...editableProfile, experienceSummary: e.target.value})}
                                                    className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                                    rows={4}
                                                />
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Main Layout: Profile on Left, Jobs on Right */}
                        <div className="grid lg:grid-cols-3 gap-8">
                            {/* Profile Information - Left Side (2/3 width) */}
                            <div className="lg:col-span-2 space-y-8">
                                {/* Personal Information and Experience Grid */}
                                <div className="grid md:grid-cols-2 gap-6">
                                    {/* Personal Information Section */}
                                    <div>
                                        <h3 className="text-lg font-semibold text-gray-800 mb-4 border-b-2 border-blue-100 pb-2">
                                            📋 Personal Information
                                        </h3>
                                        <div className="space-y-3">
                                            <div className="flex items-center">
                                                <span className="font-medium text-gray-600 w-20">Name:</span>
                                                <span className="text-gray-900 text-lg font-medium ml-2">{userProfile.firstName || ""} {userProfile.lastName || ""}</span>
                                            </div>
                                            {userProfile.email && (
                                                <div className="flex items-center">
                                                    <span className="font-medium text-gray-600 w-20">Email:</span>
                                                    <span className="text-gray-900 ml-2">{userProfile.email}</span>
                                                </div>
                                            )}
                                            {userProfile.phone && (
                                                <div className="flex items-center">
                                                    <span className="font-medium text-gray-600 w-20">Phone:</span>
                                                    <span className="text-gray-900 ml-2">{userProfile.phone}</span>
                                                </div>
                                            )}
                                            {userProfile.location && (
                                                <div className="flex items-center">
                                                    <span className="font-medium text-gray-600 w-20">Country:</span>
                                                    <span className="text-gray-900 ml-2 flex items-center">
                                                        <span className="mr-2">🌍</span>
                                                        {userProfile.location}
                                                    </span>
                                                </div>
                                            )}
                                        </div>
                                    </div>

                                    {/* Experience Information */}
                                    <div>
                                        <h3 className="text-lg font-semibold text-gray-800 mb-4 border-b-2 border-green-100 pb-2">
                                            💼 Experience
                                        </h3>
                                        <div className="space-y-3">
                                            <div className="flex items-center">
                                                <span className="font-medium text-gray-600 w-24">Experience:</span>
                                                <span className="text-gray-900 text-lg font-medium ml-2">{userProfile.experienceYears} years</span>
                                            </div>
                                            <div className="flex items-start">
                                                <span className="font-medium text-gray-600 w-24 mt-1">Companies:</span>
                                                <div className="ml-2 space-y-1">
                                                    {userProfile.companies.map((company, index) => (
                                                        <div key={index} className="flex items-center space-x-2">
                                                            <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                                                            <span className="text-gray-900">{company}</span>
                                                        </div>
                                                    ))}
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                {/* Additional Professional Information - Below Experience */}
                                <div className="grid md:grid-cols-2 gap-6">
                                    {/* Recent Job Titles */}
                                    <div>
                                        <h3 className="text-lg font-semibold text-gray-800 mb-4 border-b-2 border-purple-100 pb-2">
                                            🎯 Recent Job Titles
                                        </h3>
                                        {userProfile.lastThreeJobTitles && userProfile.lastThreeJobTitles.length > 0 ? (
                                            <div className="space-y-2">
                                                {userProfile.lastThreeJobTitles.map((job, index) => (
                                                    <div key={index} className="flex items-center space-x-2">
                                                        <div className="w-2 h-2 bg-purple-400 rounded-full"></div>
                                                        <span className="text-gray-900 font-medium">{job}</span>
                                                    </div>
                                                ))}
                                            </div>
                                        ) : (
                                            <p className="text-gray-500 italic">No job titles found</p>
                                        )}
                                    </div>

                                    {/* Education Section */}
                                    {userProfile.education && userProfile.education.length > 0 && (
                                        <div>
                                            <h3 className="text-lg font-semibold text-gray-800 mb-4 border-b-2 border-green-100 pb-2">
                                                🎓 Education
                                            </h3>
                                            <div className="space-y-2">
                                                {userProfile.education.map((edu, index) => (
                                                    <div key={index} className="flex items-center space-x-2">
                                                        <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                                                        <span className="text-gray-900">{edu}</span>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </div>

                                {/* Certifications and Experience Summary */}
                                <div className="grid md:grid-cols-2 gap-6">
                                    {/* Certifications Section */}
                                    {userProfile.certifications && userProfile.certifications.length > 0 && (
                                        <div>
                                            <h3 className="text-lg font-semibold text-gray-800 mb-4 border-b-2 border-yellow-100 pb-2">
                                                🏆 Certifications
                                            </h3>
                                            <div className="space-y-2">
                                                {userProfile.certifications.map((cert, index) => (
                                                    <div key={index} className="flex items-center space-x-2">
                                                        <div className="w-2 h-2 bg-yellow-400 rounded-full"></div>
                                                        <span className="text-gray-900">{cert}</span>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    {/* Experience Summary */}
                                    {userProfile.experienceSummary && (
                                        <div>
                                            <h3 className="text-lg font-semibold text-gray-800 mb-4 border-b-2 border-orange-100 pb-2">
                                                📝 Experience Summary
                                            </h3>
                                            <p className="text-gray-700 leading-relaxed">{userProfile.experienceSummary}</p>
                                        </div>
                                    )}
                                </div>

                                {/* Skills Section - Full Width */}
                                <div className="pt-6 border-t border-gray-200">
                                    <h3 className="text-lg font-semibold text-gray-800 mb-4 border-b-2 border-blue-100 pb-2">
                                        🛠️ Skills Word Cloud
                                    </h3>
                                    <SkillsWordCloud skills={userProfile.skills || []} />
                                </div>
                            </div>

                            {/* Job Recommendations - Right Side (1/3 width) */}
                            {jobRecommendations.length > 0 && (
                                <div className="lg:col-span-1">
                                    <div className="sticky top-6">
                                        <div className="bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-6">
                                            <div className="flex justify-between items-center mb-6">
                                                <h3 className="text-xl font-bold text-blue-900">💼 Recommended Jobs</h3>
                                                <Link href="/jobs">
                                                    <Button variant="outline" size="sm" className="text-blue-700 border-blue-300 hover:bg-blue-100">
                                                        View All
                                                    </Button>
                                                </Link>
                                            </div>
                                            
                                            <div className="space-y-4">
                                                {jobRecommendations.slice(0, 4).map((job) => (
                                                    <div key={job.id} className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                                                        <h4 className="font-semibold text-lg text-gray-900 mb-2 line-clamp-2">{job.title}</h4>
                                                        <p className="text-gray-600 mb-1 font-medium">{job.company}</p>
                                                        <p className="text-gray-500 text-sm mb-2">{job.location}</p>
                                                        {job.salary && (
                                                            <p className="text-green-600 font-medium text-sm mb-3">{job.salary}</p>
                                                        )}
                                                        <p className="text-gray-700 text-sm mb-4 line-clamp-2">{job.description}</p>
                                                        <div className="flex justify-between items-center">
                                                            <span className="text-xs text-gray-500">
                                                                {job.daysAgo !== undefined ? `${job.daysAgo} days ago` : job.postedDate}
                                                            </span>
                                                            <a href={job.applyUrl} target="_blank" rel="noopener noreferrer">
                                                                <Button size="sm" className="bg-blue-600 hover:bg-blue-700">
                                                                    Apply
                                                                </Button>
                                                            </a>
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {/* AI Tools Navigation Section */}
                <div className="bg-white rounded-lg shadow-md p-6">
                    <h2 className="text-2xl font-bold mb-6 text-center">🤖 AI-Powered Career Tools</h2>
                    <p className="text-gray-600 text-center mb-8">
                        Choose from our suite of AI tools to accelerate your career growth
                    </p>
                    
                    <div className="grid md:grid-cols-3 gap-6">
                        {/* Career Path Generator Card */}
                        <div className="bg-gradient-to-br from-blue-50 to-indigo-100 border border-blue-200 rounded-lg p-6 hover:shadow-lg transition-shadow">
                            <div className="text-center">
                                <div className="text-4xl mb-4">🚀</div>
                                <h3 className="text-xl font-bold text-blue-900 mb-3">Career Path Generator</h3>
                                <p className="text-blue-700 text-sm mb-6">
                                    Get personalized career roadmaps based on your skills and experience. Discover potential career trajectories and required skills.
                                </p>
                                <Link href="/career-path">
                                    <Button className="w-full bg-blue-600 hover:bg-blue-700">
                                        Generate Career Path
                                    </Button>
                                </Link>
                            </div>
                        </div>

                        {/* Skill Gap Analysis Card */}
                        <div className="bg-gradient-to-br from-green-50 to-emerald-100 border border-green-200 rounded-lg p-6 hover:shadow-lg transition-shadow">
                            <div className="text-center">
                                <div className="text-4xl mb-4">📊</div>
                                <h3 className="text-xl font-bold text-green-900 mb-3">Skill Gap Analysis</h3>
                                <p className="text-green-700 text-sm mb-6">
                                    Compare your skills with job requirements. Identify gaps and get personalized learning recommendations.
                                </p>
                                <Link href="/skill-gap-analysis">
                                    <Button className="w-full bg-green-600 hover:bg-green-700">
                                        Analyze Skills
                                    </Button>
                                </Link>
                            </div>
                        </div>

                        {/* Resume Optimization Card */}
                        <div className="bg-gradient-to-br from-purple-50 to-pink-100 border border-purple-200 rounded-lg p-6 hover:shadow-lg transition-shadow">
                            <div className="text-center">
                                <div className="text-4xl mb-4">📝</div>
                                <h3 className="text-xl font-bold text-purple-900 mb-3">Resume Optimization</h3>
                                <p className="text-purple-700 text-sm mb-6">
                                    Optimize your resume for specific jobs. Get AI suggestions for better ATS compatibility and recruiter appeal.
                                </p>
                                <Link href="/resume-optimization">
                                    <Button className="w-full bg-purple-600 hover:bg-purple-700">
                                        Optimize Resume
                                    </Button>
                                </Link>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
} 