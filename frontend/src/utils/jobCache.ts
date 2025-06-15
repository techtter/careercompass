/**
 * Frontend Job Caching System for Career Compass AI
 * Provides session storage caching for job recommendations to improve performance
 */

interface JobRecommendation {
  id: string;
  title: string;
  company: string;
  location: string;
  country: string;
  salary?: string;
  description: string;
  applyUrl: string;
  source: string;
  postedDate?: string;
  daysAgo?: number;
  is_real_job?: boolean;
  match_score?: number;
}

interface CachedJobData {
  jobs: JobRecommendation[];
  timestamp: number;
  userId: string;
  profileHash: string;
  expiresAt: number;
}

interface UserProfile {
  firstName: string;
  lastName: string;
  skills: string[];
  experienceYears: number;
  lastThreeJobTitles: string[];
  location?: string | null;  // Allow null to match dashboard interface
}

class JobCacheManager {
  private readonly CACHE_KEY_PREFIX = 'careercompass_jobs_';
  private readonly DEFAULT_TTL_MINUTES = 30;
  private readonly MAX_CACHE_SIZE = 10; // Maximum number of cached job sets

  /**
   * Generate a cache key based on user profile
   */
  private generateCacheKey(userId: string): string {
    return `${this.CACHE_KEY_PREFIX}${userId}`;
  }

  /**
   * Generate a profile hash for cache validation
   */
  private generateProfileHash(profile: UserProfile): string {
    const profileData = {
      skills: profile.skills.sort(),
      experience: profile.experienceYears,
      lastJobs: profile.lastThreeJobTitles.slice(0, 2).sort(),
      location: profile.location || ''
    };
    
    return btoa(JSON.stringify(profileData));
  }

  /**
   * Check if cached data is still valid
   */
  private isValidCache(cachedData: CachedJobData, currentProfile: UserProfile): boolean {
    const now = Date.now();
    
    // Check if cache has expired
    if (now > cachedData.expiresAt) {
      console.log('🕒 Cache expired');
      return false;
    }

    // Check if profile has changed
    const currentProfileHash = this.generateProfileHash(currentProfile);
    if (cachedData.profileHash !== currentProfileHash) {
      console.log('👤 Profile changed, cache invalid');
      return false;
    }

    return true;
  }

  /**
   * Get cached job recommendations for a user
   */
  getCachedJobs(userId: string, currentProfile: UserProfile): JobRecommendation[] | null {
    try {
      const cacheKey = this.generateCacheKey(userId);
      const cachedDataStr = sessionStorage.getItem(cacheKey);
      
      if (!cachedDataStr) {
        console.log('❌ No cached jobs found');
        return null;
      }

      const cachedData: CachedJobData = JSON.parse(cachedDataStr);
      
      if (!this.isValidCache(cachedData, currentProfile)) {
        // Remove invalid cache
        this.invalidateUserCache(userId);
        return null;
      }

      console.log(`🎯 FRONTEND CACHE HIT: Found ${cachedData.jobs.length} cached jobs for user ${userId}`);
      return cachedData.jobs;
    } catch (error) {
      console.error('Error reading job cache:', error);
      this.invalidateUserCache(userId);
      return null;
    }
  }

  /**
   * Cache job recommendations for a user
   */
  cacheJobs(
    userId: string, 
    jobs: JobRecommendation[], 
    currentProfile: UserProfile,
    ttlMinutes: number = this.DEFAULT_TTL_MINUTES
  ): void {
    try {
      const cacheKey = this.generateCacheKey(userId);
      const now = Date.now();
      
      const cachedData: CachedJobData = {
        jobs,
        timestamp: now,
        userId,
        profileHash: this.generateProfileHash(currentProfile),
        expiresAt: now + (ttlMinutes * 60 * 1000)
      };

      sessionStorage.setItem(cacheKey, JSON.stringify(cachedData));
      console.log(`💾 FRONTEND CACHED: Stored ${jobs.length} jobs for user ${userId} (TTL: ${ttlMinutes} minutes)`);
      
      // Clean up old cache entries if we exceed max size
      this.cleanupOldCache();
    } catch (error) {
      console.error('Error caching jobs:', error);
    }
  }

  /**
   * Invalidate cached jobs for a specific user
   */
  invalidateUserCache(userId: string): void {
    try {
      const cacheKey = this.generateCacheKey(userId);
      sessionStorage.removeItem(cacheKey);
      console.log(`🗑️ FRONTEND CACHE INVALIDATED: Removed cached jobs for user ${userId}`);
    } catch (error) {
      console.error('Error invalidating cache:', error);
    }
  }

  /**
   * Force refresh cache for a user (invalidate and mark for refresh)
   */
  refreshUserCache(userId: string): void {
    this.invalidateUserCache(userId);
    // Set a flag to indicate cache should be refreshed
    const refreshKey = `${this.CACHE_KEY_PREFIX}refresh_${userId}`;
    sessionStorage.setItem(refreshKey, Date.now().toString());
    console.log(`🔄 FRONTEND CACHE REFRESH: Marked user ${userId} for cache refresh`);
  }

