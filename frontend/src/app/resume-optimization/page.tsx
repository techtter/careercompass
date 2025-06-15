"use client";

import { useState, useEffect } from "react";
import { useAuth, useUser, SignOutButton } from "@clerk/nextjs";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/Button";
import { Label } from "@/components/ui/Label";
import { Textarea } from "@/components/ui/Textarea";
import { ThemeToggle } from "@/components/ui/ThemeToggle";
import Link from "next/link";
import ReactMarkdown from "react-markdown";

interface CVRecord {
    id: string;
    user_id: string;
    filename: string;
    raw_text: string;
    name?: string;
    email?: string;
    phone?: string;
    location?: string;
    experience?: string;
    skills?: string;
    education?: string;
    summary?: string;
    created_at: string;
    updated_at: string;
}

// Utility function to detect if text is JSON
const isJsonString = (str: string): boolean => {
    try {
        const parsed = JSON.parse(str);
        return typeof parsed === 'object' && parsed !== null;
    } catch {
        return false;
    }
};

// Utility function to format CV content consistently
const formatCvContent = (rawText: string, cvRecord: CVRecord): string => {
    if (!rawText) {
        // Create fallback CV content from structured data
        return createFallbackCvContent(cvRecord);
    }

    // Check if raw_text is a JSON string (from old saves)
    if (isJsonString(rawText)) {
        try {
            const parsedData = JSON.parse(rawText);
            return createCvFromParsedData(parsedData);
        } catch {
            return createFallbackCvContent(cvRecord);
        }
    }

    // Return the original CV text as-is
    return rawText;
};

// Create CV content from parsed JSON data
const createCvFromParsedData = (data: any): string => {
    const sections = [];
    
    // Header
    if (data.firstName || data.lastName) {
        sections.push(`${data.firstName || ''} ${data.lastName || ''}`.trim());
    }
    
    if (data.email) sections.push(`Email: ${data.email}`);
    if (data.phone) sections.push(`Phone: ${data.phone}`);
    if (data.location) sections.push(`Location: ${data.location}`);
    
    sections.push(''); // Empty line
    
    // Professional Summary
    if (data.experienceSummary) {
        sections.push('PROFESSIONAL SUMMARY');
        sections.push(data.experienceSummary);
        sections.push('');
    }
    
    // Experience
    if (data.experienceYears) {
        sections.push('EXPERIENCE');
        sections.push(`${data.experienceYears} years of professional experience`);
        
        if (data.lastThreeJobTitles && Array.isArray(data.lastThreeJobTitles)) {
            data.lastThreeJobTitles.forEach((title: string, index: number) => {
                const company = data.companies && data.companies[index] ? ` at ${data.companies[index]}` : '';
                sections.push(`• ${title}${company}`);
            });
        }
        sections.push('');
    }
    
    // Skills
    if (data.skills && Array.isArray(data.skills) && data.skills.length > 0) {
        sections.push('SKILLS');
        sections.push(data.skills.join(', '));
        sections.push('');
    }
    
    // Education
    if (data.education && Array.isArray(data.education) && data.education.length > 0) {
        sections.push('EDUCATION');
        data.education.forEach((edu: string) => {
            sections.push(`• ${edu}`);
        });
        sections.push('');
    }
    
    // Certifications
    if (data.certifications && Array.isArray(data.certifications) && data.certifications.length > 0) {
        sections.push('CERTIFICATIONS');
        data.certifications.forEach((cert: string) => {
            sections.push(`• ${cert}`);
        });
    }
    
    return sections.join('\n');
};

// Create fallback CV content from CVRecord
const createFallbackCvContent = (cvRecord: CVRecord): string => {
    const sections = [];
    
    if (cvRecord.name) sections.push(cvRecord.name);
    if (cvRecord.email) sections.push(`Email: ${cvRecord.email}`);
    if (cvRecord.phone) sections.push(`Phone: ${cvRecord.phone}`);
    if (cvRecord.location) sections.push(`Location: ${cvRecord.location}`);
    
    sections.push(''); // Empty line
    
    if (cvRecord.summary) {
        sections.push('PROFESSIONAL SUMMARY');
        sections.push(cvRecord.summary);
        sections.push('');
    }
    
    if (cvRecord.experience) {
        sections.push('EXPERIENCE');
        sections.push(cvRecord.experience);
        sections.push('');
    }
    
    if (cvRecord.skills) {
        sections.push('SKILLS');
        sections.push(cvRecord.skills);
        sections.push('');
    }
    
    if (cvRecord.education) {
        sections.push('EDUCATION');
        sections.push(cvRecord.education);
    }
    
    return sections.join('\n');
};

