import type { Metadata } from "next";
import React from "react";
import "./globals.css";
import { ClerkProvider } from "@clerk/nextjs";
import { ThemeProvider } from "@/contexts/ThemeContext";
import { UserProfileProvider } from "@/contexts/UserProfileContext";

export const metadata: Metadata = {
  title: "Career Compass AI",
  description: "AI-powered career guidance for professional growth",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ClerkProvider
      afterSignInUrl="/dashboard"
      afterSignUpUrl="/dashboard"
      signInUrl="/login"
      signUpUrl="/signup"
    >
      <html lang="en" className="light" suppressHydrationWarning>
        <head>
          <script
            dangerouslySetInnerHTML={{
              __html: `
                (function() {
                  function applyTheme() {
                    try {
                      var savedTheme = localStorage.getItem('theme');
                      var systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
                      var theme = savedTheme || (systemPrefersDark ? 'dark' : 'light');
                      
                      // Ensure we remove any existing theme classes first
                      document.documentElement.classList.remove('light', 'dark');
                      // Add the correct theme class
                      document.documentElement.classList.add(theme);
                      // Set the color scheme
                      document.documentElement.style.colorScheme = theme;
                      
                      // Store the theme for consistency
                      localStorage.setItem('theme', theme);
                      
                      console.log('Theme applied:', theme);
                    } catch (e) {
                      console.warn('Theme initialization error:', e);
                      document.documentElement.classList.remove('light', 'dark');
                      document.documentElement.classList.add('light');
                      document.documentElement.style.colorScheme = 'light';
                    }
                  }
                  
                  // Apply theme immediately
                  applyTheme();
                  
                  // Also apply when DOM is ready
                  if (document.readyState === 'loading') {
                    document.addEventListener('DOMContentLoaded', applyTheme);
                  }
                })();
              `,
            }}
          />
        </head>
        <body className="font-sans antialiased transition-colors duration-300 bg-white dark:bg-gray-900 text-gray-900 dark:text-white min-h-screen" suppressHydrationWarning>
          <ThemeProvider>
            <UserProfileProvider>
              {children}
            </UserProfileProvider>
          </ThemeProvider>
        </body>
      </html>
    </ClerkProvider>
  );
}
