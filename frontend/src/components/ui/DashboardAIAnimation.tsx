"use client";

import React from 'react';

export default function DashboardAIAnimation() {
  return (
    <div className="relative w-24 h-24 flex items-center justify-center">
      {/* Core Brain */}
      <div className="absolute w-12 h-12 bg-gradient-to-r from-blue-500/30 to-purple-500/30 rounded-full animate-pulse-slow" />
      
      {/* Rotating Rings */}
      <div className="absolute w-16 h-16 border-2 border-blue-500/20 rounded-full animate-spin-slow" />
      <div className="absolute w-20 h-20 border-2 border-purple-500/20 rounded-full animate-reverse-spin" />
      
      {/* Neural Network Nodes */}
      {Array.from({ length: 6 }).map((_, i) => (
        <div
          key={i}
          className="absolute w-1.5 h-1.5 bg-gradient-to-r from-blue-500/50 to-purple-500/50 rounded-full animate-pulse"
          style={{
            top: `${Math.random() * 100}%`,
            left: `${Math.random() * 100}%`,
            animationDelay: `${i * 0.2}s`
          }}
        />
      ))}
      
      {/* Synapses */}
      <div className="absolute inset-0">
        {Array.from({ length: 3 }).map((_, i) => (
          <div
            key={i}
            className="absolute w-full h-full border border-purple-500/10 rounded-full"
            style={{
              transform: `rotate(${i * 60}deg)`,
              animation: `spin ${3 + i}s linear infinite`
            }}
          />
        ))}
      </div>
    </div>
  );
} 