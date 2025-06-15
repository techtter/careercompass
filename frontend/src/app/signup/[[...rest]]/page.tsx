"use client";

import { SignUp } from "@clerk/nextjs";
import { useAuth } from "@clerk/nextjs";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState, Suspense } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/Button";

function SignupContent() {
  const { isLoaded, isSignedIn } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const [showExistingUserMessage, setShowExistingUserMessage] = useState(false);

  // Check if user is already signed in
  useEffect(() => {
    if (isLoaded && isSignedIn) {
      router.push("/dashboard");
    }
  }, [isLoaded, isSignedIn, router]);

  // Check for existing user redirect
  useEffect(() => {
    const existingUser = searchParams.get("existing_user");
    if (existingUser === "true") {
      setShowExistingUserMessage(true);
    }
  }, [searchParams]);

  // Monitor for Clerk errors in the DOM
  useEffect(() => {
    const checkForErrors = () => {
      // Look for Clerk error messages in the DOM
      const errorElements = document.querySelectorAll('[data-localization-key*="error"], .cl-formFieldErrorText, .cl-alert');
      
      for (const element of errorElements) {
        const errorText = element.textContent?.toLowerCase() || '';
        
        // Check for existing user errors
        if (errorText.includes('already exists') || 
            errorText.includes('identifier already exists') ||
            errorText.includes('email address is taken') ||
            errorText.includes('user already exists')) {
          
          console.log('Detected existing user error, redirecting to login');
          router.push('/login?from_signup=true');
          return;
        }
      }
    };

    // Check immediately
    checkForErrors();

    // Set up a mutation observer to watch for DOM changes
    const observer = new MutationObserver(() => {
      checkForErrors();
    });

    // Start observing
    observer.observe(document.body, {
      childList: true,
      subtree: true,
      characterData: true
    });

    // Cleanup
    return () => {
      observer.disconnect();
    };
  }, [router]);

  // Show existing user message and redirect to sign-in
  if (showExistingUserMessage) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-100 dark:bg-gray-900">
        <div className="max-w-md w-full bg-white dark:bg-gray-800 rounded-lg shadow-md p-8 text-center">
          <div className="mb-6">
            <div className="mx-auto w-16 h-16 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center mb-4">
              <svg className="w-8 h-8 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
              Account Already Exists
            </h2>
            <p className="text-gray-600 dark:text-gray-300">
              It looks like you already have an account with us. Please sign in instead.
            </p>
          </div>
          
          <div className="space-y-4">
            <Link href="/login" className="block">
              <Button className="w-full">
                Sign In to Your Account
              </Button>
            </Link>
            
            <Link href="/login?forgot=true" className="block">
              <Button variant="outline" className="w-full">
                Forgot Password?
              </Button>
            </Link>
            
            <Link href="/" className="block text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300">
              ← Back to Home
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100 dark:bg-gray-900">
      <div className="w-full max-w-md">
        <SignUp 
          appearance={{
            elements: {
              rootBox: "mx-auto",
              card: "shadow-lg",
            }
          }}
          redirectUrl="/dashboard"
          afterSignUpUrl="/dashboard"
          routing="path"
          path="/signup"
          signInUrl="/login"
        />
        
        {/* Additional help text */}
        <div className="mt-6 text-center">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Already have an account?{" "}
            <Link href="/login" className="text-blue-600 dark:text-blue-400 hover:underline">
              Sign in here
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}

export default function SignupPage() {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center min-h-screen bg-gray-100 dark:bg-gray-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2 text-gray-600 dark:text-gray-400">Loading...</p>
        </div>
      </div>
    }>
      <SignupContent />
    </Suspense>
  );
} 