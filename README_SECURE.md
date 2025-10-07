# Secure Debate Research Assistant

## 🔒 Security-First Public Deployment

Your app is now ready for **PUBLIC deployment** with these security features:

### ✅ Key Security Features

1. **User-Provided API Keys**
   - No API keys stored on server
   - Users enter their own OpenAI + Tavily keys
   - Keys stored ONLY in browser session memory
   - Auto-cleared when browser closes

2. **Optional Authentication**
   - Supabase integration for user accounts
   - Works without auth if not configured
   - Auth controls access, NOT API key storage

3. **No Data Persistence**
   - API keys never saved to disk
   - No logging of sensitive data
   - Vector DB stores only research results (no keys)

---

## 🚀 Quick Start

### Running Locally

**Secure Version (for public deployment):**
```bash
streamlit run app_secure.py
```
Now open: **http://localhost:8503**

**Original Version (for local use with .env):**
```bash
streamlit run app.py
```
Now open: **http://localhost:8502**

---

## 📁 Project Structure

```
LangChain/
├── app_secure.py              ⭐ USE THIS for public deployment
├── orchestrator_secure.py     ⭐ Secure orchestrator (API key injection)
├── agents_secure/             ⭐ Secure agents (accept API keys as params)
│
├── app.py                     🔧 Original (uses .env, local only)
├── orchestrator.py            🔧 Original orchestrator
├── agents/                    🔧 Original agents
│
├── README_DEPLOYMENT.md       📖 Full deployment guide
├── README_SECURE.md          📖 This file
├── README_MULTI_AGENT.md     📖 Architecture overview
│
├── .env.example              ✅ Safe to commit
├── .gitignore                ✅ Excludes .env
└── requirements.txt          ✅ All dependencies
```

---

## 🔑 How It Works

### User Flow

1. **Visit App URL**
2. **(Optional) Login** with Supabase account
3. **Enter API Keys:**
   - OpenAI API key
   - Tavily API key
4. **Start researching!**
5. **Close browser** → keys automatically cleared

### Developer Flow

1. **Deploy app** to Streamlit Cloud / Heroku / Cloud Run
2. **(Optional) Configure Supabase** for authentication
3. **Share link** with users
4. **Users provide their own API keys** → no cost to you!

---

## 💰 Cost Model

### Your Costs (Hosting)
- **Streamlit Cloud:** FREE tier available
- **Heroku:** ~$7/month
- **Cloud Run:** ~$5-10/month

### User Costs (API Usage)
- **OpenAI:** ~$0.01-0.10 per research topic
- **Tavily:** FREE for 1,000 searches/month

**Key Benefit:** Users pay for their own API usage!

---

## 🔐 Authentication Setup (Optional)

### To Enable Authentication:

1. **Create Supabase project:**
   - Go to [supabase.com](https://supabase.com)
   - Create new project
   - Copy URL and anon key

2. **Set environment variables:**

   **Streamlit Cloud:**
   ```toml
   # App Settings → Secrets
   SUPABASE_URL = "https://xxx.supabase.co"
   SUPABASE_ANON_KEY = "your-anon-key"
   ```

   **Local Testing:**
   ```bash
   # Create .env file
   echo 'SUPABASE_URL="https://xxx.supabase.co"' >> .env
   echo 'SUPABASE_ANON_KEY="your-anon-key"' >> .env
   ```

3. **Restart app** - authentication will now be required!

### To Disable Authentication:

Simply don't set `SUPABASE_URL` and `SUPABASE_ANON_KEY`. The app will skip auth and go straight to API key configuration.

---

## 📦 Deployment

### Streamlit Cloud (Easiest)

1. Push to GitHub:
   ```bash
   git init
   git add .
   git commit -m "Secure debate research app"
   git push -u origin main
   ```

2. Deploy at [share.streamlit.io](https://share.streamlit.io)
   - Main file: `app_secure.py`
   - Python version: 3.10

3. **(Optional) Add Supabase secrets** in App Settings

4. **Done!** Share your URL

### Other Platforms

See `README_DEPLOYMENT.md` for:
- Heroku deployment
- Docker + Cloud Run
- AWS ECS
- Full configuration guides

---

## 🧪 Testing the Secure App

### Local Test (No Auth)

```bash
# No Supabase configured
streamlit run app_secure.py
```

You'll see:
1. "Authentication not configured" → Click through
2. Enter test API keys
3. Start researching!

### Local Test (With Auth)

```bash
# Set Supabase env vars in .env
SUPABASE_URL="https://xxx.supabase.co"
SUPABASE_ANON_KEY="your-key"

streamlit run app_secure.py
```

You'll see:
1. Login / Register tabs
2. Create account → verify email
3. Login → Enter API keys
4. Start researching!

---

## 📋 User Instructions

Share these with your users:

### Getting API Keys

**OpenAI:**
1. Visit [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Create account + add billing
3. Create API key
4. Copy it (you won't see it again!)

**Tavily:**
1. Visit [tavily.com](https://tavily.com)
2. Sign up (free!)
3. Copy API key from dashboard
4. Free tier: 1,000 searches/month

### Using the App

1. Open the app URL
2. Create account (if auth enabled) or skip
3. Enter your API keys
4. Click "Start Research"
5. Your keys are safe - stored only in browser!

---

## 🛡️ Security Checklist

Before deploying publicly:

- [x] Using `app_secure.py` (not `app.py`)
- [x] `.env` in `.gitignore`
- [x] Only `.env.example` committed (no real keys)
- [x] Users provide their own API keys
- [x] Keys stored in session state only
- [x] No API keys logged or persisted
- [ ] (Optional) Supabase auth configured
- [ ] Repository is public (or private if preferred)
- [ ] README with user instructions

---

## 🔧 Troubleshooting

**"ModuleNotFoundError: No module named 'agents_secure'"**
- Make sure you're running `app_secure.py` (not `app.py`)
- The secure version uses `agents_secure/` directory

**"Authentication failed"**
- Check `SUPABASE_URL` and `SUPABASE_ANON_KEY` are set correctly
- Verify user confirmed email address
- Or disable auth by removing Supabase env vars

**"Invalid API key"**
- User should verify their OpenAI/Tavily keys
- Check keys have sufficient credits/quota

---

## 🎯 What's Different from Original?

| Feature | `app.py` (Original) | `app_secure.py` (Secure) |
|---------|-------------------|------------------------|
| API Keys | From `.env` file | User-provided in UI |
| Deployment | Local only | Public-ready |
| Authentication | None | Optional Supabase |
| Cost Model | Your API cost | Users pay API cost |
| Security | Keys in .env | Keys in session only |

---

## 📚 Related Documentation

- **README_DEPLOYMENT.md** - Complete deployment guide
- **README_MULTI_AGENT.md** - Architecture & how agents work
- **README_SECURE.md** - This file (security overview)

---

## ✅ Ready to Deploy!

Your app is now configured for secure public deployment:

1. ✅ API keys are user-provided
2. ✅ Optional authentication ready
3. ✅ Deployment configs created
4. ✅ Security best practices implemented
5. ✅ Cost passed to users

**Next Steps:**
1. Test locally: `streamlit run app_secure.py`
2. Push to GitHub
3. Deploy to Streamlit Cloud
4. Share with users!

🎉 You're all set!
