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
    <div className="relative w-full h-20 bg-gradient-to-r from-purple-50 via-blue-50 to-indigo-50 dark:from-purple-900/10 dark:via-blue-900/10 dark:to-indigo-900/10 rounded-lg overflow-hidden border border-purple-200/50 dark:border-purple-700/30">
      {/* Enhanced Background Pattern with Animations */}
      <div className="absolute inset-0 opacity-5 dark:opacity-10">
        <svg className="w-full h-full" viewBox="0 0 200 80">
          <defs>
            <linearGradient id="bgGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="currentColor" className="text-purple-500 dark:text-purple-400" />
              <stop offset="50%" stopColor="currentColor" className="text-blue-500 dark:text-blue-400" />
              <stop offset="100%" stopColor="currentColor" className="text-cyan-500 dark:text-cyan-400" />
            </linearGradient>
            <filter id="glow">
              <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
              <feMerge> 
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
          </defs>
          
          {/* Animated Neural Network Lines */}
          <g stroke="url(#bgGradient)" strokeWidth="0.8" fill="none" opacity="0.4" filter="url(#glow)">
            <line x1="20" y1="20" x2="60" y2="30" className="animate-pulse" />
            <line x1="20" y1="40" x2="60" y2="30" className="animate-pulse" style={{animationDelay: '0.5s'}} />
            <line x1="60" y1="30" x2="100" y2="25" className="animate-pulse" style={{animationDelay: '1s'}} />
            <line x1="100" y1="25" x2="140" y2="40" className="animate-pulse" style={{animationDelay: '1.5s'}} />
            <line x1="140" y1="40" x2="180" y2="35" className="animate-pulse" style={{animationDelay: '2s'}} />
          </g>
          
          {/* Floating Neural Nodes */}
          <g className="fill-purple-500 dark:fill-purple-400" opacity="0.6">
            <circle cx="20" cy="20" r="1.5" className="animate-pulse" filter="url(#glow)" />
            <circle cx="20" cy="40" r="1.5" className="animate-pulse" style={{animationDelay: '0.3s'}} filter="url(#glow)" />
            <circle cx="60" cy="30" r="2" className="animate-pulse" style={{animationDelay: '0.6s'}} filter="url(#glow)" />
            <circle cx="100" cy="25" r="2" className="animate-pulse" style={{animationDelay: '0.9s'}} filter="url(#glow)" />
            <circle cx="140" cy="40" r="2.5" className="animate-pulse" style={{animationDelay: '1.2s'}} filter="url(#glow)" />
            <circle cx="180" cy="35" r="2" className="animate-pulse" style={{animationDelay: '1.5s'}} filter="url(#glow)" />
          </g>
        </svg>
      </div>

      {/* Floating Particles Animation */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-2 left-10 w-1 h-1 bg-purple-400 dark:bg-purple-300 rounded-full animate-ping opacity-40"></div>
        <div className="absolute top-4 right-20 w-1 h-1 bg-blue-400 dark:bg-blue-300 rounded-full animate-ping opacity-40" style={{animationDelay: '1s'}}></div>
        <div className="absolute bottom-3 left-1/3 w-1 h-1 bg-indigo-400 dark:bg-indigo-300 rounded-full animate-ping opacity-40" style={{animationDelay: '2s'}}></div>
        <div className="absolute bottom-2 right-10 w-1 h-1 bg-cyan-400 dark:bg-cyan-300 rounded-full animate-ping opacity-40" style={{animationDelay: '0.5s'}}></div>
      </div>

      {/* Main Content - Horizontal Layout */}
      <div className="relative z-10 flex items-center justify-between h-full px-6">
        {/* Left: Enhanced AI Brain with Animations */}
        <div className="flex items-center space-x-3">
          <div className="relative">
            {/* Outer Glow Ring */}
            <div className="absolute inset-0 w-12 h-12 -m-1 bg-gradient-to-br from-purple-400/30 to-blue-500/30 dark:from-purple-300/30 dark:to-blue-400/30 rounded-full animate-pulse blur-sm"></div>
            
            {/* Main AI Brain */}
            <div className="relative w-10 h-10 bg-gradient-to-br from-purple-500 to-blue-600 dark:from-purple-400 dark:to-blue-500 rounded-full flex items-center justify-center shadow-lg transform transition-transform duration-300 hover:scale-110">
              <div className="text-white dark:text-gray-100 font-bold text-xs animate-pulse">AI</div>
              
              {/* Inner Sparkle */}
              <div className="absolute top-1 right-1 w-1 h-1 bg-white rounded-full animate-ping opacity-80"></div>
            </div>
            
            {/* Rotating Analysis Ring */}
            {isAnalyzing && (
              <>
                <div className="absolute inset-0 w-10 h-10 border-2 border-purple-300 dark:border-purple-600 rounded-full animate-spin opacity-60" style={{animationDuration: '2s'}}></div>
                <div className="absolute inset-0 w-10 h-10 border-2 border-blue-300 dark:border-blue-600 rounded-full animate-spin opacity-40" style={{animationDuration: '3s', animationDirection: 'reverse'}}></div>
              </>
            )}
          </div>
          
          <div className="flex flex-col">
            <div className="text-sm font-semibold text-purple-700 dark:text-purple-300 flex items-center space-x-1">
              <span className={isAnalyzing ? "animate-spin" : "animate-bounce"}>{isAnalyzing ? "🔍" : "🎯"}</span>
              <span>{isAnalyzing ? "Analyzing..." : "AI Ready"}</span>
            </div>
            <div className="text-xs text-purple-600 dark:text-purple-400">
              {isAnalyzing ? "Processing skills" : "Skill gap analysis"}
            </div>
          </div>
        </div>

        {/* Center: Enhanced Processing Indicator */}
        <div className="flex items-center space-x-2">
          {isAnalyzing ? (
            <div className="flex items-center space-x-2">
              {/* Bouncing Dots */}
              <div className="w-2 h-2 bg-purple-400 dark:bg-purple-300 rounded-full animate-bounce shadow-sm"></div>
              <div className="w-2 h-2 bg-blue-400 dark:bg-blue-300 rounded-full animate-bounce shadow-sm" style={{animationDelay: '0.2s'}}></div>
              <div className="w-2 h-2 bg-indigo-400 dark:bg-indigo-300 rounded-full animate-bounce shadow-sm" style={{animationDelay: '0.4s'}}></div>
              
              {/* Pulsing Analysis Icon */}
              <div className="ml-2 text-purple-500 dark:text-purple-400 animate-pulse">
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
          ) : (
            <div className="flex items-center space-x-2 text-xs text-gray-500 dark:text-gray-400">
              <span className="animate-pulse text-yellow-500">⚡</span>
              <span className="animate-pulse">Ready for analysis</span>
            </div>
          )}
        </div>

        {/* Right: Enhanced Success Indicator with Animations */}
        <div className="flex items-center space-x-2">
          <div className="relative">
            {/* Success Glow */}
            <div className="absolute inset-0 w-10 h-10 -m-1 bg-gradient-to-br from-green-400/30 to-emerald-500/30 dark:from-green-300/30 dark:to-emerald-400/30 rounded-full animate-pulse blur-sm"></div>
            
            {/* Main Success Icon */}
            <div className="relative w-8 h-8 bg-gradient-to-br from-green-500 to-emerald-600 dark:from-green-400 dark:to-emerald-500 rounded-full flex items-center justify-center shadow-lg transform transition-transform duration-300 hover:scale-110">
              <svg className="w-4 h-4 text-white dark:text-gray-100 animate-pulse" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              
              {/* Success Sparkle */}
              <div className="absolute -top-1 -right-1 w-2 h-2 bg-yellow-300 rounded-full animate-ping opacity-70"></div>
            </div>
          </div>
          
          <div className="text-xs text-green-700 dark:text-green-300 font-medium flex items-center space-x-1">
            <span className="animate-bounce">🚀</span>
            <span>Career Growth</span>
          </div>
        </div>
      </div>

      {/* Enhanced Bottom Progress Bar */}
      {isAnalyzing && (
        <div className="absolute bottom-0 left-0 w-full h-1 bg-gray-200 dark:bg-gray-700 overflow-hidden">
          <div className="h-full bg-gradient-to-r from-purple-500 via-blue-500 to-indigo-500 dark:from-purple-400 dark:via-blue-400 dark:to-indigo-400 animate-pulse relative">
            {/* Moving Shimmer Effect */}
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-pulse" style={{animationDuration: '1.5s'}}></div>
          </div>
        </div>
      )}

      {/* Floating Success Particles (when not analyzing) */}
      {!isAnalyzing && (
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-1 right-8 text-yellow-400 animate-bounce opacity-60" style={{animationDelay: '0s', fontSize: '8px'}}>✨</div>
          <div className="absolute bottom-1 left-12 text-green-400 animate-bounce opacity-60" style={{animationDelay: '1s', fontSize: '8px'}}>⭐</div>
          <div className="absolute top-2 left-1/2 text-blue-400 animate-bounce opacity-60" style={{animationDelay: '2s', fontSize: '8px'}}>💫</div>
        </div>
      )}
    </div>
  );
} 