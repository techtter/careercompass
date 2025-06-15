"use client";

import React from 'react';
import { TypeAnimation } from 'react-type-animation';

export default function AIBackgroundAnimation() {
  return (
    <div className="relative flex items-center justify-between p-8 my-6 bg-gradient-to-r from-blue-500/5 via-purple-500/5 to-blue-500/5 rounded-xl shadow-lg overflow-hidden w-full">
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

      {/* Left Side - AI Brain Animation */}
      <div className="relative z-10 flex items-center">
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
          {/* Brain Core with AI Text */}
          <div className="relative w-20 h-20 rounded-full bg-gradient-to-br from-blue-600 via-purple-600 to-blue-600 animate-pulse p-1">
            <div className="absolute inset-1 bg-white/10 rounded-full backdrop-blur-sm flex items-center justify-center">
              {/* AI Text Overlay */}
              <span className="text-white font-bold text-sm animate-pulse">AI</span>
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
      </div>

      {/* Center - AI Text Animation */}
      <div className="relative z-10 flex flex-col items-center flex-1 mx-8">
        <TypeAnimation
          sequence={[
            'AI-Powered Career Guidance',
            1500,
            'Personalized Job Recommendations',
            1500,
            'Smart Resume Analysis',
            1500,
            'Career Path Planning',
            1500,
            'Skill Gap Analysis',
            1500
          ]}
          wrapper="p"
          speed={50}
          className="text-lg font-semibold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 via-purple-600 to-blue-600 text-center"
          repeat={Infinity}
        />
        <p className="text-sm text-blue-600/70 animate-pulse text-center">Empowering your career journey with AI</p>
      </div>

      {/* Right Side - Additional AI Elements */}
      <div className="relative z-10 flex items-center">
        <div className="flex flex-col space-y-2">
          {/* AI Feature Indicators */}
          {['Smart Analysis', 'Career Planning', 'Job Matching'].map((feature, i) => (
            <div key={feature} className="flex items-center space-x-2 animate-fadeIn" style={{animationDelay: `${i * 0.3}s`}}>
              <div className="w-2 h-2 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full animate-ping" style={{animationDelay: `${i * 0.2}s`}}></div>
              <span className="text-xs text-blue-600/80 font-medium">{feature}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
} 