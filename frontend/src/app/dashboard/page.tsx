"use client";

import { useState, useEffect } from "react";
import { useAuth, useUser, SignOutButton } from "@clerk/nextjs";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Label } from "@/components/ui/Label";
import Link from "next/link";

interface UserProfile {
  name: string;
  experience: string;
  skills: string[];
  lastTwoJobs: string[];
  email?: string | null;
  phone?: string | null;
  location?: string | null;
  education?: string | null;
  summary?: string | null;
}

export default function DashboardPage() {
    const { getToken, isLoaded, isSignedIn } = useAuth();
    const { user } = useUser();
    const router = useRouter();
    
    // State for uploaded resume and parsed profile
    const [uploadedFile, setUploadedFile] = useState<File | null>(null);
    const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
    const [uploadingResume, setUploadingResume] = useState(false);
    const [isSaving, setIsSaving] = useState(false);
    const [savedCvId, setSavedCvId] = useState<number | null>(null);
    const [rawText, setRawText] = useState<string>("");

    useEffect(() => {
        if (isLoaded && !isSignedIn) {
            router.push("/login");
        }
    }, [isLoaded, isSignedIn, router]);

    // Handle resume file upload
    const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (file) {
            setUploadedFile(file);
        }
    };

    // Parse uploaded resume
    const handleResumeUpload = async () => {
        if (!uploadedFile) return;

        setUploadingResume(true);
        const formData = new FormData();
        formData.append('file', uploadedFile);

        try {
            const token = await getToken();
            const response = await fetch('/api/parse-resume', {
                method: 'POST',
                headers: {
                    Authorization: `Bearer ${token}`,
                },
                body: formData,
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to parse resume');
            }

            const result = await response.json();
            setUserProfile(result.parsed_data);
            setRawText(result.file_info.raw_text);
            
            alert(`✅ Resume parsed successfully! Extracted details for: ${result.parsed_data.name || 'User'}`);
            
        } catch (error) {
            console.error('Error parsing resume:', error);
            alert(error instanceof Error ? error.message : 'Error parsing resume. Please try again.');
        } finally {
            setUploadingResume(false);
        }
    };

    // Save CV to database
    const handleSaveCV = async () => {
        if (!userProfile || !uploadedFile || !rawText) return;

        setIsSaving(true);
        try {
            const token = await getToken();
            const response = await fetch('/api/save-cv', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${token}`,
                },
                body: JSON.stringify({
                    user_id: user?.id,
                    filename: uploadedFile.name,
                    file_type: uploadedFile.type,
                    raw_text: rawText,
                    parsed_data: userProfile,
                }),
            });

            if (!response.ok) {
                throw new Error('Failed to save CV');
            }

            const result = await response.json();
            setSavedCvId(result.cv_record_id);
            alert('✅ CV saved successfully to your profile!');
            
        } catch (error) {
            console.error('Error saving CV:', error);
            alert('Error saving CV. Please try again.');
        } finally {
            setIsSaving(false);
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
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <header className="bg-white shadow-sm border-b">
                <div className="container mx-auto px-4 py-4 flex justify-between items-center">
                    <h1 className="text-2xl font-bold text-gray-900">Career Compass AI</h1>
                    <div className="flex items-center space-x-4">
                        <span className="text-gray-600">Welcome, {user?.firstName || "User"}!</span>
                        <SignOutButton>
                            <Button variant="outline" size="sm">
                                Sign Out
                            </Button>
                        </SignOutButton>
                    </div>
                </div>
            </header>

            <div className="container mx-auto p-4 space-y-8">
                
                {/* Resume Upload Section */}
                <div className="bg-white rounded-lg shadow-md p-6">
                    <h2 className="text-xl font-bold mb-4">📄 Upload Your Resume</h2>
                    <div className="flex flex-col space-y-4">
                        <div>
                            <Label htmlFor="resume-upload">Choose Resume File (PDF, DOC, DOCX, TXT)</Label>
                            <Input
                                id="resume-upload"
                                type="file"
                                accept=".pdf,.doc,.docx,.txt"
                                onChange={handleFileUpload}
                                className="mt-2"
                            />
                            <p className="text-sm text-gray-500 mt-1">
                                Supports PDF, DOC, DOCX, and TXT files. We'll extract your name, skills, experience, and job titles automatically.
                            </p>
                        </div>
                        {uploadedFile && (
                            <div className="flex items-center space-x-4">
                                <span className="text-sm text-gray-600">
                                    Selected: {uploadedFile.name}
                                </span>
                                <Button 
                                    onClick={handleResumeUpload}
                                    disabled={uploadingResume}
                                    size="sm"
                                >
                                    {uploadingResume ? "Parsing..." : "Parse Resume"}
                                </Button>
                            </div>
                        )}
                    </div>
                </div>

                {/* User Profile Section - Shows after resume parsing */}
                {userProfile && (
                    <div className="bg-white rounded-lg shadow-md p-6">
                        <div className="flex justify-between items-center mb-4">
                            <h2 className="text-xl font-bold">👤 Your Profile Summary</h2>
                            {!savedCvId && (
                                <Button 
                                    onClick={handleSaveCV}
                                    disabled={isSaving}
                                    className="bg-green-600 hover:bg-green-700"
                                >
                                    {isSaving ? "Saving..." : "💾 Save to Profile"}
                                </Button>
                            )}
                            {savedCvId && (
                                <span className="text-green-600 font-semibold">✅ Saved to Profile</span>
                            )}
                        </div>
                        <div className="grid md:grid-cols-2 gap-6">
                            <div>
                                <div className="mb-4">
                                    <h3 className="font-semibold text-gray-700 mb-2">Name:</h3>
                                    <p className="text-gray-900 text-lg">{userProfile.name}</p>
                                </div>
                                <div className="mb-4">
                                    <h3 className="font-semibold text-gray-700 mb-2">Experience:</h3>
                                    <p className="text-gray-900">{userProfile.experience}</p>
                                </div>
                                {userProfile.email && (
                                    <div className="mb-4">
                                        <h3 className="font-semibold text-gray-700 mb-2">Email:</h3>
                                        <p className="text-gray-900">{userProfile.email}</p>
                                    </div>
                                )}
                                {userProfile.phone && (
                                    <div className="mb-4">
                                        <h3 className="font-semibold text-gray-700 mb-2">Phone:</h3>
                                        <p className="text-gray-900">{userProfile.phone}</p>
                                    </div>
                                )}
                            </div>
                            <div>
                                <div className="mb-4">
                                    <h3 className="font-semibold text-gray-700 mb-2">Recent Job Titles:</h3>
                                    <ul className="list-disc list-inside text-gray-900">
                                        {userProfile.lastTwoJobs.map((job, index) => (
                                            <li key={index}>{job}</li>
                                        ))}
                                    </ul>
                                </div>
                                {userProfile.location && (
                                    <div className="mb-4">
                                        <h3 className="font-semibold text-gray-700 mb-2">Location:</h3>
                                        <p className="text-gray-900">{userProfile.location}</p>
                                    </div>
                                )}
                                {userProfile.education && (
                                    <div className="mb-4">
                                        <h3 className="font-semibold text-gray-700 mb-2">Education:</h3>
                                        <p className="text-gray-900">{userProfile.education}</p>
                                    </div>
                                )}
                            </div>
                            <div>
                                <div className="mb-4">
                                    <h3 className="font-semibold text-gray-700 mb-2">Key Skills:</h3>
                                    <div className="flex flex-wrap gap-2">
                                        {userProfile.skills.map((skill, index) => (
                                            <span 
                                                key={index}
                                                className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-sm"
                                            >
                                                {skill}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                                {userProfile.summary && (
                                    <div>
                                        <h3 className="font-semibold text-gray-700 mb-2">Professional Summary:</h3>
                                        <p className="text-gray-900 text-sm">{userProfile.summary}</p>
                                    </div>
                                )}
                            </div>
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