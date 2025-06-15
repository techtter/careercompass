"use client";

import React, { createContext, useContext, useEffect, useState } from 'react';
import { useUser } from '@clerk/nextjs';

interface UserProfile {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  fullName: string;
  imageUrl: string;
  skills: string[];
  experience: string;
  location: string;
  jobTitle: string;
  company: string;
  education: string[];
  certifications: string[];
  experienceYears: number;
  lastThreeJobTitles: string[];
}

interface UserProfileContextType {
  userProfile: UserProfile | null;
  isLoading: boolean;
  error: string | null;
  refreshProfile: () => Promise<void>;
  updateProfile: (profile: UserProfile) => void;
  clearProfile: () => void;
}

const UserProfileContext = createContext<UserProfileContextType | undefined>(undefined);

export function UserProfileProvider({ children }: { children: React.ReactNode }) {
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { user, isLoaded, isSignedIn } = useUser();

  const fetchUserProfile = async (): Promise<UserProfile | null> => {
    if (!user?.id) return null;

    try {
      // First try to get profile from backend API (which may have CV data)
      const response = await fetch(`/api/user-profile/${user.id}`);
      if (response.ok) {
        const profile = await response.json();
        if (profile) {
          return {
            id: user.id,
            email: profile.email || user.emailAddresses?.[0]?.emailAddress || '',
            firstName: profile.firstName || user.firstName || '',
            lastName: profile.lastName || user.lastName || '',
            fullName: profile.firstName && profile.lastName 
              ? `${profile.firstName} ${profile.lastName}` 
              : user.fullName || `${user.firstName || ''} ${user.lastName || ''}`.trim(),
            imageUrl: user.imageUrl || '',
            skills: profile.skills || [],
            experience: profile.experience || '',
            location: profile.location || '',
            jobTitle: profile.jobTitle || '',
            company: profile.company || '',
            education: profile.education || [],
            certifications: profile.certifications || [],
            experienceYears: profile.experienceYears || 0,
            lastThreeJobTitles: profile.lastThreeJobTitles || []
          };
        }
      }
    } catch (error) {
      console.log('Backend profile not available, using session data:', error);
    }

    // Fall back to session context data without hardcoded defaults
    const sessionProfile: UserProfile = {
      id: user.id,
      email: user.emailAddresses?.[0]?.emailAddress || '',
      firstName: user.firstName || '',
      lastName: user.lastName || '',
      fullName: user.fullName || `${user.firstName || ''} ${user.lastName || ''}`.trim(),
      imageUrl: user.imageUrl || '',
      // Only use metadata if it exists, no hardcoded defaults
      skills: (user.publicMetadata?.skills as string[]) || (user.unsafeMetadata?.skills as string[]) || [],
      experience: (user.publicMetadata?.experience as string) || (user.unsafeMetadata?.experience as string) || '',
      location: (user.publicMetadata?.location as string) || (user.unsafeMetadata?.location as string) || '',
      jobTitle: (user.publicMetadata?.jobTitle as string) || (user.unsafeMetadata?.jobTitle as string) || '',
      company: (user.publicMetadata?.company as string) || (user.unsafeMetadata?.company as string) || '',
      education: (user.publicMetadata?.education as string[]) || (user.unsafeMetadata?.education as string[]) || [],
      certifications: (user.publicMetadata?.certifications as string[]) || (user.unsafeMetadata?.certifications as string[]) || [],
      experienceYears: (user.publicMetadata?.experienceYears as number) || (user.unsafeMetadata?.experienceYears as number) || 0,
      lastThreeJobTitles: (user.publicMetadata?.lastThreeJobTitles as string[]) || (user.unsafeMetadata?.lastThreeJobTitles as string[]) || []
    };

    return sessionProfile;
  };

  const refreshProfile = async () => {
    if (!isLoaded || !isSignedIn || !user) return;

    setIsLoading(true);
    setError(null);

    try {
      const profile = await fetchUserProfile();
      setUserProfile(profile);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch user profile';
      setError(errorMessage);
      console.error('Error fetching user profile:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const updateProfile = (profile: UserProfile) => {
    setUserProfile(profile);
    setError(null);
  };

  const clearProfile = () => {
    setUserProfile(null);
    setError(null);
  };

  // Initialize profile when user is loaded and signed in
  useEffect(() => {
    if (isLoaded && isSignedIn && user && !userProfile) {
      refreshProfile();
    } else if (isLoaded && !isSignedIn) {
      clearProfile();
    }
  }, [isLoaded, isSignedIn, user?.id]);

  const contextValue: UserProfileContextType = {
    userProfile,
    isLoading,
    error,
    refreshProfile,
    updateProfile,
    clearProfile
  };

  return (
    <UserProfileContext.Provider value={contextValue}>
      {children}
    </UserProfileContext.Provider>
  );
}

export function useUserProfile() {
  const context = useContext(UserProfileContext);
  if (context === undefined) {
    throw new Error('useUserProfile must be used within a UserProfileProvider');
  }
  return context;
} 