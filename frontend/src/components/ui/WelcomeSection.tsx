"use client";

import React from 'react';
import dynamic from 'next/dynamic';
import { useUser, SignOutButton } from '@clerk/nextjs';
import Image from 'next/image';
import { Button } from '@/components/ui/Button';
import { ThemeToggle } from '@/components/ui/ThemeToggle';

// Dynamically import the AI animation with no SSR
const DashboardAIAnimation = dynamic(() => import('./DashboardAIAnimation'), {
  ssr: false,
  loading: () => <div className="w-24 h-24" /> // Placeholder while loading
});

interface WelcomeSectionProps {
  firstName?: string;
}

export default function WelcomeSection({ firstName }: WelcomeSectionProps) {
  const { user } = useUser();
  const profileImageUrl = user?.imageUrl;

  return (
    <div className="relative mb-8 p-8 bg-gradient-to-br from-blue-50 via-purple-50 to-indigo-50 dark:from-blue-900/20 dark:via-purple-900/20 dark:to-indigo-900/20 rounded-2xl shadow-lg border border-blue-100 dark:border-blue-800/30 overflow-hidden">
      {/* AI Background Pattern */}
      <div className="absolute inset-0 opacity-5 dark:opacity-10">
        <div className="absolute inset-0" 
          style={{
            backgroundImage: `radial-gradient(circle at 20px 20px, rgba(59, 130, 246, 0.3) 2px, transparent 0)`,
            backgroundSize: '40px 40px',
            animation: 'float 6s ease-in-out infinite',
          }}
        />
        {/* Floating AI particles */}
        {[...Array(8)].map((_, i) => (
          <div
            key={i}
            className="absolute w-2 h-2 bg-blue-400/30 rounded-full animate-pulse"
            style={{
              top: `${Math.random() * 100}%`,
              left: `${Math.random() * 100}%`,
              animationDelay: `${i * 0.5}s`,
              animationDuration: `${3 + Math.random() * 2}s`
            }}
          />
        ))}
      </div>

      {/* Top Right Controls */}
      <div className="absolute top-4 right-4 z-20 flex items-center space-x-3">
        <div className="shadow-lg hover:shadow-xl transition-shadow duration-300 rounded-full">
          <ThemeToggle />
        </div>
        <SignOutButton>
          <Button variant="outline" size="sm" className="p-3 rounded-full w-11 h-11 flex items-center justify-center hover:bg-white/80 dark:hover:bg-gray-800/80 backdrop-blur-sm border-white/50 dark:border-gray-700/50 shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-300" title="Sign Out">
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

      <div className="relative z-10 flex items-center justify-between">
        <div className="space-y-4 flex-1">
          <div className="space-y-2">
            <div className="flex items-center space-x-4">
              {profileImageUrl && (
                <div className="relative w-16 h-16 rounded-full overflow-hidden ring-4 ring-blue-200 dark:ring-blue-700/50 shadow-lg flex-shrink-0">
                  <Image
                    src={profileImageUrl}
                    alt="Profile"
                    fill
                    className="object-cover"
                  />
                </div>
              )}
              <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 dark:from-blue-400 dark:via-purple-400 dark:to-indigo-400 text-transparent bg-clip-text animate-fadeIn">
                Welcome{firstName ? `, ${firstName}` : ''}! 👋
              </h1>
            </div>
            <div className="flex items-center space-x-2 animate-fadeIn" style={{animationDelay: '0.2s'}}>
              <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-sm text-green-600 dark:text-green-400 font-medium">AI Career Assistant Active</span>
            </div>
          </div>
          
          <div className="space-y-3">
            <p className="text-xl text-gray-700 dark:text-gray-300 font-medium animate-fadeIn" style={{animationDelay: '0.4s'}}>
              🚀 Let&apos;s unlock your career potential with AI-powered insights
            </p>
            <p className="text-gray-600 dark:text-gray-400 leading-relaxed max-w-3xl animate-fadeIn" style={{animationDelay: '0.6s'}}>
              Our intelligent AI assistant is analyzing your profile to provide personalized career paths, identify skill gaps, and match you with perfect opportunities. Together, we&apos;ll accelerate your professional growth using cutting-edge technology.
            </p>
            
            {/* AI Features Highlight */}
            <div className="flex flex-wrap gap-3 mt-4 animate-fadeIn" style={{animationDelay: '0.8s'}}>
              <div className="flex items-center space-x-2 bg-blue-100 dark:bg-blue-900/30 px-3 py-1 rounded-full">
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-ping"></div>
                <span className="text-sm text-blue-700 dark:text-blue-300 font-medium">Smart Job Matching</span>
              </div>
              <div className="flex items-center space-x-2 bg-purple-100 dark:bg-purple-900/30 px-3 py-1 rounded-full">
                <div className="w-2 h-2 bg-purple-500 rounded-full animate-ping" style={{animationDelay: '0.2s'}}></div>
                <span className="text-sm text-purple-700 dark:text-purple-300 font-medium">Career Path Planning</span>
              </div>
              <div className="flex items-center space-x-2 bg-green-100 dark:bg-green-900/30 px-3 py-1 rounded-full">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-ping" style={{animationDelay: '0.4s'}}></div>
                <span className="text-sm text-green-700 dark:text-green-300 font-medium">Skill Analysis</span>
              </div>
              <div className="flex items-center space-x-2 bg-orange-100 dark:bg-orange-900/30 px-3 py-1 rounded-full">
                <div className="w-2 h-2 bg-orange-500 rounded-full animate-ping" style={{animationDelay: '0.6s'}}></div>
                <span className="text-sm text-orange-700 dark:text-orange-300 font-medium">Resume Optimization</span>
              </div>
            </div>
          </div>
        </div>
        
        {/* Enhanced AI Animation */}
        <div className="flex-shrink-0 transform hover:scale-105 transition-transform duration-300 relative -ml-8">
          <div className="absolute inset-0 bg-gradient-to-r from-blue-400/20 to-purple-400/20 rounded-full blur-xl animate-pulse"></div>
          <div className="relative">
            <DashboardAIAnimation />
            {/* AI Text Overlay */}
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-2xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 dark:from-blue-400 dark:via-purple-400 dark:to-indigo-400 text-transparent bg-clip-text animate-pulse">
                AI
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 