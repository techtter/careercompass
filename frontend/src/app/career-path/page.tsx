"use client";

import { useState, useEffect } from "react";
import { useAuth, useUser, SignOutButton } from "@clerk/nextjs";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Label } from "@/components/ui/Label";
import { Textarea } from "@/components/ui/Textarea";
import Link from "next/link";
import ReactMarkdown from "react-markdown";

export default function CareerPathPage() {
    const { getToken, isLoaded, isSignedIn } = useAuth();
    const { user } = useUser();
    const router = useRouter();
    
    // State for Career Path
    const [jobTitle, setJobTitle] = useState("");
    const [experience, setExperience] = useState("");
    const [skills, setSkills] = useState("");
    const [careerPath, setCareerPath] = useState("");
    const [loadingCareerPath, setLoadingCareerPath] = useState(false);
    const [cvRecord, setCvRecord] = useState<any>(null);
    const [isLoadingCV, setIsLoadingCV] = useState(false);

    useEffect(() => {
        if (isLoaded && !isSignedIn) {
            router.push("/login");
        }
    }, [isLoaded, isSignedIn, router]);

    // Load CV data when component mounts
    useEffect(() => {
        const loadCVData = async () => {
            if (!user?.id) return;
            
            setIsLoadingCV(true);
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
                        // Create CV record structure from user profile data
                        const cvData = {
                            id: data.cv_record_id,
                            filename: data.cv_filename || "CV",
                            user_profile: data.user_profile,
                            raw_text: data.cv_raw_text || "",
                            last_updated: data.last_updated
                        };
                        
                        setCvRecord(cvData);
                        
                        // Pre-fill form with CV data
                        if (data.user_profile.lastThreeJobTitles && data.user_profile.lastThreeJobTitles.length > 0) {
                            setJobTitle(data.user_profile.lastThreeJobTitles[0]);
                        }
                        
                        if (data.user_profile.experienceYears) {
                            setExperience(`${data.user_profile.experienceYears} years of experience`);
                        } else if (data.user_profile.experienceSummary) {
                            setExperience(data.user_profile.experienceSummary);
                        }
                        
                        if (data.user_profile.skills && Array.isArray(data.user_profile.skills)) {
                            setSkills(data.user_profile.skills.join(", "));
                        }
                    }
                }
            } catch (error) {
                console.error("Error loading CV data:", error);
            } finally {
                setIsLoadingCV(false);
            }
        };

        if (isLoaded && isSignedIn && user?.id) {
            loadCVData();
        }
    }, [isLoaded, isSignedIn, user?.id, getToken]);

    const handleCareerPathSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoadingCareerPath(true);
        setCareerPath("");

        try {
            const token = await getToken();
            const response = await fetch("/api/generate-career-path", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`,
                },
                body: JSON.stringify({
                    user_id: user?.id,
                    cv_record_id: cvRecord?.id || null,
                    job_title: jobTitle,
                    experience: experience,
                    skills: skills.split(",").map((skill) => skill.trim()),
                }),
            });

            if (!response.ok) {
                throw new Error("Failed to generate career path");
            }

            const data = await response.json();
            setCareerPath(data.career_path);
        } catch (error) {
            console.error(error);
            alert("Failed to generate career path. Please try again.");
        } finally {
            setLoadingCareerPath(false);
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
                    <div className="flex items-center space-x-4">
                        <Link href="/dashboard" className="text-blue-600 hover:text-blue-800">
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
                            <h1 className="text-2xl font-bold text-gray-900">Career Path Generator</h1>
                        </div>
                    </div>
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

            <div className="container mx-auto p-6">
                <div className="bg-white rounded-lg shadow-md p-8">
                    <div className="mb-6">
                        <h2 className="text-3xl font-bold text-gray-900 mb-2">🚀 Career Path Generator</h2>
                        <p className="text-gray-600">
                            Generate a personalized career roadmap based on your current skills and experience. 
                            Get insights into potential career trajectories, required skills, and next steps.
                        </p>
                        {isLoadingCV && (
                            <div className="text-blue-600 mt-2">📄 Loading your CV data...</div>
                        )}
                        {cvRecord && (
                            <div className="text-green-600 mt-2">✅ Using data from your saved CV: {cvRecord.filename}</div>
                        )}
                        {!cvRecord && !isLoadingCV && (
                            <div className="text-amber-600 mt-2">⚠️ No saved CV found. Please upload your CV in the dashboard first for better results.</div>
                        )}
                    </div>

                    <form onSubmit={handleCareerPathSubmit} className="space-y-6">
                        <div>
                            <Label htmlFor="job-title">Current or Desired Job Title</Label>
                            <Input
                                id="job-title"
                                value={jobTitle}
                                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setJobTitle(e.target.value)}
                                placeholder="e.g., Software Engineer, Data Scientist, Product Manager"
                                required
                                className="mt-2"
                            />
                        </div>
                        
                        <div>
                            <Label htmlFor="experience">Your Experience</Label>
                            <Textarea
                                id="experience"
                                value={experience}
                                onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setExperience(e.target.value)}
                                placeholder="e.g., 5 years in backend development with focus on scalable systems"
                                required
                                rows={4}
                                className="mt-2"
                            />
                        </div>
                        
                        <div>
                            <Label htmlFor="skills">Your Skills (comma-separated)</Label>
                            <Input
                                id="skills"
                                value={skills}
                                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSkills(e.target.value)}
                                placeholder="e.g., Python, React, SQL, Machine Learning, Project Management"
                                required
                                className="mt-2"
                            />
                            <p className="text-sm text-gray-500 mt-1">
                                List your technical and soft skills separated by commas
                            </p>
                        </div>
                        
                        <Button type="submit" disabled={loadingCareerPath} className="w-full">
                            {loadingCareerPath ? "Generating Your Career Path..." : "Generate Career Path"}
                        </Button>
                    </form>

                    {careerPath && (
                        <div className="mt-8 p-8 border rounded-lg bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200 shadow-lg">
                            <h3 className="text-2xl font-semibold mb-6 text-blue-900 flex items-center">
                                🎯 Your Personalized Career Path
                            </h3>
                            <div className="prose prose-lg max-w-none text-gray-800">
                                <ReactMarkdown
                                    components={{
                                        h1: ({node, ...props}) => (
                                            <h1 className="text-3xl font-bold text-blue-900 mb-6 mt-8 pb-2 border-b-2 border-blue-200" {...props} />
                                        ),
                                        h2: ({node, ...props}) => (
                                            <h2 className="text-2xl font-semibold text-blue-800 mb-4 mt-6 pb-1 border-b border-blue-100" {...props} />
                                        ),
                                        h3: ({node, ...props}) => (
                                            <h3 className="text-xl font-medium text-blue-700 mb-3 mt-5" {...props} />
                                        ),
                                        h4: ({node, ...props}) => (
                                            <h4 className="text-lg font-medium text-blue-600 mb-2 mt-4" {...props} />
                                        ),
                                        p: ({node, ...props}) => (
                                            <p className="mb-4 text-gray-700 leading-relaxed text-base" {...props} />
                                        ),
                                        ul: ({node, ...props}) => (
                                            <ul className="list-disc list-outside mb-4 pl-6 space-y-2" {...props} />
                                        ),
                                        ol: ({node, ...props}) => (
                                            <ol className="list-decimal list-outside mb-4 pl-6 space-y-2" {...props} />
                                        ),
                                        li: ({node, ...props}) => (
                                            <li className="text-gray-700 leading-relaxed" {...props} />
                                        ),
                                        strong: ({node, ...props}) => (
                                            <strong className="font-semibold text-blue-800" {...props} />
                                        ),
                                        em: ({node, ...props}) => (
                                            <em className="italic text-blue-700" {...props} />
                                        ),
                                        code: ({node, ...props}) => (
                                            <code className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm font-mono" {...props} />
                                        ),
                                        pre: ({node, ...props}) => (
                                            <pre className="bg-gray-100 p-4 rounded-lg overflow-x-auto mb-4" {...props} />
                                        ),
                                        blockquote: ({node, ...props}) => (
                                            <blockquote className="border-l-4 border-blue-300 pl-4 italic text-blue-700 mb-4" {...props} />
                                        ),
                                        table: ({node, ...props}) => (
                                            <table className="w-full border-collapse border border-gray-300 mb-4" {...props} />
                                        ),
                                        th: ({node, ...props}) => (
                                            <th className="border border-gray-300 px-4 py-2 bg-blue-100 font-semibold text-left" {...props} />
                                        ),
                                        td: ({node, ...props}) => (
                                            <td className="border border-gray-300 px-4 py-2" {...props} />
                                        ),
                                        hr: ({node, ...props}) => (
                                            <hr className="my-6 border-t-2 border-blue-200" {...props} />
                                        ),
                                    }}
                                >
                                    {careerPath}
                                </ReactMarkdown>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
} 