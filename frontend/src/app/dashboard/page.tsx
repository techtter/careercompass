"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@clerk/nextjs";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Label } from "@/components/ui/Label";
import { Textarea } from "@/components/ui/Textarea";

export default function DashboardPage() {
    const { getToken, isLoaded, isSignedIn } = useAuth();
    const router = useRouter();
    
    // State for Career Path
    const [jobTitle, setJobTitle] = useState("");
    const [experience, setExperience] = useState("");
    const [skills, setSkills] = useState("");
    const [careerPath, setCareerPath] = useState("");
    const [loadingCareerPath, setLoadingCareerPath] = useState(false);

    // State for Skill Gap Analysis
    const [jobDescription, setJobDescription] = useState("");
    const [skillGapAnalysis, setSkillGapAnalysis] = useState("");
    const [loadingSkillGap, setLoadingSkillGap] = useState(false);

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
                    job_title: jobTitle,
                    experience,
                    skills: skills.split(",").map(skill => skill.trim()),
                }),
            });

            if (!response.ok) {
                throw new Error("Failed to generate career path");
            }

            const data = await response.json();
            setCareerPath(data.career_path);
        } catch (error) {
            console.error(error);
        } finally {
            setLoadingCareerPath(false);
        }
    };

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
                    skills: skills.split(",").map(skill => skill.trim()),
                    job_description: jobDescription,
                }),
            });

            if (!response.ok) {
                throw new Error("Failed to generate skill gap analysis");
            }

            const data = await response.json();
            setSkillGapAnalysis(data.analysis);
        } catch (error) {
            console.error(error);
        } finally {
            setLoadingSkillGap(false);
        }
    };

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
        } finally {
            setLoadingResume(false);
        }
    };

    if (!isLoaded || !isSignedIn) {
        return null; // or a loading spinner
    }

    return (
        <div className="container mx-auto p-4 space-y-8">
            <div className="grid md:grid-cols-2 gap-8">
                <div>
                    <h1 className="text-2xl font-bold mb-4">Career Path Generator</h1>
                    <form onSubmit={handleCareerPathSubmit} className="space-y-4">
                        <div>
                            <Label htmlFor="job-title">Current or Desired Job Title</Label>
                            <Input
                                id="job-title"
                                value={jobTitle}
                                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setJobTitle(e.target.value)}
                                placeholder="e.g., Software Engineer"
                                required
                            />
                        </div>
                        <div>
                            <Label htmlFor="experience">Your Experience</Label>
                            <Textarea
                                id="experience"
                                value={experience}
                                onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setExperience(e.target.value)}
                                placeholder="e.g., 5 years in backend development"
                                required
                            />
                        </div>
                        <div>
                            <Label htmlFor="skills">Your Skills (comma-separated)</Label>
                            <Input
                                id="skills"
                                value={skills}
                                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSkills(e.target.value)}
                                placeholder="e.g., Python, React, SQL"
                                required
                            />
                        </div>
                        <Button type="submit" disabled={loadingCareerPath}>
                            {loadingCareerPath ? "Generating..." : "Generate Career Path"}
                        </Button>
                    </form>

                    {careerPath && (
                        <div className="mt-8 p-4 border rounded-md bg-gray-50">
                            <h2 className="text-xl font-semibold mb-2">Your Personalized Career Path</h2>
                            <pre className="whitespace-pre-wrap font-sans">{careerPath}</pre>
                        </div>
                    )}
                </div>

                <div>
                    <h1 className="text-2xl font-bold mb-4">Skill Gap Analysis</h1>
                    <form onSubmit={handleSkillGapSubmit} className="space-y-4">
                        <div>
                            <Label htmlFor="skills-for-gap-analysis">
                                Your Skills (comma-separated, used from Career Path)
                            </Label>
                            <Input
                                id="skills-for-gap-analysis"
                                value={skills}
                                readOnly
                                className="bg-gray-100"
                            />
                        </div>
                        <div>
                            <Label htmlFor="job-description">Job Description</Label>
                            <Textarea
                                id="job-description"
                                value={jobDescription}
                                onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setJobDescription(e.target.value)}
                                placeholder="Paste the job description here"
                                required
                                rows={10}
                            />
                        </div>
                        <Button type="submit" disabled={loadingSkillGap}>
                            {loadingSkillGap ? "Analyzing..." : "Analyze Skill Gap"}
                        </Button>
                    </form>

                    {skillGapAnalysis && (
                        <div className="mt-8 p-4 border rounded-md bg-gray-50">
                            <h2 className="text-xl font-semibold mb-2">Skill Gap Analysis</h2>
                            <pre className="whitespace-pre-wrap font-sans">{skillGapAnalysis}</pre>
                        </div>
                    )}
                </div>
            </div>

            <div>
                <h1 className="text-2xl font-bold mb-4">Resume Optimization</h1>
                <form onSubmit={handleResumeSubmit} className="space-y-4">
                    <div>
                        <Label htmlFor="resume-text">Your Resume</Label>
                        <Textarea
                            id="resume-text"
                            value={resumeText}
                            onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setResumeText(e.target.value)}
                            placeholder="Paste your resume text here"
                            required
                            rows={15}
                        />
                    </div>
                    <div>
                        <Label htmlFor="job-description-for-resume">Target Job Description</Label>
                        <Textarea
                            id="job-description-for-resume"
                            value={jobDescriptionForResume}
                            onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setJobDescriptionForResume(e.target.value)}
                            placeholder="Paste the target job description here"
                            required
                            rows={15}
                        />
                    </div>
                    <Button type="submit" disabled={loadingResume}>
                        {loadingResume ? "Optimizing..." : "Optimize Resume"}
                    </Button>
                </form>

                {resumeOptimization && (
                    <div className="mt-8 p-4 border rounded-md bg-gray-50">
                        <h2 className="text-xl font-semibold mb-2">Resume Optimization Suggestions</h2>
                        <pre className="whitespace-pre-wrap font-sans">{resumeOptimization}</pre>
                    </div>
                )}
            </div>
        </div>
    );
} 