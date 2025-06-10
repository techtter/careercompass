# Clerk Authentication Setup Guide

## Fix "redirect_uri_mismatch" Error

To fix the authentication error, you need to configure the correct redirect URIs in your Clerk dashboard:

### Step 1: Go to Clerk Dashboard
1. Visit [clerk.com](https://clerk.com) and log into your account
2. Select your "Career Compass AI" application

### Step 2: Configure Redirect URIs
In your Clerk dashboard, go to **Configure > Paths** and set:

**For Development (localhost):**
- **Sign-in redirect URL**: `http://localhost:3000/dashboard`
- **Sign-up redirect URL**: `http://localhost:3000/dashboard`  
- **Sign-in fallback redirect URL**: `http://localhost:3000`
- **Sign-up fallback redirect URL**: `http://localhost:3000`

**Allowed redirect URLs (add all of these):**
- `http://localhost:3000`
- `http://localhost:3000/dashboard`
- `http://localhost:3000/login`
- `http://localhost:3000/signup`
- `http://localhost:3001` (backup port)
- `http://localhost:3002` (backup port)

### Step 3: Configure Sign-in/Sign-up URLs
In **Configure > Paths**, also set:
- **Sign-in page URL**: `/login`
- **Sign-up page URL**: `/signup`

### Step 4: Save and Test
1. Save all changes in Clerk dashboard
2. Restart your Next.js server: `npm run dev`
3. Try signing in again

### Current Environment Variables Required
Make sure your `.env.local` file has:
```env
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_your_key_here
CLERK_SECRET_KEY=sk_test_your_key_here

# These should match your Clerk dashboard configuration
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/login
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/signup
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/dashboard
```

### Common Issues:
1. **Port mismatch**: Make sure the port in Clerk dashboard matches your dev server port (3000, 3001, or 3002)
2. **HTTP vs HTTPS**: Use `http://` for localhost development
3. **Trailing slashes**: Don't add trailing slashes to URLs
4. **Case sensitivity**: URLs are case-sensitive

After making these changes, the authentication should work properly! 