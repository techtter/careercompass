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
                        {/* Neural Network Nodes */}
                        {Array.from({ length: 12 }).map((_, i) => (
                          <div
                            key={i}
                            className="absolute w-2 h-2 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full animate-ping"
                            style={{
                              top: `${Math.random() * 100}%`,
                              left: `${Math.random() * 100}%`,
                              animationDelay: `${i * 0.2}s`,
                              animationDuration: '3s'
                            }}
                          />
                        ))}
                        {/* Neural Network Lines */}
                        {Array.from({ length: 6 }).map((_, i) => (
                          <div
                            key={`line-${i}`}
                            className="absolute h-px bg-gradient-to-r from-blue-500/30 via-purple-500/30 to-blue-500/30 w-full animate-pulse"
                            style={{
                              top: `${(i + 1) * 15}%`,
                              transform: `rotate(${i * 30}deg)`,
                              animationDelay: `${i * 0.3}s`
                            }}
                          />
                        ))}
                      </div>

                      {/* Central AI Brain Animation */}
                      <div className="relative z-10 flex items-center space-x-6">
                        <div className="relative">
                          {/* Multiple Rotating Rings */}
                          {Array.from({ length: 3 }).map((_, i) => (
                            <div
                              key={`ring-${i}`}
                              className={`absolute inset-${i} border-4 rounded-full ${i % 2 === 0 ? 'animate-spin-slow' : 'animate-reverse-spin'}`}
                              style={{
                                borderColor: `rgba(${i === 0 ? '59, 130, 246' : i === 1 ? '147, 51, 234' : '79, 70, 229'}, 0.3)`,
                                animationDuration: `${4 + i}s`
                              }}
                            />
                          ))}
                          {/* Brain Core */}
                          <div className="relative w-20 h-20 rounded-full bg-gradient-to-br from-blue-600 via-purple-600 to-blue-600 animate-pulse p-1">
                            <div className="absolute inset-1 bg-white/10 rounded-full backdrop-blur-sm">
                              {/* Synapses */}
                              {Array.from({ length: 4 }).map((_, i) => (
                                <div
                                  key={`synapse-${i}`}
                                  className="absolute w-1 h-1 bg-white rounded-full animate-ping"
                                  style={{
                                    top: `${25 + (i * 15)}%`,
                                    left: `${25 + (i * 15)}%`,
                                    animationDelay: `${i * 0.3}s`
                                  }}
                                />
                              ))}
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
                              'Creating tailored recommendations...',
                              1500,
                              'Optimizing career trajectory...',
                              1500
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