"use client";

import { useState, useEffect, useRef } from "react";
import { useAuth, useUser, SignOutButton } from "@clerk/nextjs";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Label } from "@/components/ui/Label";
import { Textarea } from "@/components/ui/Textarea";
import { ThemeToggle } from "@/components/ui/ThemeToggle";
import Link from "next/link";
import ReactMarkdown from "react-markdown";
import SkillGapAIAnimation from "@/components/ui/SkillGapAIAnimation";
import { useUserProfile } from "@/contexts/UserProfileContext";

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

// Function to process text and convert specific sections to bullet points
const processTextForBulletPoints = (text: string) => {
    // Sections that should have sentences converted to bullet points
    const sectionsToProcess = [
        "1. PROFESSIONAL PROFILE ASSESSMENT",
        "2. SKILL MATCH ANALYSIS", 
        "4. EXPERIENCE & BACKGROUND ANALYSIS",
        "6. CAREER STRATEGY RECOMMENDATIONS",
        "8. MARKET INSIGHTS FOR YOUR PROFILE"
    ];
    
    let processedText = text;
    
    sectionsToProcess.forEach(sectionTitle => {
        // Find the section in the text
        const sectionStart = processedText.indexOf(`## ${sectionTitle}`);
        if (sectionStart === -1) return;
        
        // Find the next section (starts with ##)
        const nextSectionMatch = processedText.substring(sectionStart + sectionTitle.length + 3).match(/\n## /);
        const sectionEnd = nextSectionMatch && nextSectionMatch.index !== undefined
            ? sectionStart + sectionTitle.length + 3 + nextSectionMatch.index
            : processedText.length;
        
        // Extract the section content
        const sectionContent = processedText.substring(sectionStart, sectionEnd);
        
        // Process the content to convert sentences to bullet points
        const lines = sectionContent.split('\n');
        const processedLines = lines.map(line => {
            // Skip the section header, empty lines, already formatted lines, and sub-headers
            if (line.startsWith('## ') || 
                line.trim() === '' || 
                line.startsWith('**') || 
                line.startsWith('- ') || 
                line.startsWith('* ') ||
                line.includes(':**') ||
                line.startsWith('#') ||
                line.startsWith('###') ||
                line.startsWith('####')) {
                return line;
            }
            
            // Only convert lines that look like descriptive sentences (not headers or special formatting)
            if (line.trim() && 
                line.length > 20 && // Only process substantial content
                !line.match(/^\s*\*\*.*\*\*\s*$/) && // Skip bold-only lines
                !line.includes('|') && // Skip table content
                line.includes(' ')) { // Must contain spaces (actual sentences)
                
                // Split by sentence endings and create bullet points
                const sentences = line.split(/(?<=[.!?])\s+/).filter(s => s.trim());
                if (sentences.length > 1) {
                    return sentences.map(sentence => `- ${sentence.trim()}`).join('\n');
                } else if (line.trim().endsWith('.') || line.trim().endsWith('!') || line.trim().endsWith('?')) {
                    return `- ${line.trim()}`;
                }
            }
            
            return line;
        });
        
        const processedSection = processedLines.join('\n');
        processedText = processedText.substring(0, sectionStart) + processedSection + processedText.substring(sectionEnd);
    });
    
    return processedText;
};

// Enhanced ReactMarkdown component with course link processing
const EnhancedMarkdown = ({ children }: { children: string }) => {
    const processedContent = processTextWithCourseLinks(processTextForBulletPoints(children));
    
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
    const { userProfile } = useUserProfile();
    
    // State for Skill Gap Analysis
    const [jobDescription, setJobDescription] = useState("");
    const [targetRole, setTargetRole] = useState("");
    const [skillGapAnalysis, setSkillGapAnalysis] = useState("");
    const [loadingSkillGap, setLoadingSkillGap] = useState(false);
    const [showAllSkills, setShowAllSkills] = useState(false);
    
    // Ref for auto-scrolling to response section
    const responseRef = useRef<HTMLDivElement>(null);

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
                    skills: [], // Skills will be read from user profile in backend
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
            
            // Auto-scroll to response section after analysis is complete
            setTimeout(() => {
                if (responseRef.current) {
                    responseRef.current.scrollIntoView({ 
                        behavior: 'smooth', 
                        block: 'start' 
                    });
                }
            }, 100);
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
                {/* AI-Powered Skill Gap Analysis Section */}
                <div className="mb-8 bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-purple-200 dark:border-purple-700/30 overflow-hidden">
                    <div className="p-6 bg-gradient-to-r from-purple-50 via-blue-50 to-indigo-50 dark:from-purple-900/20 dark:via-blue-900/20 dark:to-indigo-900/20">
                        <div className="flex items-center justify-between mb-4">
                            <div className="flex items-center space-x-3">
                                <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-blue-600 rounded-lg flex items-center justify-center shadow-lg">
                                    <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <circle cx="12" cy="12" r="10" strokeWidth="2"/>
                                        <circle cx="12" cy="12" r="6" strokeWidth="2"/>
                                        <circle cx="12" cy="12" r="2" strokeWidth="2"/>
                                        <path d="M12 2v4M12 18v4M2 12h4M18 12h4" strokeWidth="2"/>
                                    </svg>
                                </div>
                                <div>
                                    <h2 className="text-2xl font-bold text-purple-900 dark:text-purple-100">AI-Powered Skill Gap Analysis</h2>
                                    <p className="text-purple-700 dark:text-purple-300 text-sm">Let AI guide you to your dream job</p>
                                </div>
                            </div>
                            <div className="hidden md:flex items-center space-x-2 text-purple-600 dark:text-purple-400">
                                <div className="w-2 h-2 bg-purple-400 rounded-full animate-pulse"></div>
                                <span className="text-sm font-medium">AI Analysis Active</span>
                            </div>
                        </div>
                        
                        <SkillGapAIAnimation 
                            isAnalyzing={loadingSkillGap}
                            targetRole={targetRole || "your target role"}
                            userSkills={userProfile?.skills || []}
                        />
                    </div>
                </div>

                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-8">
                    <div className="mb-8">
                        <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">📊 Skill Gap Analysis</h2>
                        <p className="text-gray-600 dark:text-gray-300 mb-4">
                            🤖 AI analyzes your complete professional profile - skills, experience, certifications, job history, and education - 
                            against target job requirements to identify gaps and provide personalized learning guidance with direct course links.
                        </p>
                        
                        {/* Motivational Cards */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
                            <div className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/30 p-4 rounded-lg border border-blue-200 dark:border-blue-700">
                                <div className="flex items-center space-x-3">
                                    <div className="text-2xl">🎯</div>
                                    <div>
                                        <h3 className="font-semibold text-blue-900 dark:text-blue-100">Identify Gaps</h3>
                                        <p className="text-blue-700 dark:text-blue-300 text-sm">Know exactly what to learn</p>
                                    </div>
                                </div>
                            </div>
                            
                            <div className="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/30 p-4 rounded-lg border border-purple-200 dark:border-purple-700">
                                <div className="flex items-center space-x-3">
                                    <div className="text-2xl">📚</div>
                                    <div>
                                        <h3 className="font-semibold text-purple-900 dark:text-purple-100">Get Resources</h3>
                                        <p className="text-purple-700 dark:text-purple-300 text-sm">Direct links to courses</p>
                                    </div>
                                </div>
                            </div>
                            
                            <div className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/30 p-4 rounded-lg border border-green-200 dark:border-green-700">
                                <div className="flex items-center space-x-3">
                                    <div className="text-2xl">🚀</div>
                                    <div>
                                        <h3 className="font-semibold text-green-900 dark:text-green-100">Land the Job</h3>
                                        <p className="text-green-700 dark:text-green-300 text-sm">Secure your dream role</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <form onSubmit={handleSkillGapSubmit} className="space-y-6">
                        {/* User Profile Summary */}
                        {userProfile && (
                            <div className="bg-blue-50 dark:bg-blue-900/20 p-6 rounded-lg border border-blue-200 dark:border-blue-700">
                                <h3 className="font-semibold text-blue-900 dark:text-blue-100 mb-4 flex items-center">
                                    <span className="mr-2">📋</span>
                                    Your Profile Summary
                                </h3>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm">
                                    <div className="space-y-3">
                                        <div>
                                            <p className="text-blue-800 dark:text-blue-200">
                                                <strong>👤 Name:</strong> {userProfile.firstName && userProfile.lastName ? `${userProfile.firstName} ${userProfile.lastName}` : userProfile.fullName || "Not specified"}
                                            </p>
                                        </div>
                                        <div>
                                            <p className="text-blue-800 dark:text-blue-200">
                                                <strong>💼 Experience:</strong> {userProfile.experienceYears > 0 ? `${userProfile.experienceYears} years` : "Not specified"}
                                            </p>
                                        </div>
                                        <div>
                                            <p className="text-blue-800 dark:text-blue-200">
                                                <strong>📧 Email:</strong> {userProfile.email || "Not specified"}
                                            </p>
                                        </div>
                                        <div>
                                            <p className="text-blue-800 dark:text-blue-200">
                                                <strong>📍 Location:</strong> {userProfile.location || "Not specified"}
                                            </p>
                                        </div>
                                    </div>
                                    <div className="space-y-3">
                                        <div>
                                            <p className="text-blue-800 dark:text-blue-200">
                                                <strong>🏢 Recent Roles:</strong> {userProfile.lastThreeJobTitles?.length > 0 ? userProfile.lastThreeJobTitles.slice(0, 2).join(", ") + (userProfile.lastThreeJobTitles.length > 2 ? "..." : "") : "Not specified"}
                                            </p>
                                        </div>
                                        <div>
                                            <p className="text-blue-800 dark:text-blue-200">
                                                <strong>🎓 Education:</strong> {userProfile.education?.length > 0 ? userProfile.education.slice(0, 2).join(", ") + (userProfile.education.length > 2 ? "..." : "") : "Not specified"}
                                            </p>
                                        </div>
                                        <div>
                                            <p className="text-blue-800 dark:text-blue-200">
                                                <strong>🏆 Certifications:</strong> {userProfile.certifications?.length > 0 ? userProfile.certifications.slice(0, 2).join(", ") + (userProfile.certifications.length > 2 ? "..." : "") : "Not specified"}
                                            </p>
                                        </div>
                                        <div>
                                            <p className="text-blue-800 dark:text-blue-200">
                                                <strong>📝 Experience Summary:</strong> {userProfile.experience ? (userProfile.experience.length > 100 ? userProfile.experience.substring(0, 100) + "..." : userProfile.experience) : "Not specified"}
                                            </p>
                                        </div>
                                    </div>
                                </div>
                                
                                {/* Skills Section with More >> functionality */}
                                <div className="mt-4 pt-4 border-t border-blue-200 dark:border-blue-700">
                                    <div className="flex items-center justify-between mb-2">
                                        <p className="text-blue-800 dark:text-blue-200 font-medium">
                                            <strong>🛠️ Skills ({userProfile.skills?.length || 0}):</strong>
                                        </p>
                                        {userProfile.skills?.length > 10 && (
                                            <button
                                                onClick={() => setShowAllSkills(!showAllSkills)}
                                                className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-200 text-sm font-medium underline transition-colors"
                                            >
                                                {showAllSkills ? "Show Less <<" : "More >>"}
                                            </button>
                                        )}
                                    </div>
                                    <div className="flex flex-wrap gap-2">
                                        {userProfile.skills?.length > 0 ? (
                                            (showAllSkills ? userProfile.skills : userProfile.skills.slice(0, 10)).map((skill, index) => (
                                                <span
                                                    key={index}
                                                    className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-100 dark:bg-blue-800 text-blue-800 dark:text-blue-200 border border-blue-200 dark:border-blue-600"
                                                >
                                                    {skill}
                                                </span>
                                            ))
                                        ) : (
                                            <span className="text-blue-600 dark:text-blue-400 text-sm italic">No skills specified</span>
                                        )}
                                    </div>
                                    {!showAllSkills && userProfile.skills?.length > 10 && (
                                        <p className="text-xs text-blue-600 dark:text-blue-400 mt-2">
                                            Showing 10 of {userProfile.skills.length} skills
                                        </p>
                                    )}
                                </div>

                                {/* Show different messages based on whether profile data exists */}
                                {userProfile.skills?.length > 0 && userProfile.experienceYears > 0 ? (
                                    <div className="mt-4 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-700">
                                        <p className="text-xs text-green-700 dark:text-green-300 flex items-center">
                                            <span className="mr-2">✨</span>
                                            AI will analyze your complete profile automatically - no need to re-enter your skills!
                                        </p>
                                    </div>
                                ) : (
                                    <div className="mt-4 p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-700">
                                        <p className="text-xs text-yellow-700 dark:text-yellow-300">
                                            <span className="mr-2">💡</span>
                                            <Link href="/dashboard" className="underline hover:text-yellow-800 dark:hover:text-yellow-200 font-medium">Upload your CV on the dashboard</Link> to populate your profile with accurate data for better analysis.
                                            <br />
                                            <span className="mr-2">✨</span>
                                            AI will still analyze based on the job description, but having your profile data makes it much more personalized!
                                        </p>
                                    </div>
                                )}
                            </div>
                        )}
                        
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
                        
                        <Button 
                            type="submit" 
                            disabled={loadingSkillGap} 
                            className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white font-semibold py-3 px-6 rounded-lg shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
                        >
                            {loadingSkillGap ? (
                                <div className="flex items-center justify-center space-x-2">
                                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                                    <span>🤖 AI Analyzing Your Skills...</span>
                                </div>
                            ) : (
                                <div className="flex items-center justify-center space-x-2">
                                    <span>🚀 Start AI Analysis</span>
                                </div>
                            )}
                        </Button>
                    </form>

                    {skillGapAnalysis && (
                        <div ref={responseRef} className="mt-8 space-y-6">
                            {/* AI Success Banner */}
                            <div className="bg-gradient-to-r from-green-500 to-emerald-600 rounded-xl p-6 text-white shadow-lg">
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center space-x-4">
                                        <div className="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center">
                                            <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                                                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                                            </svg>
                                        </div>
                                        <div>
                                            <h3 className="text-xl font-bold">🎉 AI Analysis Complete!</h3>
                                            <p className="text-green-100">Your personalized roadmap to {targetRole || "success"} is ready</p>
                                        </div>
                                    </div>
                                    <div className="hidden md:flex items-center space-x-3">
                                        <div className="text-center">
                                            <div className="text-2xl font-bold">🚀</div>
                                            <div className="text-xs">Ready to Launch</div>
                                        </div>
                                        <div className="text-center">
                                            <div className="text-2xl font-bold">💪</div>
                                            <div className="text-xs">You Got This</div>
                                        </div>
                                        <div className="text-center">
                                            <div className="text-2xl font-bold">🎯</div>
                                            <div className="text-xs">Goal Focused</div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Analysis Results */}
                            <div className="p-8 border rounded-lg bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/30 border-green-200 dark:border-green-700 shadow-lg">
                                <div className="flex items-center justify-between mb-6">
                                    <h3 className="text-2xl font-semibold text-green-900 dark:text-green-100 flex items-center">
                                        🎯 Your AI-Powered Career Roadmap
                                    </h3>
                                    <div className="flex items-center space-x-2 text-green-700 dark:text-green-300">
                                        <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                                        <span className="text-sm font-medium">Click course links to start learning</span>
                                    </div>
                                </div>
                                
                                {/* Motivational Message */}
                                <div className="mb-6 p-4 bg-white/60 dark:bg-gray-800/60 rounded-lg border border-green-200 dark:border-green-700">
                                    <div className="flex items-center space-x-3">
                                        <div className="text-2xl">🤖</div>
                                        <div>
                                            <p className="text-green-800 dark:text-green-200 font-medium">
                                                <strong>AI Insight:</strong> Based on your skills and target role, I've identified the most impactful areas for growth. 
                                                Follow this roadmap and you'll be ready to secure {targetRole || "your dream job"} sooner than you think!
                                            </p>
                                        </div>
                                    </div>
                                </div>

                                <div className="prose prose-lg max-w-none text-gray-800 dark:text-gray-200">
                                    <EnhancedMarkdown>
                                        {skillGapAnalysis}
                                    </EnhancedMarkdown>
                                </div>

                                {/* Action Encouragement */}
                                <div className="mt-8 p-4 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-lg border border-blue-200 dark:border-blue-700">
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center space-x-3">
                                            <div className="text-2xl">💡</div>
                                            <div>
                                                <h4 className="font-semibold text-blue-900 dark:text-blue-100">Ready to Take Action?</h4>
                                                <p className="text-blue-700 dark:text-blue-300 text-sm">
                                                    Start with the highest priority skills and track your progress. Every step brings you closer to your goal!
                                                </p>
                                            </div>
                                        </div>
                                        <div className="hidden md:block">
                                            <div className="text-4xl animate-bounce">🎯</div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
} 