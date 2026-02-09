# Hosting Your Spotify Dashboard - Deployment Guide

## Quick Comparison

| Option | Difficulty | Cost | Best For |
|--------|-----------|------|----------|
| **Render** | ⭐ Easy | Free | Quick deployment, beginners |
| **Railway** | ⭐ Easy | Free tier | Fast setup, auto-deploy |
| **PythonAnywhere** | ⭐⭐ Medium | Free tier | Simple Python apps |
| **Heroku** | ⭐⭐ Medium | $5/month | Reliable hosting |
| **Vercel** | ⭐⭐⭐ Advanced | Free | Requires converting to serverless |

**Recommended: Render** (Easiest + Free)

---

## Option 1: Deploy to Render (RECOMMENDED - Free & Easy)

### Step 1: Prepare Your Code

Create a new file called `render.yaml` in your project:

```yaml
services:
  - type: web
    name: spotify-dashboard
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn spotify_dashboard:app
    envVars:
      - key: SPOTIFY_CLIENT_ID
        sync: false
      - key: SPOTIFY_CLIENT_SECRET
        sync: false
```

Add `gunicorn` to your `requirements.txt`:
```
flask>=2.3.0
requests>=2.31.0
gunicorn>=21.0.0
```

### Step 2: Push to GitHub

1. Go to [GitHub.com](https://github.com) and create a new repository
2. In your project folder, run:
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/spotify-dashboard.git
git push -u origin main
```

### Step 3: Deploy on Render

1. Go to [Render.com](https://render.com) and sign up (free)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Render will auto-detect your settings
5. Add environment variables:
   - `SPOTIFY_CLIENT_ID`: your_client_id
   - `SPOTIFY_CLIENT_SECRET`: your_client_secret
6. Click "Create Web Service"

**Done!** Your app will be live at: `https://your-app-name.onrender.com`

⚠️ Free tier sleeps after 15 min of inactivity (takes ~30 sec to wake up)

---

## Option 2: Deploy to Railway (Also Free & Easy)

### Step 1: Prepare Code

Create `Procfile` (no extension):
```
web: gunicorn spotify_dashboard:app
```

Add `gunicorn` to `requirements.txt`:
```
flask>=2.3.0
requests>=2.31.0
gunicorn>=21.0.0
```

### Step 2: Deploy

1. Go to [Railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Add environment variables in Settings:
   - `SPOTIFY_CLIENT_ID`
   - `SPOTIFY_CLIENT_SECRET`
6. Railway automatically deploys!

**URL:** `https://your-app.railway.app`

---

## Option 3: PythonAnywhere (Simple, No Git Required)

### Step 1: Sign Up
1. Go to [PythonAnywhere.com](https://www.pythonanywhere.com)
2. Create a free account

### Step 2: Upload Files
1. Go to "Files" tab
2. Upload your project files:
   - `spotify_dashboard.py`
   - `requirements.txt`
   - `templates/index.html`

### Step 3: Install Dependencies
1. Open a "Bash console"
2. Run:
```bash
pip install --user flask requests
```

### Step 4: Configure Web App
1. Go to "Web" tab
2. Click "Add a new web app"
3. Choose "Flask" and Python 3.10
4. Set source code path to your `spotify_dashboard.py`
5. In "WSGI configuration file", update:
```python
from spotify_dashboard import app as application
```

### Step 5: Set Environment Variables
1. In "Web" tab, scroll to "Environment variables"
2. Add:
   - `SPOTIFY_CLIENT_ID`
   - `SPOTIFY_CLIENT_SECRET`
3. Click "Reload" button

**URL:** `https://yourusername.pythonanywhere.com`

---

## Option 4: Quick Mobile Testing (Local Network)

Want to test on your phone RIGHT NOW without deploying?

### Step 1: Find Your Computer's IP

**Mac/Linux:**
```bash
ipconfig getifaddr en0
# or
hostname -I
```

**Windows:**
```cmd
ipconfig
# Look for "IPv4 Address" like 192.168.1.x
```

### Step 2: Update Flask App

Change the last line in `spotify_dashboard.py`:
```python
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

### Step 3: Run and Connect

1. Run: `python spotify_dashboard.py`
2. On your phone (connected to SAME WiFi):
   - Go to: `http://YOUR_IP_ADDRESS:5000`
   - Example: `http://192.168.1.5:5000`

⚠️ Only works on same WiFi network. Not accessible from internet.

---

## Option 5: Ngrok (Quick Public URL - Testing Only)

Perfect for quick sharing with friends!

### Step 1: Install Ngrok
```bash
# Mac
brew install ngrok

# Or download from https://ngrok.com
```

### Step 2: Run Your App
```bash
python spotify_dashboard.py
```

### Step 3: Create Public Tunnel
In a new terminal:
```bash
ngrok http 5000
```

You'll get a public URL like: `https://abc123.ngrok.io`

**Share this URL with friends!**

⚠️ Free URLs expire when you close ngrok. Not for permanent hosting.

---

## Recommended Setup Files for Deployment

### `.gitignore` (prevents committing secrets)
```
__pycache__/
*.pyc
.env
*.log
.DS_Store
```

### `runtime.txt` (for Render/Heroku)
```
python-3.11.0
```

### Modified `spotify_dashboard.py` (production-ready)

Add this at the top:
```python
import os

# Get port from environment (for cloud hosting)
PORT = int(os.environ.get('PORT', 5000))
```

Change the bottom:
```python
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)
```

---

## Security Tips for Public Hosting

1. **Never commit credentials to GitHub**
   - Always use environment variables
   - Add `.env` to `.gitignore`

2. **Add rate limiting** (optional but recommended)
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)
```

3. **Consider adding basic auth** if you want to restrict access
```python
from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

@auth.verify_password
def verify(username, password):
    if username == 'admin' and password == 'your_password':
        return True
    return False

@app.route('/')
@auth.login_required
def index():
    return render_template('index.html')
```

---

## My Recommendation

**For beginners:** Use **Render** or **Railway**
- Both are free
- Both work great with Flask
- Simple setup process
- Good for sharing with friends

**For quick testing:** Use **ngrok**
- Takes 2 minutes to setup
- Instant public URL
- Perfect for showing friends

**For mobile testing only:** Use **local network** method
- No internet required
- Instant
- Only works on your WiFi

Need help with any specific deployment method? Let me know!
