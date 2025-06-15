"use client";

import { useState, useEffect, useRef } from "react";
import { useAuth, useUser, SignOutButton } from "@clerk/nextjs";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Label } from "@/components/ui/Label";
import { Textarea } from "@/components/ui/Textarea";
import { ThemeToggle } from "@/components/ui/ThemeToggle";
import SkillsWordCloud from "@/components/ui/SkillsWordCloud";
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
    const [isEditingSkills, setIsEditingSkills] = useState(false);
    const careerPathResultsRef = useRef<HTMLDivElement>(null);

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
            
            // Scroll to results after a short delay to ensure content is rendered
            setTimeout(() => {
                careerPathResultsRef.current?.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }, 100);
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
                            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Career Path Generator</h1>
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

            <div className="container mx-auto p-6">
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-8">
                    <div className="mb-6">
                        <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">🚀 Career Path Generator</h2>
                        <p className="text-gray-600 dark:text-gray-300">
                            Generate a personalized career roadmap based on your current skills and experience. 
                            Get insights into potential career trajectories, required skills, and next steps.
                        </p>
                        {isLoadingCV && (
                            <div className="text-blue-600 dark:text-blue-400 mt-2">📄 Loading your CV data...</div>
                        )}
                        {cvRecord && (
                            <div className="text-green-600 dark:text-green-400 mt-2">✅ Using data from your saved CV: {cvRecord.filename}</div>
                        )}
                        {!cvRecord && !isLoadingCV && (
                            <div className="text-amber-600 dark:text-amber-400 mt-2">⚠️ No saved CV found. Please upload your CV in the dashboard first for better results.</div>
                        )}
                    </div>

                    <form onSubmit={handleCareerPathSubmit} className="space-y-6">
                        <div className="grid md:grid-cols-2 gap-6">
                            <div>
                                <Label htmlFor="job-title">Current or Desired Job Title</Label>
                                <Input
                                    id="job-title"
                                    value={jobTitle}
                                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => setJobTitle(e.target.value)}
                                    placeholder="e.g., Software Engineer, Data Scientist"
                                    required
                                    className="mt-2"
                                />
                            </div>
                            
                            <div>
                                <Label htmlFor="experience">Your Experience</Label>
                                <Input
                                    id="experience"
                                    value={experience}
                                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => setExperience(e.target.value)}
                                    placeholder="e.g., 5 years in backend development"
                                    required
                                    className="mt-2"
                                />
                            </div>
                        </div>
                        
                        <div>
                            <div className="flex items-center justify-between mb-2">
                                <Label htmlFor="skills" className="text-lg font-semibold">🛠️ Technical Skills</Label>
                                {!isEditingSkills && (
                                    <Button
                                        type="button"
                                        variant="outline"
                                        size="sm"
                                        onClick={() => setIsEditingSkills(true)}
                                        className="text-xs px-3 py-1 h-7 text-blue-600 dark:text-blue-400 border-blue-300 dark:border-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/20"
                                    >
                                        ✏️ Edit Skills
                                    </Button>
                                )}
                            </div>
                            <div className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg bg-gray-50 dark:bg-gray-800">
                                {isEditingSkills ? (
                                    <div className="space-y-3">
                                        <Textarea
                                            value={skills}
                                            onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setSkills(e.target.value)}
                                            placeholder="Enter your skills separated by commas (e.g., Python, React, SQL, Machine Learning)"
                                            rows={4}
                                            className="w-full"
                                        />
                                        <div className="flex justify-center space-x-3">
                                            <Button
                                                type="button"
                                                size="sm"
                                                onClick={() => setIsEditingSkills(false)}
                                                className="bg-green-600 hover:bg-green-700 text-white px-4 py-2"
                                            >
                                                ✅ Save Skills
                                            </Button>
                                            <Button
                                                type="button"
                                                variant="outline"
                                                size="sm"
                                                onClick={() => setIsEditingSkills(false)}
                                                className="px-4 py-2"
                                            >
                                                ❌ Cancel
                                            </Button>
                                        </div>
                                    </div>
                                ) : (
                                    <div>
                                        {skills ? (
                                            <SkillsWordCloud skills={skills.split(",").map(skill => skill.trim()).filter(skill => skill.length > 0)} />
                                        ) : (
                                            <p className="text-gray-500 dark:text-gray-400 text-center py-4">
                                                Your skills will appear here once loaded from your CV
                                            </p>
                                        )}
                                    </div>
                                )}
                            </div>
                        </div>
                        
                        <Button type="submit" disabled={loadingCareerPath} className="w-full">
                            {loadingCareerPath ? "Generating Your Career Path..." : "Generate Career Path"}
                        </Button>
                    </form>

                    {careerPath && (
                        <div ref={careerPathResultsRef} className="mt-8 p-8 border rounded-lg bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/30 border-blue-200 dark:border-blue-700 shadow-lg">
                            <h3 className="text-2xl font-semibold mb-6 text-blue-900 dark:text-blue-100 flex items-center">
                                🎯 Your Personalized Career Path
                            </h3>
                            <div className="prose prose-lg max-w-none text-gray-800 dark:text-gray-200">
                                <ReactMarkdown
                                    components={{
                                        h1: ({ node, ...props }) => (
                                            <h1 className="text-3xl font-bold text-blue-900 dark:text-blue-100 mb-6 border-b-2 border-blue-200 dark:border-blue-800 pb-3" {...props} />
                                        ),
                                        h2: ({ node, ...props }) => (
                                            <h2 className="text-2xl font-semibold text-blue-800 dark:text-blue-200 mb-4 mt-8" {...props} />
                                        ),
                                        h3: ({ node, ...props }) => (
                                            <h3 className="text-xl font-semibold text-blue-700 dark:text-blue-300 mb-3 mt-6" {...props} />
                                        ),
                                        p: ({ node, ...props }) => (
                                            <p className="mb-4 text-gray-700 dark:text-gray-300 leading-relaxed text-base" {...props} />
                                        ),
                                        ul: ({ node, ...props }) => (
                                            <ul className="list-disc list-inside mb-4 space-y-2" {...props} />
                                        ),
                                        ol: ({ node, ...props }) => (
                                            <ol className="list-decimal list-inside mb-4 space-y-2" {...props} />
                                        ),
                                        li: ({ node, ...props }) => (
                                            <li className="text-gray-700 dark:text-gray-300 leading-relaxed" {...props} />
                                        ),
                                        strong: ({ node, ...props }) => (
                                            <strong className="font-semibold text-gray-900 dark:text-gray-100" {...props} />
                                        ),
                                        em: ({ node, ...props }) => (
                                            <em className="italic text-gray-600 dark:text-gray-400" {...props} />
                                        ),
                                        code: ({ node, ...props }) => (
                                            <code className="bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-200 px-2 py-1 rounded text-sm font-mono" {...props} />
                                        ),
                                        blockquote: ({ node, ...props }) => (
                                            <blockquote className="border-l-4 border-green-400 dark:border-green-600 pl-6 py-2 italic text-gray-600 dark:text-gray-400 my-6 bg-green-50 dark:bg-green-900/20" {...props} />
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