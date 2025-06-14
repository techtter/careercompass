# API Setup Guide for CareerCompassAI

## Real Job API Configuration

CareerCompassAI fetches real job data from multiple job APIs. To enable all features, you need to set up API keys.

### Quick Setup

1. **Create a `.env` file** in the `backend` directory:
   ```bash
   cd backend
   touch .env
   ```

2. **Add your API keys** to the `.env` file:
   ```env
   # Job API Configuration
   USE_REAL_JOBS=true

   # RapidAPI Key for JSearch (LinkedIn/Indeed jobs)
   RAPID_API_KEY=your_actual_rapidapi_key_here

   # Adzuna API credentials  
   ADZUNA_APP_ID=your_actual_adzuna_app_id_here
   ADZUNA_APP_KEY=your_actual_adzuna_api_key_here

   # OpenAI API Key (required for AI services)
   OPENAI_API_KEY=your_actual_openai_api_key_here

   # Claude API Key (for document analysis)
   CLAUDE_API_KEY=your_actual_claude_api_key_here
   ```

### API Key Sources

#### 1. JSearch API (LinkedIn/Indeed Jobs) - **Recommended**
- **URL**: https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch
- **What it provides**: LinkedIn and Indeed job listings
- **Cost**: Free tier available (100 requests/month)
- **Setup**: Sign up for RapidAPI, subscribe to JSearch API, copy your API key

#### 2. Adzuna API (Job Aggregator)
- **URL**: https://developer.adzuna.com/
- **What it provides**: Indeed, LinkedIn, and other job board data
- **Cost**: Free tier available (1000 requests/month)
- **Setup**: Register for Adzuna developer account, get App ID and API Key

#### 3. RemoteOK API (Remote Jobs) - **No Setup Required**
- **What it provides**: Remote job listings
- **Cost**: Free
- **Setup**: None required - works automatically

### Testing Your Setup

Run the test script to verify your API configuration:

```bash
cd backend
python test_real_jobs.py
```

### What Works Without API Keys

Even without any API keys, the system will:
- ✅ Fetch real remote jobs from RemoteOK API
- ✅ Generate high-quality mock jobs that simulate real API responses
- ✅ Provide location-based job prioritization
- ✅ Apply relevance scoring based on user skills and experience

### What You Get With API Keys

With proper API keys configured:
- 🚀 **More real jobs**: Access to LinkedIn, Indeed, and other major job boards
- 🎯 **Better targeting**: Location-specific job searches
- 📊 **Higher quality**: Real company data, salaries, and job descriptions
- 🔄 **Fresh data**: Recently posted jobs from multiple sources

### Environment Variable Priority

The system loads environment variables in this order:
1. `.env` file (highest priority)
2. `config.env` file (fallback)
3. System environment variables

### Security Notes

- ⚠️ **Never commit your `.env` file** to version control
- ✅ The `.env` file is already in `.gitignore`
- 🔒 Keep your API keys secure and rotate them regularly

### Troubleshooting

If you're not seeing real jobs:

1. **Check your `.env` file** exists in the `backend` directory
2. **Verify API keys** are correct (no extra spaces or quotes)
3. **Run the test script** to see detailed error messages
4. **Check API quotas** - you might have exceeded free tier limits

### Support

For issues with specific APIs:
- **JSearch API**: Check RapidAPI dashboard for usage and errors
- **Adzuna API**: Check Adzuna developer console for quota and status
- **RemoteOK API**: Should work without setup - check internet connection

The system is designed to gracefully fall back to mock data if APIs are unavailable, so your application will always work even without API keys. 