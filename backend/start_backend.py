#!/usr/bin/env python3
"""
Backend startup script with proper error handling and configuration
"""
import os
import sys
import uvicorn
from pathlib import Path

def setup_environment():
    """Setup environment variables with fallback values"""
    
    # Set OpenAI API key with fallback
    if not os.getenv('OPENAI_API_KEY'):
        os.environ['OPENAI_API_KEY'] = 'sk-proj-placeholder-key-for-development'
        print("Warning: Using placeholder OpenAI API key")
    
    # Set Supabase credentials with fallbacks
    if not os.getenv('SUPABASE_URL'):
        os.environ['SUPABASE_URL'] = 'https://placeholder.supabase.co'
        print("Warning: Using placeholder Supabase URL")
    
    if not os.getenv('SUPABASE_ANON_KEY'):
        os.environ['SUPABASE_ANON_KEY'] = 'placeholder_key'
        print("Warning: Using placeholder Supabase key")
    
    # Set Clerk credentials with fallbacks
    if not os.getenv('CLERK_SECRET_KEY'):
        os.environ['CLERK_SECRET_KEY'] = 'sk_test_placeholder'
        print("Warning: Using placeholder Clerk secret key")
    
    if not os.getenv('NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY'):
        os.environ['NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY'] = 'pk_test_placeholder'
        print("Warning: Using placeholder Clerk publishable key")

def start_server():
    """Start the FastAPI server with proper configuration"""
    setup_environment()
    
    print("Starting CareerCompass Backend...")
    print(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    print(f"OpenAI API Key: {'***' + os.getenv('OPENAI_API_KEY', '')[-4:] if os.getenv('OPENAI_API_KEY') else 'Not set'}")
    print("Backend will run on http://localhost:8000")
    print("-" * 50)
    
    try:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            reload_dirs=["./"],
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\nBackend server stopped.")
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_server() 