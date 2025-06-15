"use client";

import { useState, useEffect } from "react";
import { useAuth, useUser, SignOutButton } from "@clerk/nextjs";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Label } from "@/components/ui/Label";
import { Textarea } from "@/components/ui/Textarea";
import { ThemeToggle } from "@/components/ui/ThemeToggle";
import Link from "next/link";
import ReactMarkdown from "react-markdown";

// Course URL mappings for different platforms
const COURSE_PLATFORMS = {
    coursera: {
        baseUrl: "https://www.coursera.org/search?query=",
        name: "Coursera"
    },
    udemy: {
        baseUrl: "https://www.udemy.com/courses/search/?q=",
        name: "Udemy"
    },
    pluralsight: {
        baseUrl: "https://www.pluralsight.com/search?q=",
        name: "Pluralsight"
    },
    linkedin: {
        baseUrl: "https://www.linkedin.com/learning/search?keywords=",
        name: "LinkedIn Learning"
    },
    deeplearning: {
        baseUrl: "https://www.deeplearning.ai/courses/",
        name: "DeepLearning.ai"
    },
    youtube: {
        baseUrl: "https://www.youtube.com/results?search_query=",
        name: "YouTube"
    },
    aws: {
        baseUrl: "https://aws.amazon.com/training/learn-about/",
        name: "AWS Training"
    },
    amazon: {
        baseUrl: "https://aws.amazon.com/training/learn-about/",
        name: "Amazon Web Services"
    },
    google: {
        baseUrl: "https://cloud.google.com/training/courses/",
        name: "Google Cloud Training"
    },
    googlecloud: {
        baseUrl: "https://cloud.google.com/training/courses/",
        name: "Google Cloud"
    },
    microsoft: {
        baseUrl: "https://docs.microsoft.com/en-us/learn/browse/?terms=",
        name: "Microsoft Learn"
    },
    facebook: {
        baseUrl: "https://developers.facebook.com/docs/",
        name: "Facebook"
    },
    mozilla: {
        baseUrl: "https://developer.mozilla.org/en-US/search?q=",
        name: "Mozilla"
    },
    oreilly: {
        baseUrl: "https://www.oreilly.com/search/?q=",
        name: "O'Reilly Media"
    },
    pearson: {
        baseUrl: "https://www.pearson.com/us/higher-education/products-services-teaching/learning-engagement-tools/search.html?q=",
        name: "Pearson"
    },
    bytebyteGo: {
        baseUrl: "https://bytebytego.com/courses/",
        name: "ByteByteGo"
    },
    itrevolution: {
        baseUrl: "https://itrevolution.com/book/",
        name: "IT Revolution Press"
    },
    cloudnative: {
        baseUrl: "https://www.cncf.io/certification/",
        name: "Cloud Native Computing Foundation"
    },
    projectmanagement: {
        baseUrl: "https://www.pmi.org/certifications/",
        name: "Project Management Institute"
    },
    pythonsoftware: {
        baseUrl: "https://docs.python.org/3/search.html?q=",
        name: "Python Software Foundation"
    },
    stanford: {
        baseUrl: "https://online.stanford.edu/search-catalog?keywords=",
        name: "Stanford University"
    },
    washington: {
        baseUrl: "https://www.pce.uw.edu/search?q=",
        name: "University of Washington"
    },
    hongkong: {
        baseUrl: "https://www.edx.org/school/hkustx",
        name: "University of Hong Kong"
    }
};

