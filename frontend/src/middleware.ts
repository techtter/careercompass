import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server';
import { NextResponse } from 'next/server';

const isProtectedRoute = createRouteMatcher(['/dashboard(.*)']);
const isAuthRoute = createRouteMatcher(['/login', '/signup']);

export default clerkMiddleware(async (auth, req) => {
  try {
    const { userId } = await auth();
    
    // If user is signed in and trying to access auth pages, redirect to dashboard
    if (userId && isAuthRoute(req)) {
      return NextResponse.redirect(new URL('/dashboard', req.url));
    }
    
    // Protect dashboard routes
    if (isProtectedRoute(req)) {
      await auth.protect();
    }
  } catch (error) {
    // In development, if Clerk auth fails, allow access to continue for testing
    console.warn('Clerk authentication error:', error);
    
    // For development mode, allow access to protected routes
    if (process.env.NODE_ENV === 'development') {
      return NextResponse.next();
    }
    
    // In production, redirect to login
    if (isProtectedRoute(req)) {
      return NextResponse.redirect(new URL('/login', req.url));
    }
  }
});

export const config = {
  matcher: [
    // Skip Next.js internals and all static files, unless found in search params
    '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
    // Always run for API routes
    '/(api|trpc)(.*)',
  ],
}; 