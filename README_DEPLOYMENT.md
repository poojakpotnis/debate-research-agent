# Deployment Guide for Debate Research Assistant

## Secure Public Deployment

This app is designed to be deployed publicly WITHOUT storing your API keys on the server. Users provide their own API keys which are stored only in their browser session.

---

## Deployment Options

### Option 1: Streamlit Community Cloud (Recommended)

1. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/debate-research-agent.git
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub account
   - Select your repository
   - Set main file: `app_secure.py`
   - Click "Deploy"

3. **Configure Secrets** (Optional - only if using Supabase auth):
   - In Streamlit Cloud dashboard, go to App Settings → Secrets
   - Add:
     ```toml
     SUPABASE_URL = "your-supabase-url"
     SUPABASE_ANON_KEY = "your-supabase-anon-key"
     ```

4. **Share your app!**
   - App URL will be: `https://YOUR_APP_NAME.streamlit.app`

---

### Option 2: Heroku

1. **Install Heroku CLI**:
   ```bash
   brew install heroku/brew/heroku  # macOS
   ```

2. **Create `Procfile`**:
   ```bash
   echo "web: streamlit run app_secure.py --server.port=\$PORT --server.headless=true" > Procfile
   ```

3. **Create `runtime.txt`**:
   ```bash
   echo "python-3.10.12" > runtime.txt
   ```

4. **Deploy**:
   ```bash
   heroku create your-app-name
   git push heroku main
   ```

5. **Set environment variables** (Optional - for Supabase):
   ```bash
   heroku config:set SUPABASE_URL=your-url
   heroku config:set SUPABASE_ANON_KEY=your-key
   ```

---

### Option 3: Docker + Cloud Run / ECS

1. **Create `Dockerfile`**:
   ```dockerfile
   FROM python:3.10-slim

   WORKDIR /app

   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   COPY . .

   EXPOSE 8501

   CMD ["streamlit", "run", "app_secure.py", "--server.port=8501", "--server.headless=true"]
   ```

2. **Build and test locally**:
   ```bash
   docker build -t debate-research-app .
   docker run -p 8501:8501 debate-research-app
   ```

3. **Deploy to Google Cloud Run**:
   ```bash
   gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/debate-research
   gcloud run deploy --image gcr.io/YOUR_PROJECT_ID/debate-research --platform managed
   ```

---

## Security Best Practices

### ✅ What We Do

1. **No Server-Side API Key Storage**:
   - API keys are NEVER stored in `.env` on the server
   - Users enter their own keys via the UI
   - Keys stored only in Streamlit session state (browser memory)
   - Keys are never logged or saved to disk

2. **Session Security**:
   - Keys persist only for the duration of the browser session
   - Closing the browser clears all keys
   - No cookies or local storage used

3. **Optional Authentication**:
   - Supabase auth can be enabled for user management
   - Auth is optional - app works without it
   - If enabled, only controls access, not API key storage

### ❌ What We DON'T Do

1. **Never commit API keys to Git**:
   - `.env` is in `.gitignore`
   - Only `.env.example` is committed (with blank values)

2. **Never log API keys**:
   - Keys are not printed to console or logs
   - Error messages don't include key values

3. **Never store keys in database**:
   - Even with Supabase auth, API keys stay in session only

---

## Authentication Setup (Optional)

### Using Supabase

1. **Create Supabase Project**:
   - Go to [supabase.com](https://supabase.com)
   - Create a new project
   - Get your URL and anon key from Settings → API

2. **Configure Environment**:
   - If deploying to Streamlit Cloud: Add to app secrets
   - If deploying elsewhere: Set environment variables:
     ```bash
     export SUPABASE_URL="your-url"
     export SUPABASE_ANON_KEY="your-key"
     ```

3. **Email Templates** (Optional):
   - Customize email templates in Supabase dashboard
   - Authentication → Email Templates

### Disabling Authentication

To deploy without authentication:
- Simply don't set `SUPABASE_URL` and `SUPABASE_ANON_KEY`
- App will skip auth and go straight to API key configuration

---

## Environment Variables

### Required: NONE
The app works out of the box with no server-side configuration!

### Optional (for authentication):
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_ANON_KEY`: Your Supabase anonymous key

---

## User Instructions

Share these instructions with your users:

### Getting API Keys

**OpenAI API Key**:
1. Go to [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Create an account or sign in
3. Click "Create new secret key"
4. Copy the key (you won't see it again!)
5. Add billing information and credits

**Tavily API Key**:
1. Go to [tavily.com](https://tavily.com)
2. Sign up for a free account
3. Get your API key from the dashboard
4. Free tier: 1,000 searches/month

### Using the App

1. Open the app URL
2. (If auth enabled) Create account / Login
3. Enter your OpenAI and Tavily API keys
4. Click "Start Research"
5. Your keys are stored only in your browser session
6. When you close the browser, keys are cleared

---

## Monitoring & Costs

### User Costs (Important!)

Users pay for their own API usage:
- **OpenAI**: ~$0.01-0.10 per debate topic (depending on sources)
- **Tavily**: Free for 1,000 searches/month, then $0.005/search

### Your Costs (Hosting)

- **Streamlit Cloud**: Free tier available (1 GB RAM)
- **Heroku**: Free tier deprecated, ~$7/month for hobby plan
- **Cloud Run**: Pay per use, ~$5-10/month for light usage

---

## Troubleshooting

### "Authentication not configured" message

If you want to skip authentication:
- This is normal! Just click through to API key setup
- Users can still use the app without accounts

If you want authentication:
- Make sure `SUPABASE_URL` and `SUPABASE_ANON_KEY` are set
- Check secrets are properly configured in deployment platform

### "API key invalid" errors

- User should check their API keys are correct
- OpenAI: Verify key at platform.openai.com
- Tavily: Verify key at tavily.com dashboard
- Keys must have sufficient credits/quota

### App crashes or timeouts

- Increase server resources (RAM/CPU)
- Reduce `max_results` slider default value
- Reduce `sources_per_side` slider default value

---

## Files Structure

```
LangChain/
├── app_secure.py               # Main secure app (use this for deployment!)
├── orchestrator_secure.py      # Orchestrator with API key injection
├── agents_secure/              # Agents that accept API keys
│   ├── __init__.py
│   ├── query_generator.py
│   ├── search_retrieval.py
│   ├── source_validator.py
│   ├── analysis_classifier.py
│   ├── citation_formatter.py
│   └── vector_storage.py
├── .streamlit/
│   └── config.toml             # Streamlit configuration
├── requirements.txt            # Python dependencies
├── .env.example                # Example env file (safe to commit)
├── .gitignore                  # Don't commit .env!
└── README_DEPLOYMENT.md        # This file
```

---

## Quick Start Commands

### Local Testing:
```bash
pip install -r requirements.txt
streamlit run app_secure.py
```

### Streamlit Cloud:
1. Push to GitHub
2. Connect at share.streamlit.io
3. Deploy!

### Docker:
```bash
docker build -t debate-app .
docker run -p 8501:8501 debate-app
```

---

## Support

For issues or questions:
1. Check this deployment guide
2. Review README_MULTI_AGENT.md for architecture details
3. Open an issue on GitHub

---

**Remember**: This app is designed for PUBLIC deployment where USERS provide their own API keys. Never commit real API keys to your repository!
