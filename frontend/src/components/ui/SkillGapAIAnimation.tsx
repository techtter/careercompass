"use client";

import React from 'react';

interface SkillGapAIAnimationProps {
  isAnalyzing?: boolean;
  targetRole?: string;
  userSkills?: string[];
}

export default function SkillGapAIAnimation({ 
  isAnalyzing = false, 
  targetRole = "your target role",
  userSkills = []
}: SkillGapAIAnimationProps) {
  return (
    <div className="relative w-full h-64 bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-50 dark:from-purple-900/20 dark:via-blue-900/20 dark:to-indigo-900/20 rounded-xl overflow-hidden border border-purple-200 dark:border-purple-700/30">
      {/* Background Neural Network */}
      <div className="absolute inset-0 opacity-10 dark:opacity-20">
        <svg className="w-full h-full" viewBox="0 0 400 200">
          {/* Neural network connections */}
          <defs>
            <linearGradient id="connectionGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#8B5CF6" />
              <stop offset="50%" stopColor="#3B82F6" />
              <stop offset="100%" stopColor="#06B6D4" />
            </linearGradient>
          </defs>
          
          {/* Connection lines */}
          <g stroke="url(#connectionGradient)" strokeWidth="1" fill="none" opacity="0.6">
            <line x1="50" y1="50" x2="150" y2="80" className="animate-pulse" />
            <line x1="50" y1="100" x2="150" y2="80" className="animate-pulse" style={{animationDelay: '0.5s'}} />
            <line x1="50" y1="150" x2="150" y2="120" className="animate-pulse" style={{animationDelay: '1s'}} />
            <line x1="150" y1="80" x2="250" y2="60" className="animate-pulse" style={{animationDelay: '1.5s'}} />
            <line x1="150" y1="120" x2="250" y2="100" className="animate-pulse" style={{animationDelay: '2s'}} />
            <line x1="250" y1="60" x2="350" y2="100" className="animate-pulse" style={{animationDelay: '2.5s'}} />
            <line x1="250" y1="100" x2="350" y2="100" className="animate-pulse" style={{animationDelay: '3s'}} />
          </g>
          
          {/* Neural nodes */}
          <g fill="#8B5CF6" opacity="0.8">
            <circle cx="50" cy="50" r="4" className="animate-pulse" />
            <circle cx="50" cy="100" r="4" className="animate-pulse" style={{animationDelay: '0.3s'}} />
            <circle cx="50" cy="150" r="4" className="animate-pulse" style={{animationDelay: '0.6s'}} />
            <circle cx="150" cy="80" r="5" className="animate-pulse" style={{animationDelay: '0.9s'}} />
            <circle cx="150" cy="120" r="5" className="animate-pulse" style={{animationDelay: '1.2s'}} />
            <circle cx="250" cy="60" r="5" className="animate-pulse" style={{animationDelay: '1.5s'}} />
            <circle cx="250" cy="100" r="5" className="animate-pulse" style={{animationDelay: '1.8s'}} />
            <circle cx="350" cy="100" r="6" className="animate-pulse" style={{animationDelay: '2.1s'}} />
          </g>
        </svg>
      </div>

      {/* Main Content */}
      <div className="relative z-10 flex items-center justify-between h-full px-8">
        {/* Left: AI Brain with Analysis */}
        <div className="flex flex-col items-center space-y-3">
          <div className="relative">
            {/* AI Brain Core */}
            <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-blue-600 rounded-full flex items-center justify-center shadow-lg">
              <div className="text-white font-bold text-lg animate-pulse">AI</div>
            </div>
            
            {/* Rotating Analysis Ring */}
            <div className="absolute inset-0 w-16 h-16 border-2 border-purple-300 dark:border-purple-600 rounded-full animate-spin" style={{animationDuration: '3s'}}></div>
            <div className="absolute inset-1 w-14 h-14 border-2 border-blue-300 dark:border-blue-600 rounded-full animate-spin" style={{animationDuration: '2s', animationDirection: 'reverse'}}></div>
          </div>
          
          {/* AI Status Messages */}
          <div className="text-center">
            <div className="text-sm font-semibold text-purple-700 dark:text-purple-300 animate-pulse">
              {isAnalyzing ? "🔍 Analyzing Skills..." : "🎯 AI Skill Analyzer"}
            </div>
            <div className="text-xs text-purple-600 dark:text-purple-400 mt-1">
              {isAnalyzing ? "Identifying gaps" : "Ready to help"}
            </div>
          </div>
        </div>

        {/* Center: Skill Analysis Flow */}
        <div className="flex-1 mx-8">
          <div className="space-y-1.5">
            {/* Current Skills */}
            <div className="flex items-center space-x-3">
              <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
              <div className="text-sm text-gray-700 dark:text-gray-300">
                <span className="font-semibold text-green-600 dark:text-green-400">Your Skills:</span>
                <span className="ml-2">
                  {userSkills.length > 0 
                    ? userSkills.slice(0, 3).join(", ") + (userSkills.length > 3 ? "..." : "")
                    : "Python, React, SQL..."
                  }
                </span>
              </div>
            </div>

            {/* Analysis Arrow */}
            <div className="flex items-center justify-center py-0.5">
              <div className="text-purple-500 animate-bounce">
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </div>
            </div>

            {/* Target Role */}
            <div className="flex items-center space-x-3">
              <div className="w-3 h-3 bg-blue-500 rounded-full animate-pulse" style={{animationDelay: '0.5s'}}></div>
              <div className="text-sm text-gray-700 dark:text-gray-300">
                <span className="font-semibold text-blue-600 dark:text-blue-400">Target:</span>
                <span className="ml-2">{targetRole}</span>
              </div>
            </div>

            {/* Analysis Arrow */}
            <div className="flex items-center justify-center py-0.5">
              <div className="text-purple-500 animate-bounce" style={{animationDelay: '0.3s'}}>
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </div>
            </div>

            {/* Gap Analysis */}
            <div className="flex items-center space-x-3">
              <div className="w-3 h-3 bg-orange-500 rounded-full animate-pulse" style={{animationDelay: '1s'}}></div>
              <div className="text-sm text-gray-700 dark:text-gray-300">
                <span className="font-semibold text-orange-600 dark:text-orange-400">Gap Analysis:</span>
                <span className="ml-2">{isAnalyzing ? "In progress..." : "Ready to analyze"}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right: Success Indicators */}
        <div className="flex flex-col items-center space-y-4">
          {/* Success Target */}
          <div className="relative">
            <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-emerald-600 rounded-full flex items-center justify-center shadow-lg">
              <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="absolute -top-1 -right-1 w-4 h-4 bg-yellow-400 rounded-full animate-ping"></div>
          </div>

          {/* Motivational Messages */}
          <div className="text-center space-y-2">
            <div className="text-xs font-semibold text-green-700 dark:text-green-300">
              🚀 Career Growth
            </div>
            <div className="text-xs text-green-600 dark:text-green-400">
              Secure Your Dream Job
            </div>
          </div>

          {/* Floating Learning Icons */}
          <div className="relative">
            <div className="absolute -top-8 -left-4 text-blue-500 animate-bounce" style={{animationDelay: '0.5s'}}>
              📚
            </div>
            <div className="absolute -top-6 left-4 text-purple-500 animate-bounce" style={{animationDelay: '1s'}}>
              🎓
            </div>
            <div className="absolute -top-4 -left-2 text-orange-500 animate-bounce" style={{animationDelay: '1.5s'}}>
              💡
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Progress Indicators */}
      <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 flex space-x-2">
        <div className="w-2 h-2 bg-purple-400 rounded-full animate-pulse"></div>
        <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse" style={{animationDelay: '0.3s'}}></div>
        <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" style={{animationDelay: '0.6s'}}></div>
        <div className="w-2 h-2 bg-orange-400 rounded-full animate-pulse" style={{animationDelay: '0.9s'}}></div>
      </div>

      {/* Motivational Quote Overlay */}
      {!isAnalyzing && (
        <div className="absolute top-4 right-4 bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-lg px-3 py-2 shadow-lg">
          <div className="text-xs font-semibold text-purple-700 dark:text-purple-300">
            💪 "Bridge the gap, reach your goal!"
          </div>
        </div>
      )}
    </div>
  );
} 