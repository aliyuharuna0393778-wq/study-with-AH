# Putting Study with AH Online (Free Hosting)

Right now the site only works on your own phone at 127.0.0.1 — nobody else
can reach it. To let other students access it from anywhere, host it on
Render (free tier, easiest option).

## Steps (using Render.com)

1. Create a free account at https://render.com

2. Put your `student_portal` folder into a GitHub repository:
   - Create a free GitHub account if you don't have one (github.com)
   - Create a new repository, e.g. "study-with-ah"
   - Upload all the files: app.py, templates/, static/, requirements.txt, Procfile
     (You can do this from the GitHub website's "Add file > Upload files" —
     no computer needed, works from your phone browser)

3. On Render:
   - Click "New +" > "Web Service"
   - Connect your GitHub repo
   - Settings:
     - Environment: Python 3
     - Build Command: pip install -r requirements.txt
     - Start Command: gunicorn app:app
   - Click "Create Web Service"

4. Render will give you a live URL like:
   https://study-with-ah.onrender.com
   This works from any phone, anywhere — not just yours.

## Important before going live

1. **Change the secret key** in app.py — replace
   "change-this-to-a-random-secret-key" with a long random string.

2. **Change the admin password** in app.py — replace "changeme123"
   with something only you know.

3. **Database note**: Render's free tier does not keep files permanently —
   your SQLite database (students.db) may reset when the service restarts
   or redeploys. For a real, permanent student database, you'd want to
   upgrade to a persistent disk on Render, or use a hosted database like
   Render's free PostgreSQL. Ask me if you want help switching to that —
   it's a bigger change than what's needed to get you online today.

4. Turn off debug mode for production — in app.py, change:
   app.run(host="0.0.0.0", port=5000, debug=True)
   to:
   app.run(host="0.0.0.0", port=5000, debug=False)
   (Not strictly needed with gunicorn/Render, but good practice.)
