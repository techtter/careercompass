"use client";

import { useState, useEffect } from "react";
import { useAuth, useUser, SignOutButton } from "@clerk/nextjs";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/Button";
import { Label } from "@/components/ui/Label";
import { Textarea } from "@/components/ui/Textarea";
import Link from "next/link";

export default function ResumeOptimizationPage() {
    const { getToken, isLoaded, isSignedIn } = useAuth();
    const { user } = useUser();
    const router = useRouter();
    
    // State for Resume Optimization
    const [resumeText, setResumeText] = useState("");
    const [jobDescriptionForResume, setJobDescriptionForResume] = useState("");
    const [resumeOptimization, setResumeOptimization] = useState("");
    const [loadingResume, setLoadingResume] = useState(false);

    useEffect(() => {
        if (isLoaded && !isSignedIn) {
            router.push("/login");
        }
    }, [isLoaded, isSignedIn, router]);

    const handleResumeSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoadingResume(true);
        setResumeOptimization("");

        try {
            const token = await getToken();
            const response = await fetch("/api/optimize-resume", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`,
                },
                body: JSON.stringify({
                    resume_text: resumeText,
                    job_description: jobDescriptionForResume,
                }),
            });

            if (!response.ok) {
                throw new Error("Failed to optimize resume");
            }

            const data = await response.json();
            setResumeOptimization(data.optimization);
        } catch (error) {
            console.error(error);
            alert("Failed to optimize resume. Please try again.");
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
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <header className="bg-white shadow-sm border-b">
                <div className="container mx-auto px-4 py-4 flex justify-between items-center">
                    <div className="flex items-center space-x-4">
                        <Link href="/dashboard" className="text-blue-600 hover:text-blue-800">
                            ← Back to Dashboard
                        </Link>
                        <h1 className="text-2xl font-bold text-gray-900">Resume Optimization</h1>
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
                        <h2 className="text-3xl font-bold text-gray-900 mb-2">📝 Resume Optimization</h2>
                        <p className="text-gray-600">
                            Optimize your resume for specific job applications. Get AI-powered suggestions to improve 
                            your resume content, formatting, and keyword optimization for better ATS compatibility.
                        </p>
                    </div>

                    <form onSubmit={handleResumeSubmit} className="space-y-6">
                        <div>
                            <Label htmlFor="resume-text">Your Current Resume</Label>
                            <Textarea
                                id="resume-text"
                                value={resumeText}
                                onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setResumeText(e.target.value)}
                                placeholder="Paste your complete resume text here including contact information, experience, education, skills, etc..."
                                required
                                rows={15}
                                className="mt-2"
                            />
                            <p className="text-sm text-gray-500 mt-1">
                                Copy and paste your entire resume content for comprehensive analysis
                            </p>
                        </div>
                        
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
                            <p className="text-sm text-gray-500 mt-1">
                                Include the full job posting to tailor your resume specifically for this role
                            </p>
                        </div>
                        
                        <Button type="submit" disabled={loadingResume} className="w-full">
                            {loadingResume ? "Optimizing Your Resume..." : "Optimize Resume"}
                        </Button>
                    </form>

                    {resumeOptimization && (
                        <div className="mt-8 p-6 border rounded-lg bg-gradient-to-r from-purple-50 to-pink-50 border-purple-200">
                            <h3 className="text-2xl font-semibold mb-4 text-purple-900">
                                ✨ Resume Optimization Suggestions
                            </h3>
                            <div className="prose max-w-none">
                                <pre className="whitespace-pre-wrap font-sans text-gray-800 leading-relaxed">
                                    {resumeOptimization}
                                </pre>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
} 