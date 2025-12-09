# 🚂 Railway Deployment Guide

Complete guide to deploy the Financial Analysis System on Railway.

---

## 🎯 Quick Deploy

### **Option 1: Deploy from GitHub (Recommended)**

1. **Go to Railway:** https://railway.app/
2. **Click "New Project"**
3. **Select "Deploy from GitHub repo"**
4. **Choose:** `nickm538/financial-analysis-system`
5. **Railway will automatically:**
   - Detect the `railway.json` configuration
   - Install dependencies from `requirements.txt`
   - Run the Streamlit app using the `Procfile`

### **Option 2: Deploy with Railway CLI**

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Initialize project
railway init

# Link to GitHub repo
railway link

# Deploy
railway up
```

---

## 🔧 Configuration

### **Environment Variables**

Railway will need these API keys. Add them in the Railway dashboard:

1. Go to your project in Railway
2. Click on "Variables" tab
3. Add the following:

```
ALPHAVANTAGE_API_KEY=your_key_here
FINNHUB_API_KEY=your_key_here
MASSIVE_API_KEY=your_key_here
```

**Get Free API Keys:**
- [AlphaVantage](https://www.alphavantage.co/support/#api-key)
- [Finnhub](https://finnhub.io/register)
- [Massive API](https://massive.io/)

**Note:** TwelveData API key is hardcoded in `twelvedata_client.py` (default: `5e7a5daaf41d46a8966963106ebef210`)

---

## 📦 Deployment Files

Railway deployment uses these files:

### **1. railway.json**
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "streamlit run streamlit_dashboard_PRODUCTION_FIXED.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### **2. Procfile**
```
web: streamlit run streamlit_dashboard_PRODUCTION_FIXED.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true
```

### **3. .streamlit/config.toml**
Streamlit configuration for production deployment.

### **4. start.sh**
Alternative startup script (executable).

### **5. requirements.txt**
All Python dependencies including Streamlit.

---

## 🚀 Deployment Process

### **Step-by-Step**

1. **Connect GitHub Repository**
   - Railway → New Project → Deploy from GitHub
   - Select `nickm538/financial-analysis-system`

2. **Railway Auto-Detects:**
   - ✅ Python project
   - ✅ `requirements.txt` for dependencies
   - ✅ `railway.json` for configuration
   - ✅ `Procfile` for start command

3. **Add Environment Variables**
   - Go to Variables tab
   - Add API keys (see Configuration section)

4. **Deploy**
   - Railway automatically builds and deploys
   - Wait for build to complete (~2-3 minutes)

5. **Access Your App**
   - Railway provides a public URL
   - Example: `https://financial-analysis-system-production.up.railway.app`

---

## 🔍 Troubleshooting

### **Issue: Build Fails**

**Error:** `No module named 'streamlit'`

**Solution:** Ensure `requirements.txt` includes all dependencies:
```
streamlit>=1.28.0
pandas>=2.0.0
numpy>=1.24.0
requests>=2.31.0
python-dotenv>=1.0.0
plotly>=5.17.0
matplotlib>=3.7.0
cachetools>=5.3.0
```

---

### **Issue: App Crashes on Start**

**Error:** `Address already in use`

**Solution:** Railway automatically sets `$PORT`. The `Procfile` uses it:
```
web: streamlit run streamlit_dashboard_PRODUCTION_FIXED.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true
```

---

### **Issue: API Keys Not Working**

**Error:** `Error loading fundamentals: API key missing`

**Solution:** Add environment variables in Railway dashboard:
1. Go to project → Variables
2. Add `ALPHAVANTAGE_API_KEY`, `FINNHUB_API_KEY`, `MASSIVE_API_KEY`
3. Redeploy

---

### **Issue: Slow Performance**

**Cause:** Free tier limitations

**Solution:**
1. **Upgrade Railway plan** for more resources
2. **Optimize caching** - Already implemented (5-minute TTL)
3. **Reduce API calls** - Rate limiting already in place

---

## 📊 Railway Dashboard

### **Monitoring**

Railway provides:
- **Logs:** Real-time application logs
- **Metrics:** CPU, Memory, Network usage
- **Deployments:** History of all deployments
- **Environment:** Manage environment variables

### **Accessing Logs**

1. Go to your project in Railway
2. Click on "Deployments"
3. Select latest deployment
4. View logs in real-time

---

## 💰 Pricing

### **Railway Free Tier**
- $5 free credit per month
- Enough for ~500 hours of runtime
- Perfect for testing and development

### **Pro Plan**
- $20/month
- More resources
- Better performance
- Custom domains

---

## 🔗 Useful Links

- **Railway Dashboard:** https://railway.app/dashboard
- **Railway Docs:** https://docs.railway.app/
- **GitHub Repo:** https://github.com/nickm538/financial-analysis-system
- **Railway CLI:** https://docs.railway.app/develop/cli

---

## ✅ Deployment Checklist

Before deploying, ensure:

- [x] GitHub repository is public or connected to Railway
- [x] `railway.json` is in project root
- [x] `Procfile` is in project root
- [x] `requirements.txt` includes all dependencies
- [x] `.streamlit/config.toml` exists
- [x] Environment variables are ready (API keys)
- [x] All Python files are committed to GitHub

---

## 🎯 Expected Result

After successful deployment:

1. ✅ Railway builds the project
2. ✅ Installs all dependencies
3. ✅ Starts Streamlit on assigned port
4. ✅ Provides public URL
5. ✅ App is accessible worldwide

**Example URL:** `https://financial-analysis-system-production.up.railway.app`

---

## 🔄 Continuous Deployment

Railway automatically redeploys when you push to GitHub:

```bash
# Make changes locally
git add .
git commit -m "Update feature"
git push origin main

# Railway automatically detects push and redeploys
```

---

## 🛡️ Security

### **Environment Variables**

✅ **DO:**
- Store API keys in Railway environment variables
- Use `.env.example` as template
- Never commit `.env` to GitHub

❌ **DON'T:**
- Hardcode API keys in Python files
- Commit sensitive data to GitHub
- Share API keys publicly

---

## 📝 Post-Deployment

### **Test Your Deployment**

1. **Access the URL** Railway provides
2. **Enter a stock symbol** (e.g., AAPL)
3. **Check all tabs:**
   - AI Summary
   - Comprehensive Fundamentals
   - Technical Analysis
   - Comprehensive Scoring
4. **Verify metrics load** correctly
5. **Check console logs** in Railway dashboard

---

## 🎉 Success!

Your Financial Analysis System is now live on Railway! 🚀

**Share your deployment:**
- Copy the Railway URL
- Share with users
- Monitor usage in Railway dashboard

---

**Need help?** Open an issue on GitHub: https://github.com/nickm538/financial-analysis-system/issues
