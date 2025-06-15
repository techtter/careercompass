"use client";

import React from 'react';

interface UserProfile {
  firstName: string;
  lastName: string;
  skills: string[];
  experienceYears: number;
  lastThreeJobTitles: string[];
  location?: string;
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
  is_real_job?: boolean;
  match_score?: number;
}

interface JobAIAnimationProps {
  userProfile?: UserProfile | null;
  jobs?: JobRecommendation[];
}

export default function JobAIAnimation({ userProfile, jobs = [] }: JobAIAnimationProps) {
  // Generate dynamic job matching text based on user profile and actual jobs
  const generateJobMatches = () => {
    if (!userProfile || !jobs.length) {
      // Fallback to generic matches if no data available
      return [
        { title: 'Software Engineer', match: 85 },
        { title: 'Full Stack Developer', match: 80 },
        { title: 'Frontend Developer', match: 75 }
      ];
    }

    // Get top 3 jobs with highest match scores or most relevant titles
    const topJobs = jobs
      .filter(job => job.title && job.title.trim().length > 0)
      .sort((a, b) => {
        // Sort by match_score if available, otherwise by relevance to user skills
        if (a.match_score && b.match_score) {
          return b.match_score - a.match_score;
        }
        
        // Calculate relevance based on user's skills and job titles
        const aRelevance = calculateJobRelevance(a, userProfile);
        const bRelevance = calculateJobRelevance(b, userProfile);
        return bRelevance - aRelevance;
      })
      .slice(0, 3)
      .map((job, index) => ({
        title: job.title,
        match: job.match_score || (95 - index * 5) // Use actual match score or generate decreasing scores
      }));

    return topJobs.length > 0 ? topJobs : [
      { title: 'Software Engineer', match: 85 },
      { title: 'Full Stack Developer', match: 80 },
      { title: 'Frontend Developer', match: 75 }
    ];
  };

  // Calculate job relevance based on user profile
  const calculateJobRelevance = (job: JobRecommendation, profile: UserProfile): number => {
    let relevance = 0;
    const jobTitle = job.title.toLowerCase();
    const jobDescription = job.description.toLowerCase();
    
    // Check skill matches
    profile.skills.forEach(skill => {
      const skillLower = skill.toLowerCase();
      if (jobTitle.includes(skillLower) || jobDescription.includes(skillLower)) {
        relevance += 10;
      }
    });
    
    // Check job title matches
    profile.lastThreeJobTitles.forEach(jobTitleUser => {
      const userJobLower = jobTitleUser.toLowerCase();
      if (jobTitle.includes(userJobLower) || userJobLower.includes(jobTitle.split(' ')[0])) {
        relevance += 15;
      }
    });
    
    return relevance;
  };

  const jobMatches = generateJobMatches();

  return (
    <div className="relative flex items-center justify-center p-6 my-4 bg-gradient-to-r from-blue-500/10 via-purple-500/10 to-indigo-500/10 rounded-xl border border-blue-200 dark:border-blue-700/50 overflow-hidden">
      {/* Background Neural Network */}
      <div className="absolute inset-0 w-full h-full">
        {/* Floating Job Icons */}
        {Array.from({ length: 8 }).map((_, i) => (
          <div
            key={`job-${i}`}
            className="absolute animate-pulse"
            style={{
              top: `${20 + (i * 10)}%`,
              left: `${10 + (i * 10)}%`,
              animationDelay: `${i * 0.3}s`,
              animationDuration: '2s'
            }}
          >
            <div className="w-3 h-3 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full opacity-60"></div>
          </div>
        ))}
        
        {/* Connection Lines */}
        {Array.from({ length: 4 }).map((_, i) => (
          <div
            key={`line-${i}`}
            className="absolute h-px bg-gradient-to-r from-blue-500/20 via-purple-500/30 to-blue-500/20 animate-pulse"
            style={{
              top: `${25 + (i * 20)}%`,
              left: '0%',
              right: '0%',
              animationDelay: `${i * 0.4}s`,
              animationDuration: '3s'
            }}
          />
        ))}
      </div>

      {/* Central AI Brain */}
      <div className="relative z-10 flex items-center space-x-6">
        <div className="relative">
          {/* Rotating Rings */}
          <div className="absolute inset-0 border-4 border-blue-500/30 rounded-full animate-spin-slow"></div>
          <div className="absolute inset-1 border-4 border-purple-500/30 rounded-full animate-reverse-spin"></div>
          
          {/* AI Core */}
          <div className="relative w-16 h-16 rounded-full bg-gradient-to-br from-blue-600 via-purple-600 to-indigo-600 animate-pulse p-1">
            <div className="absolute inset-1 bg-white/10 rounded-full backdrop-blur-sm flex items-center justify-center">
              <span className="text-white font-bold text-xs animate-pulse">AI</span>
            </div>
          </div>
        </div>

        {/* AI Status Messages */}
        <div className="flex flex-col space-y-2">
          <div className="flex items-center space-x-2 animate-fadeIn">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-ping"></div>
            <span className="text-sm text-blue-700 dark:text-blue-300 font-medium">
              {userProfile ? `Analyzing ${userProfile.firstName}'s Profile` : 'AI Analyzing Your Profile'}
            </span>
          </div>
          <div className="flex items-center space-x-2 animate-fadeIn" style={{animationDelay: '0.5s'}}>
            <div className="w-2 h-2 bg-purple-500 rounded-full animate-ping" style={{animationDelay: '0.2s'}}></div>
            <span className="text-sm text-purple-700 dark:text-purple-300 font-medium">
              {userProfile && userProfile.skills.length > 0 
                ? `Matching ${userProfile.skills.length} Skills & ${userProfile.experienceYears} Years Experience`
                : 'Matching Skills & Experience'
              }
            </span>
          </div>
          <div className="flex items-center space-x-2 animate-fadeIn" style={{animationDelay: '1s'}}>
            <div className="w-2 h-2 bg-indigo-500 rounded-full animate-ping" style={{animationDelay: '0.4s'}}></div>
            <span className="text-sm text-indigo-700 dark:text-indigo-300 font-medium">
              {jobs.length > 0 
                ? `Found ${jobs.length} Perfect Career Matches`
                : 'Finding Perfect Career Matches'
              }
            </span>
          </div>
        </div>

        {/* Job Matching Visualization */}
        <div className="flex flex-col space-y-1">
          {jobMatches.map((job, i) => (
            <div key={job.title} className="flex items-center space-x-2 animate-fadeIn" style={{animationDelay: `${1.5 + i * 0.3}s`}}>
              <div className="w-1 h-1 bg-green-500 rounded-full animate-ping" style={{animationDelay: `${i * 0.1}s`}}></div>
              <span className="text-xs text-gray-600 dark:text-gray-400">{job.title}</span>
              <span className="text-xs text-green-600 dark:text-green-400 font-semibold">{job.match}% Match</span>
            </div>
          ))}
        </div>
      </div>

      {/* Floating Success Indicators */}
      <div className="absolute top-2 right-2 animate-bounce" style={{animationDelay: '2s'}}>
        <div className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center">
          <span className="text-white text-xs">✓</span>
        </div>
      </div>
      
      <div className="absolute bottom-2 left-2 animate-bounce" style={{animationDelay: '2.5s'}}>
        <div className="w-5 h-5 bg-blue-500 rounded-full flex items-center justify-center">
          <span className="text-white text-xs">🎯</span>
        </div>
      </div>
    </div>
  );
} 