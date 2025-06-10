# Career Compass AI - Frontend Setup

## Authentication Setup (Clerk)

To enable user authentication, you need to configure Clerk:

### 1. Create a Clerk Account
- Go to [clerk.com](https://clerk.com)
- Sign up for a free account
- Create a new application

### 2. Get Your API Keys
From your Clerk dashboard, copy:
- Publishable Key
- Secret Key

### 3. Create Environment File
Create a `.env.local` file in the frontend directory with:

```env
# Clerk Authentication Keys
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_your_key_here
CLERK_SECRET_KEY=sk_test_your_key_here

# Clerk URLs
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/login
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/signup
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/dashboard
```

### 4. Update Login/Signup Pages
Once configured, update the login and signup pages to use Clerk components:

```tsx
// src/app/login/page.tsx
import { SignIn } from "@clerk/nextjs";

export default function LoginPage() {
  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <SignIn />
    </div>
  );
}
```

```tsx
// src/app/signup/page.tsx
import { SignUp } from "@clerk/nextjs";

export default function SignupPage() {
  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <SignUp />
    </div>
  );
}
```

### 5. Restart Development Server
After adding environment variables, restart the server:

```bash
npm run dev
```

## Current Status
- ✅ Landing page working
- ✅ Navigation links fixed
- ⏳ Authentication requires setup (see above)
- ⏳ Dashboard requires authentication

## Navigation
- Landing page: `/`
- Login: `/login`
- Signup: `/signup`
- Dashboard: `/dashboard` (requires auth) 