"use client";

import React, { useMemo } from 'react';

interface SkillsWordCloudProps {
  skills: string[];
  className?: string;
}

const SkillsWordCloud: React.FC<SkillsWordCloudProps> = ({ skills, className = "" }) => {
  // Process and clean skills
  const processedSkills = useMemo(() => {
    if (skills.length === 0) return [];

    // Clean and split skills that might contain delimiters
    const cleanedSkills: string[] = [];
    skills.forEach(skill => {
      if (skill.includes(',') || skill.includes('/') || skill.includes('|')) {
        const splitSkills = skill.split(/[,\/\|]/).map(s => s.trim()).filter(s => s.length > 0);
        cleanedSkills.push(...splitSkills);
      } else {
        cleanedSkills.push(skill.trim());
      }
    });

    // Remove duplicates and empty skills
    return [...new Set(cleanedSkills)].filter(skill => skill.length > 0);
  }, [skills]);

  // Color themes for skill categories
  const skillStyles = [
    'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 border-blue-200 dark:border-blue-700',
    'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200 border-green-200 dark:border-green-700',
    'bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-200 border-purple-200 dark:border-purple-700',
    'bg-orange-100 dark:bg-orange-900/30 text-orange-800 dark:text-orange-200 border-orange-200 dark:border-orange-700',
    'bg-teal-100 dark:bg-teal-900/30 text-teal-800 dark:text-teal-200 border-teal-200 dark:border-teal-700',
    'bg-indigo-100 dark:bg-indigo-900/30 text-indigo-800 dark:text-indigo-200 border-indigo-200 dark:border-indigo-700',
    'bg-pink-100 dark:bg-pink-900/30 text-pink-800 dark:text-pink-200 border-pink-200 dark:border-pink-700',
    'bg-cyan-100 dark:bg-cyan-900/30 text-cyan-800 dark:text-cyan-200 border-cyan-200 dark:border-cyan-700'
  ];

  if (processedSkills.length === 0) {
    return (
      <div className={`text-center py-8 ${className}`}>
        <p className="text-gray-500 dark:text-gray-400 italic">No skills found</p>
      </div>
    );
  }

      return (
      <div className={`w-full ${className}`}>

      {/* Responsive skill grid */}
      <div className="flex flex-wrap gap-2">
        {processedSkills.map((skill, index) => (
          <div
            key={`${skill}-${index}`}
            className={`
              px-3 py-2 rounded-lg border text-sm font-medium
              hover:shadow-md transition-all duration-200 hover:scale-105
              cursor-default select-none
              ${skillStyles[index % skillStyles.length]}
            `}
            title={skill} // Tooltip for longer skill names
          >
            {skill}
          </div>
        ))}
      </div>

      {/* Simple stats footer */}
      <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-center space-x-6 text-sm text-gray-600 dark:text-gray-400">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
            <span>Technical</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            <span>Frameworks</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
            <span>Tools</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SkillsWordCloud; 