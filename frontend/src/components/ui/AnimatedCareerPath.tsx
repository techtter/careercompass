"use client";

import React, { useEffect, useState } from 'react';
import { TypeAnimation } from 'react-type-animation';

interface AnimatedCareerPathProps {
  content: string;
}

export default function AnimatedCareerPath({ content }: AnimatedCareerPathProps) {
  const [sections, setSections] = useState<string[][]>([]);
  const [isReady, setIsReady] = useState(false);
  const [showContent, setShowContent] = useState(false);

  // Function to clean markdown symbols from text
  const cleanMarkdownText = (text: string): string => {
    return text
      .replace(/\*\*/g, '') // Remove **
      .replace(/^[-*]\s*/gm, '') // Remove leading - or * with space
      .trim();
  };

  useEffect(() => {
    // Parse the markdown content into sections
    const lines = content.split('\n');
    const parsedSections: string[][] = [];
    let currentSection: string[] = [];
    let isSkillSection = false;

    lines.forEach((line) => {
      const cleanedLine = cleanMarkdownText(line);
      
      if (cleanedLine === '') return;

      if (cleanedLine.includes('Career Path Recommendation')) {
        if (currentSection.length > 0) {
          parsedSections.push(currentSection);
          currentSection = [];
        }
        currentSection.push(cleanedLine);
      } else if (cleanedLine.includes('Short-term goals') || 
                 cleanedLine.includes('Mid-term goals') || 
                 cleanedLine.includes('Long-term goals') || 
                 cleanedLine.includes('Skill Development')) {
        if (currentSection.length > 0) {
          parsedSections.push(currentSection);
          currentSection = [];
        }
        isSkillSection = cleanedLine.includes('Skill Development');
        currentSection.push(cleanedLine);
      } else if (cleanedLine !== '') {
        currentSection.push(cleanedLine);
      }
    });

    if (currentSection.length > 0) {
      parsedSections.push(currentSection);
    }

    setSections(parsedSections);
    setIsReady(true);

    // Add delay before showing content
    const timer = setTimeout(() => {
      setShowContent(true);
    }, 2000); // Show content after 2 seconds

    return () => clearTimeout(timer);
  }, [content]);

  const calculateLineDelay = (sectionIndex: number, lineIndex: number): number => {
    let totalDelay = 0;
    
    // Add up delays for all previous sections
    for (let i = 0; i < sectionIndex; i++) {
      totalDelay += (sections[i]?.length || 0) * 1000; // 1 second per line in previous sections
    }
    
    // Add delay for current section's previous lines
    totalDelay += lineIndex * 1000; // 1 second per line in current section
    
    return totalDelay;
  };

  if (!isReady) return null;

  return (
    <div className="space-y-4 p-4">
      {/* Main content with sequential animation */}
      <div className="space-y-6">
        {sections.map((section, sectionIndex) => (
          <div key={sectionIndex} className="space-y-2">
            {section.map((line, lineIndex) => {
              const isTitle = lineIndex === 0;
              const isMainTitle = line.includes('Career Path Recommendation');
              const delay = calculateLineDelay(sectionIndex, lineIndex);

              return (
                <div key={`${sectionIndex}-${lineIndex}`}>
                  <TypeAnimation
                    sequence={[
                      delay,
                      line,
                    ]}
                    wrapper={isMainTitle ? "h1" : isTitle ? "h2" : "p"}
                    speed={30}
                    cursor={false}
                    className={`
                      ${isMainTitle ? 'text-2xl text-blue-600 border-b pb-2 mb-4' : ''}
                      ${isTitle && !isMainTitle ? 'text-xl font-bold mt-6' : ''}
                      ${!isTitle ? 'pl-4 before:content-["•"] before:mr-2 before:text-blue-500' : ''}
                    `}
                  />
                  {/* Enhanced AI Animation Message */}
                  {isMainTitle && (
                    <div className="relative flex items-center justify-center p-8 my-6 bg-gradient-to-r from-blue-500/5 via-purple-500/5 to-blue-500/5 rounded-xl shadow-lg overflow-hidden">
                      {/* Neural Network Background Animation */}
                      <div className="absolute inset-0 w-full h-full">
                        <div className="absolute w-2 h-2 bg-blue-500 rounded-full animate-ping" style={{ top: '20%', left: '20%' }}></div>
                        <div className="absolute w-2 h-2 bg-purple-500 rounded-full animate-ping" style={{ top: '60%', left: '40%', animationDelay: '0.5s' }}></div>
                        <div className="absolute w-2 h-2 bg-indigo-500 rounded-full animate-ping" style={{ top: '30%', left: '70%', animationDelay: '1s' }}></div>
                        <div className="absolute w-2 h-2 bg-blue-400 rounded-full animate-ping" style={{ top: '70%', left: '80%', animationDelay: '1.5s' }}></div>
                        {/* Neural Network Lines */}
                        <div className="absolute h-px bg-gradient-to-r from-blue-500/50 to-purple-500/50 w-full top-1/4 animate-pulse"></div>
                        <div className="absolute h-px bg-gradient-to-r from-purple-500/50 to-blue-500/50 w-full top-2/4 animate-pulse delay-300"></div>
                        <div className="absolute h-px bg-gradient-to-r from-blue-500/50 to-purple-500/50 w-full top-3/4 animate-pulse delay-700"></div>
                      </div>

                      {/* Central AI Brain Animation */}
                      <div className="relative z-10 flex items-center space-x-6">
                        <div className="relative">
                          {/* Outer Ring */}
                          <div className="absolute inset-0 border-4 border-blue-500/30 rounded-full animate-spin-slow"></div>
                          {/* Middle Ring */}
                          <div className="absolute inset-2 border-4 border-purple-500/30 rounded-full animate-reverse-spin"></div>
                          {/* Inner Circle with Gradient */}
                          <div className="relative w-16 h-16 rounded-full bg-gradient-to-br from-blue-600 via-purple-600 to-blue-600 animate-pulse p-1">
                            <div className="absolute inset-1 bg-white/10 rounded-full backdrop-blur-sm"></div>
                            {/* Synapses */}
                            <div className="absolute inset-0 flex items-center justify-center">
                              <div className="w-1 h-1 bg-white rounded-full animate-ping"></div>
                            </div>
                          </div>
                        </div>

                        {/* AI Text Animation */}
                        <div className="flex flex-col">
                          <TypeAnimation
                            sequence={[
                              'AI is analyzing your profile...',
                              1500,
                              'Generating personalized career path...',
                              1500,
                              'Mapping your professional journey...',
                              1500,
                            ]}
                            wrapper="p"
                            speed={50}
                            className="text-lg font-semibold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 via-purple-600 to-blue-600"
                            repeat={Infinity}
                          />
                          <p className="text-sm text-blue-600/70 animate-pulse">Processing data and creating recommendations</p>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        ))}
      </div>
    </div>
  );
} 