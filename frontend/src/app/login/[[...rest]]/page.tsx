"use client";

import { SignIn } from "@clerk/nextjs";
import { useAuth } from "@clerk/nextjs";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState, Suspense } from "react";
import Link from "next/link";

function LoginContent() {
  const { isLoaded, isSignedIn } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const [showExistingUserMessage, setShowExistingUserMessage] = useState(false);
  const [showForgotPassword, setShowForgotPassword] = useState(false);

  // Check if user is already signed in
  useEffect(() => {
    if (isLoaded && isSignedIn) {
      router.push("/dashboard");
    }
  }, [isLoaded, isSignedIn, router]);

  // Check for redirects from signup or forgot password
  useEffect(() => {
    const fromSignup = searchParams.get("from_signup");
    const forgot = searchParams.get("forgot");
    
    if (fromSignup === "true") {
      setShowExistingUserMessage(true);
    }
    
    if (forgot === "true") {
      setShowForgotPassword(true);
    }
  }, [searchParams]);

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100 dark:bg-gray-900">
      <div className="w-full max-w-md">
        {/* Show message if redirected from signup */}
        {showExistingUserMessage && (
          <div className="mb-6 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
            <div className="flex items-center space-x-2">
              <svg className="w-5 h-5 text-blue-600 dark:text-blue-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
              <div>
                <p className="text-blue-800 dark:text-blue-200 font-medium">Account Already Exists</p>
                <p className="text-blue-700 dark:text-blue-300 text-sm">Please sign in with your existing credentials.</p>
              </div>
            </div>
          </div>
        )}

        <SignIn 
          appearance={{
            elements: {
              rootBox: "mx-auto",
              card: "shadow-lg",
            }
          }}
          redirectUrl="/dashboard"
          afterSignInUrl="/dashboard"
          routing="path"
          path="/login"
        />
        
        {/* Additional help text */}
        <div className="mt-6 text-center">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Don't have an account?{" "}
            <Link href="/signup" className="text-blue-600 dark:text-blue-400 hover:underline">
              Sign up here
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center min-h-screen bg-gray-100 dark:bg-gray-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2 text-gray-600 dark:text-gray-400">Loading...</p>
        </div>
      </div>
    }>
      <LoginContent />
    </Suspense>
  );
} 