// YouTube Channels mapping for specific skills
const YOUTUBE_CHANNELS: Record<string, Array<{name: string, url: string, description: string}>> = {
    // Programming & Development
    "python": [
        { name: "Corey Schafer", url: "https://www.youtube.com/@coreyms", description: "Python tutorials and best practices" },
        { name: "Programming with Mosh", url: "https://www.youtube.com/@programmingwithmosh", description: "Python fundamentals and advanced concepts" },
        { name: "Real Python", url: "https://www.youtube.com/@realpython", description: "Professional Python development" }
    ],
    "javascript": [
        { name: "Traversy Media", url: "https://www.youtube.com/@TraversyMedia", description: "JavaScript and web development" },
        { name: "The Net Ninja", url: "https://www.youtube.com/@NetNinja", description: "Modern JavaScript frameworks" },
        { name: "JavaScript Mastery", url: "https://www.youtube.com/@javascriptmastery", description: "Advanced JavaScript projects" }
    ],
    "react": [
        { name: "React", url: "https://www.youtube.com/@reactjs", description: "Official React channel" },
        { name: "Academind", url: "https://www.youtube.com/@academind", description: "React tutorials and best practices" },
        { name: "Codevolution", url: "https://www.youtube.com/@Codevolution", description: "React comprehensive tutorials" }
    ],
    "java": [
        { name: "Java Brains", url: "https://www.youtube.com/@Java.Brains", description: "Java enterprise development" },
        { name: "Derek Banas", url: "https://www.youtube.com/@derekbanas", description: "Java programming tutorials" },
        { name: "Coding with John", url: "https://www.youtube.com/@CodingWithJohn", description: "Java fundamentals" }
    ],
    "spring": [
        { name: "Spring Developer", url: "https://www.youtube.com/@SpringSourceDev", description: "Official Spring Framework channel" },
        { name: "Java Brains", url: "https://www.youtube.com/@Java.Brains", description: "Spring Boot and microservices" },
        { name: "Dan Vega", url: "https://www.youtube.com/@danvega", description: "Spring Boot tutorials" }
    ],
    // Data & Analytics
    "data science": [
        { name: "3Blue1Brown", url: "https://www.youtube.com/@3blue1brown", description: "Mathematical concepts for data science" },
        { name: "StatQuest", url: "https://www.youtube.com/@statquest", description: "Statistics and machine learning" },
        { name: "Krish Naik", url: "https://www.youtube.com/@krishnaik06", description: "Data science and ML tutorials" }
    ],
    "machine learning": [
        { name: "Two Minute Papers", url: "https://www.youtube.com/@TwoMinutePapers", description: "Latest ML research explained" },
        { name: "Andrew Ng", url: "https://www.youtube.com/@AndrewNgDeepLearning", description: "Machine learning fundamentals" },
        { name: "Sentdex", url: "https://www.youtube.com/@sentdex", description: "Python for ML and AI" }
    ],
    "sql": [
        { name: "Alex The Analyst", url: "https://www.youtube.com/@AlexTheAnalyst", description: "SQL for data analysis" },
        { name: "Ben Awad", url: "https://www.youtube.com/@benawad", description: "Database design and SQL" },
        { name: "techTFQ", url: "https://www.youtube.com/@techTFQ", description: "Advanced SQL tutorials" }
    ],
    // Cloud & DevOps
    "aws": [
        { name: "AWS", url: "https://www.youtube.com/@amazonwebservices", description: "Official AWS channel" },
        { name: "A Cloud Guru", url: "https://www.youtube.com/@acloudguru", description: "AWS certification training" },
        { name: "Stephane Maarek", url: "https://www.youtube.com/@StephaneMaarek", description: "AWS tutorials and certification prep" }
    ],
    "azure": [
        { name: "Microsoft Azure", url: "https://www.youtube.com/@MicrosoftAzure", description: "Official Azure channel" },
        { name: "John Savill's Technical Training", url: "https://www.youtube.com/@NTFAQGuy", description: "Azure deep dives" },
        { name: "Azure Academy", url: "https://www.youtube.com/@AzureAcademy", description: "Azure tutorials and tips" }
    ],
    "docker": [
        { name: "Docker", url: "https://www.youtube.com/@DockerIo", description: "Official Docker channel" },
        { name: "TechWorld with Nana", url: "https://www.youtube.com/@TechWorldwithNana", description: "Docker and Kubernetes tutorials" },
        { name: "NetworkChuck", url: "https://www.youtube.com/@NetworkChuck", description: "Docker for beginners" }
    ],
    "kubernetes": [
        { name: "Kubernetes", url: "https://www.youtube.com/@kubernetescommunity", description: "Official Kubernetes channel" },
        { name: "TechWorld with Nana", url: "https://www.youtube.com/@TechWorldwithNana", description: "Kubernetes comprehensive tutorials" },
        { name: "Just me and Opensource", url: "https://www.youtube.com/@wenkatn-justmeandopensource", description: "Kubernetes practical guides" }
    ],
    "devops": [
        { name: "DevOps Toolkit", url: "https://www.youtube.com/@DevOpsToolkit", description: "DevOps tools and practices" },
        { name: "TechWorld with Nana", url: "https://www.youtube.com/@TechWorldwithNana", description: "Complete DevOps roadmap" },
        { name: "Continuous Delivery", url: "https://www.youtube.com/@ContinuousDelivery", description: "DevOps best practices" }
    ],
    // System Design & Architecture
    "system design": [
        { name: "Gaurav Sen", url: "https://www.youtube.com/@gkcs", description: "System design interviews" },
        { name: "Tech Dummies", url: "https://www.youtube.com/@TechDummiesNarendraL", description: "System design concepts" },
        { name: "Success in Tech", url: "https://www.youtube.com/@SuccessinTech", description: "System design for interviews" }
    ],
    "microservices": [
        { name: "Java Brains", url: "https://www.youtube.com/@Java.Brains", description: "Microservices with Spring Boot" },
        { name: "TechPrimers", url: "https://www.youtube.com/@TechPrimers", description: "Microservices architecture" },
        { name: "Defog Tech", url: "https://www.youtube.com/@DefogTech", description: "Microservices design patterns" }
    ],
    // General Tech
    "programming": [
        { name: "freeCodeCamp.org", url: "https://www.youtube.com/@freecodecamp", description: "Free programming courses" },
        { name: "CS Dojo", url: "https://www.youtube.com/@CSDojo", description: "Programming fundamentals" },
        { name: "Fireship", url: "https://www.youtube.com/@Fireship", description: "Quick programming tutorials" }
    ],
    "web development": [
        { name: "Traversy Media", url: "https://www.youtube.com/@TraversyMedia", description: "Full-stack web development" },
        { name: "The Net Ninja", url: "https://www.youtube.com/@NetNinja", description: "Modern web technologies" },
        { name: "Web Dev Simplified", url: "https://www.youtube.com/@WebDevSimplified", description: "Simplified web development" }
    ]
};

