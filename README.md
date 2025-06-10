# Career Compass AI

A comprehensive AI-powered career planning and job search platform built with Next.js and FastAPI.

## 🚀 Features

- **AI-Powered Career Planning**: Get personalized career roadmaps and guidance
- **Job Discovery & Matching**: Smart job search with semantic matching
- **Skill Gap Analysis**: Identify skills you need and get learning recommendations
- **Resume & LinkedIn Optimization**: AI-powered profile optimization
- **Interview Coaching**: Practice interviews with AI feedback
- **Goal Setting & Progress Tracking**: Monitor your career development
- **Market Insights**: Real-time labor market trends and salary data

## 🏗️ Tech Stack

### Frontend
- **Next.js 15.3.3** - React framework with App Router
- **React 18** - UI library
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Clerk** - Authentication

### Backend
- **FastAPI** - Python web framework
- **Supabase** - Database and real-time features
- **OpenAI API** - AI integrations
- **Python 3.8+** - Backend language

## 📁 Project Structure

```
CareerCompassAI/
├── frontend/                # Next.js frontend application
│   ├── src/
│   │   ├── app/            # Next.js App Router pages
│   │   ├── components/     # Reusable UI components
│   │   ├── lib/           # Utility functions
│   │   └── middleware.ts  # Clerk authentication middleware
│   ├── public/            # Static assets
│   └── package.json       # Frontend dependencies
├── backend/               # FastAPI backend application
│   ├── main.py           # FastAPI application entry point
│   ├── database.py       # Database configuration
│   ├── ai_services.py    # AI service integrations
│   ├── clerk.py          # Clerk integration
│   └── requirements.txt  # Backend dependencies
├── PRD.md                # Product Requirements Document
└── README.md             # This file
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.8+
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/techtter/careercompass.git
cd careercompass
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:3000`

### 3. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

The backend API will be available at `http://localhost:8000`

### 4. Environment Variables

Create `.env.local` in the frontend directory:
```env
# Clerk Authentication
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_your_key_here
CLERK_SECRET_KEY=sk_test_your_key_here

# Clerk URLs
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/login
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/signup
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/dashboard
```

Create `.env` in the backend directory:
```env
# Database
DATABASE_URL=your_supabase_database_url

# AI Services
OPENAI_API_KEY=your_openai_api_key

# Clerk
CLERK_SECRET_KEY=sk_test_your_key_here
```

## 🔧 Development

### Frontend Development
```bash
cd frontend
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server
npm run lint         # Run ESLint
```

### Backend Development
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 🌐 Authentication Setup

This project uses Clerk for authentication. To set up:

1. Create a Clerk account at [clerk.com](https://clerk.com)
2. Create a new application
3. Configure redirect URLs in Clerk dashboard:
   - Sign-in redirect: `http://localhost:3000/dashboard`
   - Sign-up redirect: `http://localhost:3000/dashboard`
4. Add your Clerk keys to `.env.local`

See `frontend/CLERK_SETUP.md` for detailed setup instructions.

## 📚 API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for interactive API documentation.

## 🛠️ Available Scripts

### Frontend Scripts
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run linting

### Backend Scripts
- `uvicorn main:app --reload` - Start development server
- `python -m pytest` - Run tests (when added)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Links

- [Product Requirements Document](PRD.md)
- [Frontend Setup Guide](frontend/SETUP.md)
- [Clerk Authentication Guide](frontend/CLERK_SETUP.md)

## 🚀 Deployment

### Frontend (Vercel)
1. Connect your GitHub repository to Vercel
2. Set environment variables in Vercel dashboard
3. Deploy automatically on push to main branch

### Backend (Railway/Heroku)
1. Create a new service on Railway or Heroku
2. Connect your GitHub repository
3. Set environment variables
4. Deploy automatically on push to main branch

---

**Career Compass AI** - Empowering your career journey with AI 🚀 