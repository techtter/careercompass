"use client";

import React, { createContext, useContext, useEffect, useState } from 'react';

type Theme = 'light' | 'dark';

interface ThemeContextType {
  theme: Theme;
  toggleTheme: () => void;
  mounted: boolean;
}

// Create a default context value to prevent undefined errors
const defaultContextValue: ThemeContextType = {
  theme: 'light',
  toggleTheme: () => {},
  mounted: false,
};

const ThemeContext = createContext<ThemeContextType>(defaultContextValue);

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<Theme>('light');
  const [mounted, setMounted] = useState(false);

  // Load theme from localStorage on mount
  useEffect(() => {
    try {
      if (typeof window !== 'undefined') {
        const savedTheme = localStorage.getItem('theme') as Theme;
        if (savedTheme && (savedTheme === 'light' || savedTheme === 'dark')) {
          setTheme(savedTheme);
        } else {
          // Check system preference
          const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
          const systemTheme = systemPrefersDark ? 'dark' : 'light';
          setTheme(systemTheme);
        }
      }
    } catch (error) {
      // Fallback if localStorage is not available
      console.warn('Could not load theme from localStorage:', error);
      setTheme('light');
    }
    setMounted(true);
  }, []);

  // Apply theme to document
  useEffect(() => {
    if (mounted && typeof window !== 'undefined') {
      const root = document.documentElement;
      root.classList.remove('light', 'dark');
      root.classList.add(theme);
      
      try {
        localStorage.setItem('theme', theme);
      } catch (error) {
        // Handle localStorage errors gracefully
        console.warn('Could not save theme to localStorage:', error);
      }
    }
  }, [theme, mounted]);

  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
  };

  // Always provide the context value
  const contextValue: ThemeContextType = {
    theme,
    toggleTheme,
    mounted
  };

  return (
    <ThemeContext.Provider value={contextValue}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  // Since we now have a default value, this should never be undefined
  // But we'll keep the check for safety
  if (!context) {
    console.warn('useTheme called outside of ThemeProvider, using default values');
    return defaultContextValue;
  }
  return context;
} 