# OpenAI Setup for Intelligent Resume Parsing

The Career Compass AI now uses OpenAI's GPT models to intelligently parse resumes and extract detailed information. This provides much more accurate results than regex-based parsing.

## Setup Instructions

### 1. Get OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in to your account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the API key (starts with `sk-`)

### 2. Configure Environment Variable

Create a `.env.local` file in the `frontend` directory and add:

```env
OPENAI_API_KEY=your_actual_openai_api_key_here
```

**Important**: Replace `your_actual_openai_api_key_here` with your real OpenAI API key.

### 3. Restart Development Server

After adding the API key, restart your development server:

```bash
npm run dev
```

## Features

With OpenAI integration enabled, the resume parser can extract:

- **Name**: Full name of the person
- **Experience**: Years of experience or experience level description
- **Skills**: Technical and professional skills (up to 8 most relevant)
- **Job Titles**: Two most recent job titles
- **Email**: Email address if found in resume
- **Phone**: Phone number if found
- **Location**: Location or city if mentioned
- **Education**: Highest degree or latest education
- **Summary**: Professional summary

## Fallback Mode

If no OpenAI API key is configured, the system automatically falls back to regex-based parsing. While less accurate, this ensures the application continues to work without requiring an API key.

## Cost Considerations

- Using GPT-3.5-turbo model (cost-effective)
- Each resume parsing costs approximately $0.001-0.003
- Temperature set to 0.1 for consistent results
- Limited to 1000 tokens per request

## Security

- API key is stored as environment variable (not in code)
- .env.local files are gitignored by default
- Never commit API keys to version control

## Troubleshooting

1. **"Falling back to basic parsing"**: Check that your API key is correctly set
2. **Invalid API key error**: Verify the key is active and properly formatted
3. **Rate limiting**: OpenAI has rate limits; consider implementing retry logic for production

For any issues, check the browser console and server logs for detailed error messages. 