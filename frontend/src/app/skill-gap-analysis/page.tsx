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

export default function SkillGapAnalysisPage() {
    const { getToken, isLoaded, isSignedIn } = useAuth();
    const { user } = useUser();
    const router = useRouter();
    
    // State for Skill Gap Analysis
    const [skills, setSkills] = useState("");
    const [jobDescription, setJobDescription] = useState("");
    const [targetRole, setTargetRole] = useState("");
    const [skillGapAnalysis, setSkillGapAnalysis] = useState("");
    const [loadingSkillGap, setLoadingSkillGap] = useState(false);

    useEffect(() => {
        if (isLoaded && !isSignedIn) {
            router.push("/login");
        }
    }, [isLoaded, isSignedIn, router]);

    const handleSkillGapSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoadingSkillGap(true);
        setSkillGapAnalysis("");

        try {
            const token = await getToken();
            const response = await fetch("/api/skill-gap-analysis", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`,
                },
                body: JSON.stringify({
                    user_id: user?.id,
                    skills: skills.split(",").map((skill) => skill.trim()),
                    job_description: jobDescription,
                    target_role: targetRole || null,
                }),
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
                throw new Error(errorData.error || "Failed to analyze skill gap");
            }

            const data = await response.json();
            setSkillGapAnalysis(data.analysis);
        } catch (error) {
            console.error('Skill gap analysis error:', error);
            alert(`Failed to analyze skill gap: ${error instanceof Error ? error.message : 'Please try again.'}`);
        } finally {
            setLoadingSkillGap(false);
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
                            <h1 className="text-2xl font-bold text-gray-900">Skill Gap Analysis</h1>
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
                        <h2 className="text-3xl font-bold text-gray-900 mb-2">📊 Skill Gap Analysis</h2>
                        <p className="text-gray-600">
                            Compare your current skills with job requirements to identify gaps and learning opportunities. 
                            Get personalized recommendations for skill development.
                        </p>
                    </div>

                    <form onSubmit={handleSkillGapSubmit} className="space-y-6">
                        <div>
                            <Label htmlFor="skills">Your Current Skills (comma-separated)</Label>
                            <Input
                                id="skills"
                                value={skills}
                                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSkills(e.target.value)}
                                placeholder="e.g., Python, React, SQL, Machine Learning, Project Management"
                                required
                                className="mt-2"
                            />
                            <p className="text-sm text-gray-500 mt-1">
                                List all your technical and soft skills separated by commas
                            </p>
                        </div>
                        
                        <div>
                            <Label htmlFor="target-role">Target Role (Optional)</Label>
                            <Input
                                id="target-role"
                                value={targetRole}
                                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setTargetRole(e.target.value)}
                                placeholder="e.g., Senior Software Engineer, Data Scientist, Product Manager"
                                className="mt-2"
                            />
                            <p className="text-sm text-gray-500 mt-1">
                                Specify your target role for more focused analysis
                            </p>
                        </div>
                        
                        <div>
                            <Label htmlFor="job-description">Target Job Description</Label>
                            <Textarea
                                id="job-description"
                                value={jobDescription}
                                onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setJobDescription(e.target.value)}
                                placeholder="Paste the complete job description here including requirements, responsibilities, and qualifications..."
                                required
                                rows={12}
                                className="mt-2"
                            />
                            <p className="text-sm text-gray-500 mt-1">
                                Include the full job posting for accurate analysis
                            </p>
                        </div>
                        
                        <Button type="submit" disabled={loadingSkillGap} className="w-full">
                            {loadingSkillGap ? "Analyzing Skill Gaps..." : "Analyze Skill Gap"}
                        </Button>
                    </form>

                    {skillGapAnalysis && (
                        <div className="mt-8 p-8 border rounded-lg bg-gradient-to-r from-green-50 to-emerald-50 border-green-200 shadow-lg">
                            <h3 className="text-2xl font-semibold mb-6 text-green-900 flex items-center">
                                🎯 Your Skill Gap Analysis
                            </h3>
                            <div className="prose prose-lg max-w-none text-gray-800">
                                <ReactMarkdown
                                    components={{
                                        h1: ({node, ...props}) => (
                                            <h1 className="text-3xl font-bold text-green-900 mb-6 mt-8 pb-2 border-b-2 border-green-200" {...props} />
                                        ),
                                        h2: ({node, ...props}) => (
                                            <h2 className="text-2xl font-semibold text-green-800 mb-4 mt-6 pb-1 border-b border-green-100" {...props} />
                                        ),
                                        h3: ({node, ...props}) => (
                                            <h3 className="text-xl font-medium text-green-700 mb-3 mt-5" {...props} />
                                        ),
                                        h4: ({node, ...props}) => (
                                            <h4 className="text-lg font-medium text-green-600 mb-2 mt-4" {...props} />
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
                                            <li className="text-gray-700 leading-relaxed text-base" {...props} />
                                        ),
                                        strong: ({node, ...props}) => (
                                            <strong className="font-semibold text-gray-900" {...props} />
                                        ),
                                        em: ({node, ...props}) => (
                                            <em className="italic text-gray-600" {...props} />
                                        ),
                                        code: ({node, ...props}) => (
                                            <code className="bg-green-100 px-2 py-1 rounded text-sm text-green-800 font-mono" {...props} />
                                        ),
                                        pre: ({node, ...props}) => (
                                            <pre className="bg-gray-100 p-4 rounded-lg overflow-x-auto mb-4 text-sm" {...props} />
                                        ),
                                        blockquote: ({node, ...props}) => (
                                            <blockquote className="border-l-4 border-green-400 pl-6 py-2 italic text-gray-600 my-6 bg-green-25" {...props} />
                                        ),
                                        table: ({node, ...props}) => (
                                            <div className="overflow-x-auto mb-4">
                                                <table className="min-w-full border-collapse border border-gray-300" {...props} />
                                            </div>
                                        ),
                                        th: ({node, ...props}) => (
                                            <th className="border border-gray-300 px-4 py-2 bg-green-100 font-semibold text-left" {...props} />
                                        ),
                                        td: ({node, ...props}) => (
                                            <td className="border border-gray-300 px-4 py-2" {...props} />
                                        ),
                                        hr: ({node, ...props}) => (
                                            <hr className="my-6 border-t-2 border-green-200" {...props} />
                                        ),
                                    }}
                                >
                                    {skillGapAnalysis}
                                </ReactMarkdown>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
} 