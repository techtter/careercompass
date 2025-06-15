'use client';

import React from 'react';

interface Company {
  name: string;
  logo: React.ReactNode;
}

const companies: Company[] = [
  {
    name: 'Microsoft',
    logo: (
      <svg className="h-8 w-auto" viewBox="0 0 23 23" fill="none">
        <path d="M0 0h11v11H0z" fill="#F25022"/>
        <path d="M12 0h11v11H12z" fill="#7FBA00"/>
        <path d="M0 12h11v11H0z" fill="#00A4EF"/>
        <path d="M12 12h11v11H12z" fill="#FFB900"/>
      </svg>
    )
  },
  {
    name: 'Google',
    logo: (
      <svg className="h-8 w-auto" viewBox="0 0 24 24" fill="none">
        <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
        <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
        <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
        <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
      </svg>
    )
  },
  {
    name: 'Apple',
    logo: (
      <svg className="h-8 w-auto" viewBox="0 0 24 24" fill="none">
        <path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.81-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M13 3.5c.73-.83 1.94-1.46 2.94-1.5.13 1.17-.34 2.35-1.04 3.19-.69.85-1.83 1.51-2.95 1.42-.15-1.15.41-2.35 1.05-3.11z" fill="#000000" className="dark:fill-white"/>
      </svg>
    )
  },
  {
    name: 'Amazon',
    logo: (
      <svg className="h-8 w-auto" viewBox="0 0 100 30" fill="none">
        <path d="M28.61 21.25c-6.5 4.8-15.9 7.35-24 7.35-11.35 0-21.6-4.2-29.35-11.2-.6-.55-.065-1.3.66-.87 8.3 4.83 18.55 7.74 29.15 7.74 7.15 0 15-1.485 22.25-4.56 1.1-.46 2.02.72.95 1.54z" fill="#FF9900"/>
        <path d="M30.85 18.65c-.83-1.065-5.5-.505-7.6-.255-.64.076-.74-.48-.16-.88 3.72-2.62 9.83-1.865 10.54-0.985.71.88-.19 6.99-3.68 9.91-.54.45-1.05.21-.81-.39.78-1.95 2.53-6.32 1.7-7.35z" fill="#FF9900"/>
        <path d="M27.79 2.68v-1.7c0-.26.19-.43.43-.43h7.63c.245 0 .44.18.44.43v1.46c-.005.245-.21.56-.58.106l-3.96-3.96c-.37-.37-.98-.37-1.35 0l-3.96 3.96c-.37.455-.575.139-.58-.106z" fill="#232F3E"/>
        <path d="M8.18 15.74h-2.42c-.23-.015-.41-.19-.43-.41V2.68c0-.245.2-.44.45-.44h2.25c.255.01.46.21.47.46v1.73h.045c.63-1.68 1.81-2.46 3.41-2.46 1.62 0 2.63.78 3.36 2.46.63-1.68 2.11-2.46 3.58-2.46 1.09 0 2.27.45 2.99 1.46.81 1.12.64 2.74.64 4.16v8.14c0 .245-.2.44-.45.44h-2.42c-.26-.015-.46-.19-.47-.44V7.57c0-.56.05-1.95-.07-2.46-.19-.84-.76-1.08-1.49-1.08-.61 0-1.25.41-1.51 1.06-.26.65-.23 1.74-.23 2.48v7.16c0 .245-.2.44-.45.44h-2.42c-.26-.015-.46-.19-.47-.44V7.57c0-1.51.24-3.73-1.56-3.73-1.83 0-1.76 2.09-1.76 3.73v7.73c0 .245-.2.44-.45.44z" fill="#232F3E"/>
        <path d="M64.55 1.78c3.6 0 5.54 3.09 5.54 7.02 0 3.8-2.15 6.81-5.54 6.81-3.53 0-5.45-3.09-5.45-6.93 0-3.87 1.95-6.9 5.45-6.9zm0 2.51c-1.78 0-1.89 2.43-1.89 3.94 0 1.52-.02 4.75 1.87 4.75 1.87 0 1.96-2.61 1.96-4.2 0-.99-.05-2.3-.4-3.26-.31-.84-.78-1.23-1.54-1.23z" fill="#232F3E"/>
        <path d="M75.49 15.74h-2.4c-.26-.015-.46-.19-.47-.44V2.68c.02-.245.22-.44.47-.44h2.23c.22.01.4.16.45.37v1.95h.045c.7-1.75 1.69-2.59 3.44-2.59.81 0 1.6.29 2.11 1.08.47.73.47 1.95.47 2.83v9.42c-.02.245-.22.44-.47.44h-2.42c-.24-.015-.43-.19-.45-.44V6.49c0-1.46.16-3.6-1.63-3.6-.63 0-1.21.42-1.49 1.06-.36.82-.4 1.64-.4 2.54v8.81c-.005.245-.2.44-.445.44z" fill="#232F3E"/>
      </svg>
    )
  },
  {
    name: 'Netflix',
    logo: (
      <svg className="h-8 w-auto" viewBox="0 0 24 24" fill="none">
        <path d="M5.398 0v.006c3.028 8.556 5.37 15.175 8.348 23.596 2.344.058 4.85.398 4.854.398-2.8-7.924-5.923-16.747-8.487-24H5.398z" fill="#E50914"/>
        <path d="M5.398 0h4.715l2.883 8.157v15.839c-2.883-.398-5.37-.82-7.598-.82V0z" fill="#E50914"/>
        <path d="M18.6 0v22.951L13.887 9.63V0H18.6z" fill="#E50914"/>
      </svg>
    )
  },
  {
    name: 'Tesla',
    logo: (
      <svg className="h-8 w-auto" viewBox="0 0 24 24" fill="none">
        <path d="M12 1.5L2.5 4.5v1.2L12 3.2l9.5 2.7V4.5L12 1.5z" fill="#E31937"/>
        <path d="M12 6L2.5 8.7v1.2L12 7.2l9.5 2.7V8.7L12 6z" fill="#E31937"/>
        <path d="M2.5 11.4v1.2h19v-1.2h-19z" fill="#E31937"/>
        <path d="M2.5 14.1v1.2h19v-1.2h-19z" fill="#E31937"/>
        <path d="M2.5 16.8v1.2h19v-1.2h-19z" fill="#E31937"/>
        <path d="M2.5 19.5v1.2h19v-1.2h-19z" fill="#E31937"/>
        <path d="M10.8 22.2h2.4v1.2h-2.4v-1.2z" fill="#E31937"/>
      </svg>
    )
  },
  {
    name: 'Meta',
    logo: (
      <svg className="h-8 w-auto" viewBox="0 0 24 24" fill="none">
        <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" fill="#1877F2"/>
      </svg>
    )
  },
  {
    name: 'Spotify',
    logo: (
      <svg className="h-8 w-auto" viewBox="0 0 24 24" fill="none">
        <path d="M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 11.64 1.32.42.18.479.659.301 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719 1.02.419 1.56-.299.421-1.02.599-1.559.3z" fill="#1DB954"/>
      </svg>
    )
  },
  {
    name: 'Uber',
    logo: (
      <svg className="h-8 w-auto" viewBox="0 0 24 24" fill="none">
        <path d="M16.812 9.6V24H7.188V9.6h9.624z" fill="#000000" className="dark:fill-white"/>
        <path d="M24 7.2c0 3.972-3.228 7.2-7.2 7.2s-7.2-3.228-7.2-7.2S12.828 0 16.8 0 24 3.228 24 7.2z" fill="#000000" className="dark:fill-white"/>
        <path d="M7.2 0C3.228 0 0 3.228 0 7.2s3.228 7.2 7.2 7.2V0z" fill="#000000" className="dark:fill-white"/>
      </svg>
    )
  },
  {
    name: 'Airbnb',
    logo: (
      <svg className="h-8 w-auto" viewBox="0 0 24 24" fill="none">
        <path d="M12 0C7.8 0 4.4 3.4 4.4 7.6 4.4 13 12 24 12 24s7.6-11 7.6-16.4C19.6 3.4 16.2 0 12 0zm0 11.6c-2.2 0-4-1.8-4-4s1.8-4 4-4 4 1.8 4 4-1.8 4-4 4z" fill="#FF5A5F"/>
      </svg>
    )
  }
];

