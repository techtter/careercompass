"use client";

import React, { createContext, useContext, useEffect, useState } from 'react';

type Theme = 'light' | 'dark';

interface ThemeContextType {
  theme: Theme;
  toggleTheme: () => void;
  mounted: boolean;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<Theme>('light');
  const [mounted, setMounted] = useState(false);

  // Apply theme to document
  const applyTheme = (newTheme: Theme) => {
    if (typeof window !== 'undefined') {
      const root = document.documentElement;
      
      // Remove existing theme classes
      root.classList.remove('light', 'dark');
      // Add new theme class
      root.classList.add(newTheme);
      // Set color scheme
      root.style.colorScheme = newTheme;
      
      // Force a repaint to ensure the theme is applied
      root.style.display = 'none';
      root.offsetHeight; // Trigger reflow
      root.style.display = '';
      
      try {
        localStorage.setItem('theme', newTheme);
        console.log(`Theme applied: ${newTheme}`);
      } catch (error) {
        console.warn('Could not save theme to localStorage:', error);
      }
    }
  };

  // Initialize theme on mount
  useEffect(() => {
    const initializeTheme = () => {
      try {
        if (typeof window !== 'undefined') {
          const savedTheme = localStorage.getItem('theme') as Theme;
          const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
          
          let initialTheme: Theme;
          if (savedTheme && (savedTheme === 'light' || savedTheme === 'dark')) {
            initialTheme = savedTheme;
          } else {
            initialTheme = systemPrefersDark ? 'dark' : 'light';
          }
          
          console.log(`Initializing theme: ${initialTheme}`);
          setTheme(initialTheme);
          applyTheme(initialTheme);
        }
      } catch (error) {
        console.warn('Could not initialize theme:', error);
        setTheme('light');
        applyTheme('light');
      } finally {
        setMounted(true);
      }
    };

    initializeTheme();
  }, []);

  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    console.log(`Toggling theme from ${theme} to ${newTheme}`);
    setTheme(newTheme);
    applyTheme(newTheme);
  };

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
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
} 