// Component to display formatted CV content
const FormattedCvDisplay = ({ cvRecord }: { cvRecord: CVRecord }) => {
    const formattedContent = formatCvContent(cvRecord.raw_text, cvRecord);
    
    return (
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 shadow-sm">
            <h4 className="font-semibold text-gray-800 dark:text-gray-200 mb-4 flex items-center">
                📄 CV Content
                <span className="ml-2 text-sm font-normal text-gray-500 dark:text-gray-400">
                    (Formatted for readability)
                </span>
            </h4>
            <div className="prose prose-sm max-w-none">
                <div className="whitespace-pre-wrap text-gray-700 dark:text-gray-300 font-mono text-sm leading-relaxed bg-gray-50 dark:bg-gray-900 p-4 rounded-lg border break-words overflow-hidden">
                    {formattedContent}
                </div>
            </div>
        </div>
    );
};

export default function ResumeOptimizationPage() {
    const { getToken, isLoaded, isSignedIn } = useAuth();
    const { user } = useUser();
    const router = useRouter();
    
    // State for CV and Resume Optimization
    const [cvRecord, setCvRecord] = useState<CVRecord | null>(null);
    const [loadingCV, setLoadingCV] = useState(true);
    const [jobDescriptionForResume, setJobDescriptionForResume] = useState("");
    const [resumeOptimization, setResumeOptimization] = useState("");
    const [loadingResume, setLoadingResume] = useState(false);

    useEffect(() => {
        if (isLoaded && !isSignedIn) {
            router.push("/login");
        }
    }, [isLoaded, isSignedIn, router]);

    // Fetch user's CV from database
    useEffect(() => {
        const fetchUserCV = async () => {
            if (!user?.id) return;
            
            try {
                const token = await getToken();
                const response = await fetch(`/api/user-profile/${user.id}`, {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                });

                if (response.ok) {
                    const data = await response.json();
                    
                    if (data.user_exists && data.user_profile && data.cv_record_id) {
                        // Reconstruct CV record from the user profile data
                        const cvRecord: CVRecord = {
                            id: data.cv_record_id,
                            user_id: user.id,
                            filename: data.cv_filename || "CV",
                            raw_text: data.cv_raw_text || "",
                            name: `${data.user_profile.firstName || ''} ${data.user_profile.lastName || ''}`.trim(),
                            email: data.user_profile.email,
                            phone: data.user_profile.phone,
                            location: "", // Not available in current structure
                            experience: data.user_profile.experienceYears?.toString() || "",
                            skills: Array.isArray(data.user_profile.skills) ? data.user_profile.skills.join(", ") : "",
                            education: Array.isArray(data.user_profile.education) ? data.user_profile.education.join(", ") : "",
                            summary: data.user_profile.experienceSummary || "",
                            created_at: "",
                            updated_at: data.last_updated || ""
                        };
                        
                        // If we don't have raw_text, create a fallback
                        if (!cvRecord.raw_text) {
                            cvRecord.raw_text = `${cvRecord.name}\n${cvRecord.email}\n${cvRecord.phone}\n\nExperience: ${cvRecord.experience} years\n\nSkills: ${cvRecord.skills}\n\nEducation: ${cvRecord.education}\n\nSummary: ${cvRecord.summary}`;
                        }
                        
                        setCvRecord(cvRecord);
                    }
                }
            } catch (error) {
                console.error("Error fetching CV:", error);
            } finally {
                setLoadingCV(false);
            }
        };

        if (isLoaded && isSignedIn && user?.id) {
            fetchUserCV();
        }
    }, [isLoaded, isSignedIn, user?.id, getToken]);

    const handleResumeSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        
        if (!cvRecord) {
            alert("No CV found. Please upload your CV first from the dashboard.");
            return;
        }

        if (!jobDescriptionForResume.trim()) {
            alert("Please paste the target job description.");
            return;
        }

        setLoadingResume(true);
        setResumeOptimization("");

        try {
            const token = await getToken();
            
            // Use formatted CV content for better consistency
            const formattedCvContent = formatCvContent(cvRecord.raw_text, cvRecord);
            
            const requestBody = {
                user_id: user?.id,
                cv_record_id: cvRecord.id,
                resume_text: formattedCvContent, // Use formatted content instead of raw_text
                job_description: jobDescriptionForResume,
            };
            
            const response = await fetch("/api/optimize-resume", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`,
                },
                body: JSON.stringify(requestBody),
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
                throw new Error(errorData.error || "Failed to optimize resume");
            }

            const data = await response.json();
            
            if (data.optimization) {
                setResumeOptimization(data.optimization);
            } else {
                alert("No optimization data received. Please try again.");
            }
        } catch (error) {
            console.error("Resume optimization error:", error);
            alert(`Failed to optimize resume: ${error instanceof Error ? error.message : 'Unknown error'}`);
        } finally {
            setLoadingResume(false);
        }
    };

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
                        <Link href="/dashboard" className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300">
                            ← Back to Dashboard
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
                            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Resume Optimization</h1>
                        </div>
                    </div>
                    <div className="flex items-center space-x-4">
                        <span className="text-gray-600 dark:text-gray-300">Welcome, {user?.firstName || "User"}!</span>
                        <ThemeToggle />
                        <SignOutButton>
                            <Button variant="outline" size="sm" className="p-3 rounded-full w-11 h-11 flex items-center justify-center" title="Sign Out">
                                <svg
                                    className="w-5 h-5"
                                    fill="none"
                                    stroke="currentColor"
                                    viewBox="0 0 24 24"
                                    xmlns="http://www.w3.org/2000/svg"
                                >
                                    <path
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        strokeWidth={2}
                                        d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
                                    />
                                </svg>
                            </Button>
                        </SignOutButton>
                    </div>
                </div>
            </header>

            <div className="container mx-auto p-4 sm:p-6 max-w-7xl">
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4 sm:p-8 overflow-hidden">
                    <div className="mb-6">
                        <h2 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white mb-2">📄 Resume Optimization</h2>
                        <p className="text-gray-600 dark:text-gray-300 text-sm sm:text-base">
                            Get AI-powered suggestions to optimize your resume for specific job opportunities. 
                            Upload your resume and paste the target job description to receive personalized recommendations.
                        </p>
                    </div>

                    {loadingCV ? (
                        <div className="flex items-center justify-center py-12">
                            <div className="text-lg text-gray-600 dark:text-gray-300">Loading your CV...</div>
                        </div>
                    ) : !cvRecord ? (
                        <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-6 mb-6">
                            <div className="flex items-center">
                                <div className="flex-shrink-0">
                                    <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                                        <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                                    </svg>
                                </div>
                                <div className="ml-3">
                                    <h3 className="text-sm font-medium text-yellow-800 dark:text-yellow-200">
                                        No CV Found
                                    </h3>
                                    <div className="mt-2 text-sm text-yellow-700 dark:text-yellow-300">
                                        <p>
                                            Please upload your CV first from the dashboard to use the resume optimization feature.
                                        </p>
                                    </div>
                                    <div className="mt-4">
                                        <Link href="/dashboard">
                                            <Button variant="outline" size="sm">
                                                Go to Dashboard
                                            </Button>
                                        </Link>
                                    </div>
                                </div>
                            </div>
                        </div>
                    ) : (
                        <>
                            {/* Display Current CV */}
                            <div className="mb-8">
                                <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-6">
                                    <h3 className="text-xl font-semibold text-blue-900 dark:text-blue-100 mb-4 flex items-center">
                                        📄 Your Current CV
                                        <span className="ml-2 text-sm font-normal text-blue-600 dark:text-blue-300">
                                            ({cvRecord.filename})
                                        </span>
                                    </h3>
                                    
                                    {/* CV Summary Info */}
                                    {(cvRecord.name || cvRecord.email || cvRecord.phone) && (
                                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4 p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
                                            {cvRecord.name && (
                                                <div>
                                                    <span className="font-medium text-gray-700 dark:text-gray-300">Name:</span>
                                                    <p className="text-gray-600 dark:text-gray-400">{cvRecord.name}</p>
                                                </div>
                                            )}
                                            {cvRecord.email && (
                                                <div>
                                                    <span className="font-medium text-gray-700 dark:text-gray-300">Email:</span>
                                                    <p className="text-gray-600 dark:text-gray-400">{cvRecord.email}</p>
                                                </div>
                                            )}
                                            {cvRecord.phone && (
                                                <div>
                                                    <span className="font-medium text-gray-700 dark:text-gray-300">Phone:</span>
                                                    <p className="text-gray-600 dark:text-gray-400">{cvRecord.phone}</p>
                                                </div>
                                            )}
                                        </div>
                                    )}

                                    {/* CV Full Text - Using FormattedCvDisplay */}
                                    <div className="mt-4">
                                        <FormattedCvDisplay cvRecord={cvRecord} />
                                    </div>
                                    
                                    <p className="text-sm text-blue-600 dark:text-blue-300 mt-2">
                                        Last updated: {new Date(cvRecord.updated_at).toLocaleDateString()}
                                    </p>
                                </div>
                            </div>

                            {/* Job Description Input and Optimization */}
                            <form onSubmit={handleResumeSubmit} className="space-y-6">
                                <div>
                                    <Label htmlFor="job-description-for-resume">Target Job Description</Label>
                                    <Textarea
                                        id="job-description-for-resume"
                                        value={jobDescriptionForResume}
                                        onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setJobDescriptionForResume(e.target.value)}
                                        placeholder="Paste the complete job description here including requirements, responsibilities, qualifications, and company information..."
                                        required
                                        rows={12}
                                        className="mt-2"
                                    />
                                    <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                                        Include the full job posting to tailor your resume specifically for this role
                                    </p>
                                </div>
                                
                                <Button type="submit" disabled={loadingResume} className="w-full">
                                    {loadingResume ? "🤖 Analyzing CV and Job Description..." : "🚀 Optimize My Resume"}
                                </Button>
                            </form>
                        </>
                    )}

                    {resumeOptimization && (
                        <div className="mt-8 p-4 sm:p-8 border rounded-lg bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 border-purple-200 dark:border-purple-800 shadow-lg overflow-hidden">
                            <h3 className="text-xl sm:text-2xl font-semibold mb-6 text-purple-900 dark:text-purple-100 flex items-center break-words">
                                ✨ AI-Powered Resume Optimization Recommendations
                            </h3>
                            <div className="prose prose-sm sm:prose-lg max-w-none text-gray-800 dark:text-gray-200 overflow-hidden word-wrap break-words">
                                <ReactMarkdown
                                    components={{
                                        h1: ({node, ...props}) => (
                                            <h1 className="text-3xl font-bold text-purple-900 dark:text-purple-100 mb-6 mt-8 pb-2 border-b-2 border-purple-200 dark:border-purple-800 break-words" {...props} />
                                        ),
                                        h2: ({node, ...props}) => (
                                            <h2 className="text-2xl font-semibold text-purple-800 dark:text-purple-200 mb-4 mt-6 pb-1 border-b border-purple-100 dark:border-purple-800 break-words" {...props} />
                                        ),
                                        h3: ({node, ...props}) => (
                                            <h3 className="text-xl font-medium text-purple-700 dark:text-purple-300 mb-3 mt-5 break-words" {...props} />
                                        ),
                                        h4: ({node, ...props}) => (
                                            <h4 className="text-lg font-medium text-purple-600 dark:text-purple-400 mb-2 mt-4 break-words" {...props} />
                                        ),
                                        p: ({node, ...props}) => (
                                            <p className="mb-4 text-gray-700 dark:text-gray-300 leading-relaxed text-base break-words" {...props} />
                                        ),
                                        ul: ({node, ...props}) => (
                                            <ul className="list-disc list-outside mb-4 pl-6 space-y-2 break-words" {...props} />
                                        ),
                                        ol: ({node, ...props}) => (
                                            <ol className="list-decimal list-outside mb-4 pl-6 space-y-2 break-words" {...props} />
                                        ),
                                        li: ({node, ...props}) => (
                                            <li className="text-gray-700 dark:text-gray-300 leading-relaxed text-base break-words" {...props} />
                                        ),
                                        strong: ({node, ...props}) => (
                                            <strong className="font-semibold text-gray-900 dark:text-gray-100 break-words" {...props} />
                                        ),
                                        em: ({node, ...props}) => (
                                            <em className="italic text-gray-600 dark:text-gray-400 break-words" {...props} />
                                        ),
                                        code: ({node, ...props}) => (
                                            <code className="bg-purple-100 dark:bg-purple-900/30 px-2 py-1 rounded text-sm text-purple-800 dark:text-purple-200 font-mono break-words" {...props} />
                                        ),
                                        pre: ({node, ...props}) => (
                                            <pre className="bg-gray-100 dark:bg-gray-800 p-4 rounded-lg mb-4 text-sm whitespace-pre-wrap break-words overflow-hidden" {...props} />
                                        ),
                                        blockquote: ({node, ...props}) => (
                                            <blockquote className="border-l-4 border-purple-300 dark:border-purple-600 pl-4 italic text-gray-600 dark:text-gray-400 my-4" {...props} />
                                        ),
                                    }}
                                >
                                    {resumeOptimization}
                                </ReactMarkdown>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
} 