  /**
   * Check if user cache should be refreshed
   */
  shouldRefreshCache(userId: string): boolean {
    const refreshKey = `${this.CACHE_KEY_PREFIX}refresh_${userId}`;
    const refreshFlag = sessionStorage.getItem(refreshKey);
    
    if (refreshFlag) {
      sessionStorage.removeItem(refreshKey);
      return true;
    }
    
    return false;
  }

  /**
   * Clean up old cache entries to prevent storage bloat
   */
  private cleanupOldCache(): void {
    try {
      const cacheKeys: string[] = [];
      
      // Find all job cache keys
      for (let i = 0; i < sessionStorage.length; i++) {
        const key = sessionStorage.key(i);
        if (key && key.startsWith(this.CACHE_KEY_PREFIX) && !key.includes('refresh_')) {
          cacheKeys.push(key);
        }
      }

      // If we exceed max cache size, remove oldest entries
      if (cacheKeys.length > this.MAX_CACHE_SIZE) {
        const cacheEntries = cacheKeys.map(key => {
          try {
            const data = JSON.parse(sessionStorage.getItem(key) || '{}');
            return { key, timestamp: data.timestamp || 0 };
          } catch {
            return { key, timestamp: 0 };
          }
        });

        // Sort by timestamp and remove oldest
        cacheEntries.sort((a, b) => a.timestamp - b.timestamp);
        const toRemove = cacheEntries.slice(0, cacheEntries.length - this.MAX_CACHE_SIZE);
        
        toRemove.forEach(entry => {
          sessionStorage.removeItem(entry.key);
        });

        console.log(`🧹 FRONTEND CACHE CLEANUP: Removed ${toRemove.length} old cache entries`);
      }
    } catch (error) {
      console.error('Error cleaning up cache:', error);
    }
  }

  /**
   * Clear all job cache entries
   */
  clearAllCache(): void {
    try {
      const keysToRemove: string[] = [];
      
      for (let i = 0; i < sessionStorage.length; i++) {
        const key = sessionStorage.key(i);
        if (key && key.startsWith(this.CACHE_KEY_PREFIX)) {
          keysToRemove.push(key);
        }
      }

      keysToRemove.forEach(key => sessionStorage.removeItem(key));
      console.log(`🧹 FRONTEND CACHE CLEARED: Removed ${keysToRemove.length} cache entries`);
    } catch (error) {
      console.error('Error clearing cache:', error);
    }
  }

  /**
   * Get cache statistics
   */
  getCacheStats(): {
    totalEntries: number;
    totalJobs: number;
    cacheSize: string;
    oldestEntry: string;
    newestEntry: string;
  } {
    try {
      let totalEntries = 0;
      let totalJobs = 0;
      let oldestTimestamp = Date.now();
      let newestTimestamp = 0;
      let totalSize = 0;

      for (let i = 0; i < sessionStorage.length; i++) {
        const key = sessionStorage.key(i);
        if (key && key.startsWith(this.CACHE_KEY_PREFIX) && !key.includes('refresh_')) {
          totalEntries++;
          
          try {
            const dataStr = sessionStorage.getItem(key) || '';
            totalSize += dataStr.length;
            
            const data: CachedJobData = JSON.parse(dataStr);
            totalJobs += data.jobs.length;
            
            if (data.timestamp < oldestTimestamp) {
              oldestTimestamp = data.timestamp;
            }
            if (data.timestamp > newestTimestamp) {
              newestTimestamp = data.timestamp;
            }
          } catch {
            // Skip invalid entries
          }
        }
      }

      return {
        totalEntries,
        totalJobs,
        cacheSize: `${(totalSize / 1024).toFixed(2)} KB`,
        oldestEntry: totalEntries > 0 ? new Date(oldestTimestamp).toLocaleString() : 'N/A',
        newestEntry: totalEntries > 0 ? new Date(newestTimestamp).toLocaleString() : 'N/A'
      };
    } catch (error) {
      console.error('Error getting cache stats:', error);
      return {
        totalEntries: 0,
        totalJobs: 0,
        cacheSize: '0 KB',
        oldestEntry: 'N/A',
        newestEntry: 'N/A'
      };
    }
  }
}

// Export singleton instance
export const jobCacheManager = new JobCacheManager();

// Export types
export type { JobRecommendation, UserProfile };

// Utility functions
export const getCachedJobs = (userId: string, profile: UserProfile) => 
  jobCacheManager.getCachedJobs(userId, profile);

export const cacheJobs = (userId: string, jobs: JobRecommendation[], profile: UserProfile, ttlMinutes?: number) => 
  jobCacheManager.cacheJobs(userId, jobs, profile, ttlMinutes);

export const invalidateUserJobCache = (userId: string) => 
  jobCacheManager.invalidateUserCache(userId);

export const refreshUserJobCache = (userId: string) => 
  jobCacheManager.refreshUserCache(userId);

export const shouldRefreshJobCache = (userId: string) => 
  jobCacheManager.shouldRefreshCache(userId);

export const clearAllJobCache = () => 
  jobCacheManager.clearAllCache();

export const getJobCacheStats = () => 
  jobCacheManager.getCacheStats(); 