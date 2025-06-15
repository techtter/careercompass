"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState, Suspense } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/Button";

function SignupErrorContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [errorType, setErrorType] = useState<string>("");

  useEffect(() => {
    const error = searchParams.get("error");
    const errorCode = searchParams.get("error_code");
    
    if (error || errorCode) {
      setErrorType(error || errorCode || "unknown");
    } else {
      // If no error specified, redirect back to signup
      router.push("/signup");
    }
  }, [searchParams, router]);

  // Handle different error types
  const getErrorContent = () => {
    if (errorType.includes("identifier_already_exists") || 
        errorType.includes("user_already_exists") ||
        errorType.includes("form_identifier_exists")) {
      return {
        title: "Account Already Exists",
        message: "It looks like you already have an account with us. Please sign in instead.",
        icon: (
          <svg className="w-8 h-8 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
        ),
        primaryAction: {
          text: "Sign In to Your Account",
          href: "/login?from_signup=true"
        },
        secondaryAction: {
          text: "Forgot Password?",
          href: "/login?forgot=true"
        }
      };
    }

    // Default error content
    return {
      title: "Signup Error",
      message: "There was an issue creating your account. Please try again or contact support if the problem persists.",
      icon: (
        <svg className="w-8 h-8 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
        </svg>
      ),
      primaryAction: {
        text: "Try Again",
        href: "/signup"
      },
      secondaryAction: {
        text: "Contact Support",
        href: "mailto:contact@careercompass.ai"
      }
    };
  };

  const errorContent = getErrorContent();

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100 dark:bg-gray-900">
      <div className="max-w-md w-full bg-white dark:bg-gray-800 rounded-lg shadow-md p-8 text-center">
        <div className="mb-6">
          <div className="mx-auto w-16 h-16 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center mb-4">
            {errorContent.icon}
          </div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            {errorContent.title}
          </h2>
          <p className="text-gray-600 dark:text-gray-300">
            {errorContent.message}
          </p>
        </div>
        
        <div className="space-y-4">
          <Link href={errorContent.primaryAction.href} className="block">
            <Button className="w-full">
              {errorContent.primaryAction.text}
            </Button>
          </Link>
          
          <Link href={errorContent.secondaryAction.href} className="block">
            <Button variant="outline" className="w-full">
              {errorContent.secondaryAction.text}
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

export default function SignupErrorPage() {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center min-h-screen bg-gray-100 dark:bg-gray-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2 text-gray-600 dark:text-gray-400">Loading...</p>
        </div>
      </div>
    }>
      <SignupErrorContent />
    </Suspense>
  );
} 