export default function CompanyMarquee() {
  // Duplicate the companies array to create seamless loop
  const duplicatedCompanies = [...companies, ...companies];

  return (
    <section className="py-4 bg-white dark:bg-gray-900 overflow-hidden">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <p className="text-center text-gray-500 dark:text-gray-400 text-sm font-medium mb-4">
          Trusted by professionals at leading companies
        </p>
        
        {/* Marquee Container */}
        <div className="relative">
          {/* Gradient overlays for smooth fade effect */}
          <div className="absolute left-0 top-0 w-20 h-full bg-gradient-to-r from-white dark:from-gray-900 to-transparent z-10"></div>
          <div className="absolute right-0 top-0 w-20 h-full bg-gradient-to-l from-white dark:from-gray-900 to-transparent z-10"></div>
          
          {/* Scrolling container */}
          <div className="flex animate-marquee space-x-16 items-center">
            {duplicatedCompanies.map((company, index) => (
              <div
                key={`${company.name}-${index}`}
                className="flex items-center space-x-3 hover:scale-105 transition-transform duration-300 flex-shrink-0"
              >
                <div className="w-8 h-8 flex items-center justify-center">
                  {company.logo}
                </div>
                <span className="text-xl font-bold whitespace-nowrap text-gray-600 dark:text-gray-300">
                  {company.name}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
} 