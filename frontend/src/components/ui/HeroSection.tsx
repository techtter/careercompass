"use client";

import React from 'react';
import Link from "next/link";
import { Button } from "@/components/ui/Button";
import AIAnimationWrapper from './AIAnimationWrapper';

export default function HeroSection() {
  return (
    <section className="bg-gray-50 dark:bg-gray-800 pt-20 pb-2">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        {/* Enhanced Badge */}
        <div className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-blue-500 via-purple-500 to-indigo-500 border border-blue-300 dark:border-purple-400 rounded-full text-sm font-semibold text-white mb-8 shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300 animate-pulse">
          <span className="mr-2 text-lg animate-bounce">🚀</span>
          <span className="bg-white/20 px-2 py-1 rounded-md mr-2 text-xs font-bold">NEW</span>
          AI-Powered Career Planning
        </div>

        {/* Main Heading */}
        <h1 className="text-5xl md:text-6xl font-bold text-gray-900 dark:text-white mb-6">
          Navigate Your Career with{" "}
          <span className="bg-clip-text text-transparent bg-gradient-to-r from-blue-600 via-purple-600 to-blue-600">
            AI Guidance
          </span>
        </h1>

        {/* Subtitle */}
        <p className="text-xl text-gray-600 dark:text-gray-300 mb-10 max-w-3xl mx-auto leading-relaxed">
          Get personalized career paths, skill recommendations, and job matching powered by advanced AI. 
          Your professional growth journey starts here.
        </p>

        {/* AI Animation - Full Width */}
        <div className="w-full max-w-6xl mx-auto">
          <AIAnimationWrapper />
        </div>

        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center mb-2">
          <Link href="/signup">
            <Button size="lg" className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-lg font-semibold transition-all duration-200 transform hover:scale-105">
              Start Your Journey
            </Button>
          </Link>
        </div>
      </div>
    </section>
  );
} 