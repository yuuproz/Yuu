# MeshYU Backend - Render Ready (Python, NOT Docker)

## This is the most convenient folder - just 2 files

Files:
- main.py (autofix backend V5)
- requirements.txt

## Deploy to Render (Fix your error)

Your error: "invalid local: resolve : lstat /opt/render/project/src/pip install -r requirements.txt"
Means you put Build Command in wrong field (Root Directory or Dockerfile).

### CORRECT WAY:

1. Go to https://dashboard.render.com
2. Click your service yuu-xcdp → Settings
3. Scroll to **Build & Deploy**

4. Set these EXACTLY:

   **Runtime:** Python 3 (NOT Docker)
   
   **Root Directory:** Leave EMPTY (or ./ ) - DO NOT put pip install here
   
   **Build Command:** 
   pip install -r requirements.txt
   
   **Start Command:**
   uvicorn main:app --host 0.0.0.0 --port $PORT

5. If you see "Docker Command" field → LEAVE IT EMPTY (that's for Docker only)

6. If your Runtime shows "Docker" → Change it to Python:
   - In Settings → Runtime → Select Python 3
   - Or create NEW Web Service → Choose Python (not Docker)

7. Click **Save Changes** → Manual Deploy → Deploy latest commit

8. Wait 1-2 min → Visit https://yuu-xcdp.onrender.com/api/health
   Should show: {"status":"ok","version":"5.0-autofix"}

## Test after deploy:
- https://yuu-xcdp.onrender.com/
- https://yuu-xcdp.onrender.com/api/info?url=https://www.tiktok.com/@khaby.lame/video/7194924129440967938
- Should return JSON with title, thumbnail

## If you want Docker (not recommended):
Use Dockerfile, then Build Command is empty, and Docker Command is:
uvicorn main:app --host 0.0.0.0 --port $PORT
