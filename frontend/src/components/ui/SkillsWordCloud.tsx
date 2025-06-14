"use client";

import React, { useEffect, useState } from 'react';

interface SkillsWordCloudProps {
  skills: string[];
  className?: string;
}

interface SkillItem {
  text: string;
  size: number;
  color: string;
  x: number;
  y: number;
  rotation: number;
  animationDelay: number;
}

const SkillsWordCloud: React.FC<SkillsWordCloudProps> = ({ skills, className = "" }) => {
  const [skillItems, setSkillItems] = useState<SkillItem[]>([]);
  const [isVisible, setIsVisible] = useState(false);

  // Color palette for skills
  const colors = [
    'text-blue-600 dark:text-blue-400',
    'text-green-600 dark:text-green-400', 
    'text-purple-600 dark:text-purple-400',
    'text-red-600 dark:text-red-400',
    'text-yellow-600 dark:text-yellow-400',
    'text-indigo-600 dark:text-indigo-400',
    'text-pink-600 dark:text-pink-400',
    'text-teal-600 dark:text-teal-400',
    'text-orange-600 dark:text-orange-400',
    'text-cyan-600 dark:text-cyan-400'
  ];

  // Background colors for skill bubbles
  const bgColors = [
    'bg-blue-100 dark:bg-blue-900/30 border-blue-300 dark:border-blue-600',
    'bg-green-100 dark:bg-green-900/30 border-green-300 dark:border-green-600',
    'bg-purple-100 dark:bg-purple-900/30 border-purple-300 dark:border-purple-600', 
    'bg-red-100 dark:bg-red-900/30 border-red-300 dark:border-red-600',
    'bg-yellow-100 dark:bg-yellow-900/30 border-yellow-300 dark:border-yellow-600',
    'bg-indigo-100 dark:bg-indigo-900/30 border-indigo-300 dark:border-indigo-600',
    'bg-pink-100 dark:bg-pink-900/30 border-pink-300 dark:border-pink-600',
    'bg-teal-100 dark:bg-teal-900/30 border-teal-300 dark:border-teal-600',
    'bg-orange-100 dark:bg-orange-900/30 border-orange-300 dark:border-orange-600',
    'bg-cyan-100 dark:bg-cyan-900/30 border-cyan-300 dark:border-cyan-600'
  ];

  useEffect(() => {
    if (skills.length === 0) return;

    // Clean and split skills that might still contain delimiters
    const cleanedSkills: string[] = [];
    skills.forEach(skill => {
      if (skill.includes(',') || skill.includes('/') || skill.includes('|')) {
        // Split by delimiters and add individual skills
        const splitSkills = skill.split(/[,\/\|]/).map(s => s.trim()).filter(s => s.length > 0);
        cleanedSkills.push(...splitSkills);
      } else {
        cleanedSkills.push(skill.trim());
      }
    });

    // Remove duplicates and empty skills
    const uniqueSkills = [...new Set(cleanedSkills)].filter(skill => skill.length > 0);

    // Generate random positions and properties for each skill
    const items: SkillItem[] = uniqueSkills.map((skill, index) => {
      // Size based on skill length and importance (shorter skills get bigger)
      const baseSize = Math.max(14, 24 - skill.length * 0.8);
      const size = baseSize + Math.random() * 6;
      
      // Ensure skills don't overlap too much by using a grid-like approach
      const gridCols = Math.ceil(Math.sqrt(uniqueSkills.length));
      const gridRows = Math.ceil(uniqueSkills.length / gridCols);
      const gridX = (index % gridCols) / gridCols;
      const gridY = Math.floor(index / gridCols) / gridRows;
      
      // Add some randomness to the grid positions
      const x = (gridX * 70 + 15) + (Math.random() - 0.5) * 20;
      const y = (gridY * 70 + 15) + (Math.random() - 0.5) * 20;
      
      return {
        text: skill,
        size,
        color: colors[index % colors.length],
        x: Math.max(10, Math.min(90, x)), // Keep within bounds
        y: Math.max(10, Math.min(90, y)), // Keep within bounds
        rotation: (Math.random() - 0.5) * 20, // -10 to 10 degrees
        animationDelay: index * 0.15 // Staggered animation
      };
    });

    setSkillItems(items);
    
    // Trigger animation after component mounts
    setTimeout(() => setIsVisible(true), 200);
  }, [skills]);

  if (skills.length === 0) {
    return (
      <div className={`text-center py-8 ${className}`}>
        <p className="text-gray-500 dark:text-gray-400 italic">No skills found</p>
      </div>
    );
  }

  return (
    <div className={`relative w-full h-96 overflow-hidden rounded-lg bg-gradient-to-br from-gray-50 to-blue-50 dark:from-gray-800 dark:to-blue-900/20 border border-gray-200 dark:border-gray-700 ${className}`}>
      {/* Animated background particles */}
      <div className="absolute inset-0">
        {[...Array(30)].map((_, i) => (
          <div
            key={i}
            className={`absolute rounded-full opacity-20 animate-pulse ${
              i % 3 === 0 ? 'w-2 h-2 bg-blue-400 dark:bg-blue-500' : 
              i % 3 === 1 ? 'w-1 h-1 bg-purple-400 dark:bg-purple-500' : 
              'w-1.5 h-1.5 bg-green-400 dark:bg-green-500'
            }`}
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 4}s`,
              animationDuration: `${3 + Math.random() * 3}s`
            }}
          />
        ))}
      </div>

      {/* Floating geometric shapes */}
      <div className="absolute inset-0 overflow-hidden">
        {[...Array(8)].map((_, i) => (
          <div
            key={i}
            className={`absolute opacity-10 animate-float ${
              i % 4 === 0 ? 'w-8 h-8 bg-blue-300 dark:bg-blue-600 rounded-full' :
              i % 4 === 1 ? 'w-6 h-6 bg-purple-300 dark:bg-purple-600 rotate-45' :
              i % 4 === 2 ? 'w-10 h-10 bg-green-300 dark:bg-green-600 rounded-full' :
              'w-4 h-4 bg-yellow-300 dark:bg-yellow-600 rotate-12'
            }`}
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${i * 0.5}s`,
              animationDuration: `${4 + Math.random() * 2}s`
            }}
          />
        ))}
      </div>

      {/* Skills as floating elements */}
      {skillItems.map((item, index) => (
        <div
          key={index}
          className={`absolute transform transition-all duration-1000 ease-out ${
            isVisible ? 'opacity-100 scale-100' : 'opacity-0 scale-50'
          }`}
          style={{
            left: `${item.x}%`,
            top: `${item.y}%`,
            transform: `translate(-50%, -50%) rotate(${item.rotation}deg)`,
            transitionDelay: `${item.animationDelay}s`,
            fontSize: `${item.size}px`
          }}
        >
                     <div
             className={`
               skill-item px-4 py-2 rounded-full font-medium border-2 shadow-lg
               hover:shadow-xl hover:scale-125 transition-all duration-500
               cursor-pointer select-none backdrop-blur-sm
               ${bgColors[index % bgColors.length]}
               ${item.color}
               animate-bounce hover:animate-pulse
               relative overflow-hidden
             `}
             style={{
               animationDelay: `${item.animationDelay}s`,
               animationDuration: '1.5s',
               animationIterationCount: '1',
               fontSize: `${Math.max(12, item.size * 0.8)}px`
             }}
             onMouseEnter={(e) => {
               e.currentTarget.style.transform = 'scale(1.25) rotate(0deg)';
               e.currentTarget.style.zIndex = '20';
               e.currentTarget.style.boxShadow = '0 20px 40px rgba(0,0,0,0.2)';
               // Add a subtle glow effect
               e.currentTarget.style.filter = 'brightness(1.1)';
             }}
             onMouseLeave={(e) => {
               e.currentTarget.style.transform = 'scale(1) rotate(' + item.rotation + 'deg)';
               e.currentTarget.style.zIndex = '1';
               e.currentTarget.style.boxShadow = '';
               e.currentTarget.style.filter = '';
             }}
             onClick={() => {
               // Add a click animation
               const element = document.createElement('div');
               element.className = 'absolute inset-0 bg-white opacity-50 rounded-full animate-ping';
               element.style.pointerEvents = 'none';
               (event?.currentTarget as HTMLElement)?.appendChild(element);
               setTimeout(() => element.remove(), 600);
             }}
           >
             {/* Skill text */}
             <span className="relative z-10">{item.text}</span>
             
             {/* Animated background gradient */}
             <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-0 hover:opacity-20 transition-opacity duration-300 transform -skew-x-12 -translate-x-full hover:translate-x-full"></div>
           </div>
        </div>
      ))}

      {/* Enhanced animations */}
      <style jsx>{`
        @keyframes float {
          0%, 100% { 
            transform: translateY(0px) rotate(0deg) scale(1); 
          }
          25% { 
            transform: translateY(-8px) rotate(1deg) scale(1.02); 
          }
          50% { 
            transform: translateY(-15px) rotate(2deg) scale(1.05); 
          }
          75% { 
            transform: translateY(-8px) rotate(1deg) scale(1.02); 
          }
        }
        
        @keyframes shimmer {
          0% { background-position: -200% 0; }
          100% { background-position: 200% 0; }
        }
        
        @keyframes glow {
          0%, 100% { box-shadow: 0 0 5px rgba(59, 130, 246, 0.3); }
          50% { box-shadow: 0 0 20px rgba(59, 130, 246, 0.6); }
        }
        
        .animate-float {
          animation: float 4s ease-in-out infinite;
        }
        
        .animate-float:nth-child(2n) {
          animation-delay: 0.8s;
          animation-duration: 5s;
        }
        
        .animate-float:nth-child(3n) {
          animation-delay: 1.6s;
          animation-duration: 4.5s;
        }
        
        .animate-float:nth-child(4n) {
          animation-delay: 2.4s;
          animation-duration: 5.5s;
        }
        
        .skill-item:hover {
          animation: glow 1s ease-in-out infinite alternate;
        }
      `}</style>

      {/* Skill count indicator */}
      <div className="absolute top-4 right-4 bg-white bg-opacity-80 backdrop-blur-sm rounded-full px-3 py-1 text-sm font-medium text-gray-700 border border-gray-300">
        {skillItems.length} Skills
      </div>

      {/* Interactive hint */}
      <div className="absolute bottom-4 left-4 bg-white bg-opacity-80 backdrop-blur-sm rounded-lg px-3 py-2 text-xs text-gray-600 border border-gray-300">
        💡 Hover over skills to interact
      </div>
    </div>
  );
};

export default SkillsWordCloud; 