// Function to get YouTube channels for a skill
const getYouTubeChannelsForSkill = (skill: string): Array<{name: string, url: string, description: string}> => {
    const normalizedSkill = skill.toLowerCase().trim();
    
    // Direct match
    if (YOUTUBE_CHANNELS[normalizedSkill]) {
        return YOUTUBE_CHANNELS[normalizedSkill];
    }
    
    // Partial matches
    const matchingChannels: Array<{name: string, url: string, description: string}> = [];
    
    Object.keys(YOUTUBE_CHANNELS).forEach(key => {
        if (normalizedSkill.includes(key) || key.includes(normalizedSkill)) {
            matchingChannels.push(...YOUTUBE_CHANNELS[key]);
        }
    });
    
    // Remove duplicates
    const uniqueChannels = matchingChannels.filter((channel, index, self) => 
        index === self.findIndex(c => c.url === channel.url)
    );
    
    return uniqueChannels.slice(0, 3); // Limit to 3 channels
};

// Function to create course links
const createCourseLink = (courseName: string, platform: string) => {
    const platformKey = platform.toLowerCase()
        .replace(/[^a-z]/g, '')
        .replace(/university/g, '')
        .replace(/web/g, '')
        .replace(/services/g, '')
        .replace(/learning/g, '')
        .replace(/media/g, '')
        .replace(/press/g, '')
        .replace(/foundation/g, '')
        .replace(/institute/g, '')
        .replace(/software/g, '')
        .replace(/computing/g, '')
        .replace(/native/g, '')
        .replace(/cloud/g, '')
        .replace(/management/g, '')
        .replace(/project/g, '');
    
    const platformInfo = COURSE_PLATFORMS[platformKey as keyof typeof COURSE_PLATFORMS];
    
    if (platformInfo) {
        const searchQuery = encodeURIComponent(courseName.replace(/["""]/g, ''));
        return `${platformInfo.baseUrl}${searchQuery}`;
    }
    
    // Default to Google search if platform not found
    return `https://www.google.com/search?q=${encodeURIComponent(courseName + ' ' + platform + ' course')}`;
};

// Enhanced text processor to convert course mentions to links and add YouTube channels
const processTextWithCourseLinks = (text: string) => {
    // Pattern to match course names in quotes followed by platform mentions
    const coursePattern = /\*\*[""]([^"""]+)[""](?:\s+by\s+([^*\n]+?))\*\*/g;
    
    let processedText = text.replace(coursePattern, (match, courseName, platform) => {
        if (courseName && platform) {
            const link = createCourseLink(courseName.trim(), platform.trim());
            return `**[📚 "${courseName.trim()}"](${link})** by ${platform.trim()}`;
        }
        return match;
    });
    
    // Add YouTube channels section for skills mentioned in the text
    const skillsToCheck = [
        'python', 'javascript', 'react', 'java', 'spring', 'data science', 
        'machine learning', 'sql', 'aws', 'azure', 'docker', 'kubernetes', 
        'devops', 'system design', 'microservices', 'programming', 'web development'
    ];
    
    const mentionedSkills = skillsToCheck.filter(skill => 
        processedText.toLowerCase().includes(skill.toLowerCase())
    );
    
    if (mentionedSkills.length > 0) {
        let youtubeSection = '\n\n## 📺 Recommended YouTube Channels\n\n';
        
        mentionedSkills.forEach(skill => {
            const channels = getYouTubeChannelsForSkill(skill);
            if (channels.length > 0) {
                youtubeSection += `### ${skill.charAt(0).toUpperCase() + skill.slice(1)} Channels:\n`;
                channels.forEach(channel => {
                    youtubeSection += `- **[🎥 ${channel.name}](${channel.url})** - ${channel.description}\n`;
                });
                youtubeSection += '\n';
            }
        });
        
        // Insert YouTube section before any existing recommendations section
        const recommendationsIndex = processedText.indexOf('## 4. RECOMMENDED LEARNING PATH');
        if (recommendationsIndex !== -1) {
            processedText = processedText.slice(0, recommendationsIndex) + youtubeSection + processedText.slice(recommendationsIndex);
        } else {
            processedText += youtubeSection;
        }
    }
    
    return processedText;
};

// Enhanced ReactMarkdown component with course link processing
const EnhancedMarkdown = ({ children }: { children: string }) => {
    const processedContent = processTextWithCourseLinks(children);
    
    return (
        <ReactMarkdown
            components={{
                h1: ({ node, ...props }) => (
                    <h1 className="text-3xl font-bold text-green-900 dark:text-green-100 mb-6 border-b-2 border-green-200 dark:border-green-800 pb-3" {...props} />
                ),
                h2: ({ node, ...props }) => (
                    <h2 className="text-2xl font-semibold text-green-800 dark:text-green-200 mb-4 mt-8" {...props} />
                ),
                h3: ({ node, ...props }) => (
                    <h3 className="text-xl font-semibold text-green-700 dark:text-green-300 mb-3 mt-6" {...props} />
                ),
                h4: ({ node, ...props }) => (
                    <h4 className="text-lg font-semibold text-green-600 dark:text-green-400 mb-2 mt-4" {...props} />
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
                    <li className="text-gray-700 dark:text-gray-300 leading-relaxed text-base" {...props} />
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
                a: ({ node, href, children, ...props }) => (
                    <a 
                        href={href} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 underline font-medium transition-colors duration-200"
                        {...props}
                    >
                        {children}
                        <svg className="inline-block w-3 h-3 ml-1 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                        </svg>
                    </a>
                ),
            }}
        >
            {processedContent}
        </ReactMarkdown>
    );
};

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
                            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Skill Gap Analysis</h1>
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
                        <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">📊 Skill Gap Analysis</h2>
                        <p className="text-gray-600 dark:text-gray-300">
                            Compare your current skills with job requirements to identify gaps and learning opportunities. 
                            Get personalized recommendations for skill development with direct links to courses.
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
                        <div className="mt-8 p-8 border rounded-lg bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/30 border-green-200 dark:border-green-700 shadow-lg">
                            <h3 className="text-2xl font-semibold mb-6 text-green-900 dark:text-green-100 flex items-center">
                                🎯 Your Skill Gap Analysis
                                <span className="ml-3 text-sm font-normal text-green-700 dark:text-green-300">
                                    Click on course links to visit learning platforms
                                </span>
                            </h3>
                            <div className="prose prose-lg max-w-none text-gray-800 dark:text-gray-200">
                                <EnhancedMarkdown>
                                    {skillGapAnalysis}
                                </EnhancedMarkdown>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
} 