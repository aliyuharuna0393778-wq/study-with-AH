# Study with AH — Student Portal: Full Build & Hosting Guide

This document covers everything built and done, from the first version of the
portal to hosting it online. Keep this for reference.

---

## 1. What This Project Is

A student portal web app built with **Python (Flask)** and a **SQLite database**,
designed to run in Pydroid 3 on Android and also be hosted online for free.

### Folder structure (always required, exactly like this):

```
student_portal/
│
├── app.py
├── requirements.txt
├── Procfile
├── DEPLOY.md
│
├── templates/          (26 files — all .html pages)
│   ├── _student_header.html
│   ├── _student_footer.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── forgot_password.html
│   ├── reset_password.html
│   ├── contact.html
│   ├── notice_board.html
│   ├── student_results.html
│   ├── student_lessons.html
│   ├── student_assignments.html
│   ├── personal_data.html
│   ├── portal_help.html
│   ├── admin_login.html
│   ├── admin_students.html
│   ├── admin_reset_student.html
│   ├── admin_announcements.html
│   ├── admin_lessons.html
│   ├── admin_results.html
│   ├── admin_assignments.html
│   ├── admin_submissions.html
│   ├── admin_admins.html
│   ├── admin_profile.html
│   ├── admin_login_log.html
│   └── admin_restore.html
│
└── static/
    ├── style.css
    └── logo.jpg
```

**Rules that caused problems before, so always double-check:**
- `templates` and `static` must be spelled exactly that way, lowercase, **no trailing space** at the end of the folder name (this caused "TemplateNotFound" errors multiple times)
- Both folders sit directly next to `app.py` — never nested inside each other
- If you ever see `jinja2.exceptions.TemplateNotFound`, it always means a file is missing or a folder name has a typo/space — check the folder contents first

---

## 2. Features Built (in order)

1. **Basic registration & login** — students sign up with student ID, name, phone number, password
2. **Login without email** — matric number OR phone number + password (no Gmail/email anywhere)
3. **Forgot password** — verify identity with matric number + phone number, then set new password
4. **Contact page** — shows phone numbers and emails to reach the developer
5. **Multiple admins** — add/remove admin accounts, each with own username/password
6. **Admin can manage students directly** — reset any student's password, or remove their account
7. **Admin self-profile** — admin can change their own username/password (requires current password to confirm)
8. **Announcements (Notice Board)** — admin posts, students see them
9. **Lesson links (E-Learning)** — admin adds links to videos/materials, students view them
10. **Results & Grades** — admin enters scores per student; each student only sees their own
11. **Assignments** — admin posts assignments; students submit text/link answers; admin views submissions
12. **Login activity log** — records every login attempt (student & admin), success/fail, IP address, date/time
13. **Backup & Restore** — admin can download the whole database as a file, and restore from a backup later
14. **Sidebar layout redesign** — matches a full university portal style (header + collapsible sidebar + dashboard cards), same navy/gold color scheme
15. **Branding** — "Study with AH" logo and name throughout, "Developed by Aliyu Bn Haroon" credit

### Admin default login (change this immediately after setup):
```
Username: admin
Password: changeme123
```

---

## 3. Running It Locally in Pydroid 3

1. Install Flask via Pydroid 3's Pip menu
2. Open `app.py` from inside the correct folder (browse manually, don't rely on "Recent")
3. Tap ▶️ Run
4. Visit in Chrome: `http://127.0.0.1:5000`
5. If Pydroid was already running and you changed files, **fully stop and restart it** — it can cache old versions otherwise

---

## 4. Hosting on GitHub + Render (first hosting attempt)

### Step A — GitHub
1. Create a free account at github.com
2. Create a new **public** repository (e.g. `study-with-AH`)
3. Upload the 4 root files (`app.py`, `requirements.txt`, `Procfile`, `DEPLOY.md`) via "Add file → Upload files"
4. To upload into a subfolder that doesn't exist yet, type the folder name directly into the address bar:
   ```
   github.com/YOUR-USERNAME/YOUR-REPO/upload/main/templates
   ```
   Do the same for `static`. This trick creates the folder automatically.

### Step B — Render
1. Create a free account at render.com (sign up with GitHub — easiest)
2. Tap **New + → Web Service**
3. Connect your GitHub repo
4. Settings: Environment = Python 3, Build Command = `pip install -r requirements.txt`, Start Command = `gunicorn app:app`
5. Choose the **Free** instance
6. Tap **Create Web Service** and wait for it to build

### ⚠️ Known problem with Render (why we moved away from it)
Render's **free tier does not keep files permanently**. Every time the site goes
to sleep from inactivity and wakes back up, the `students.db` file resets to
empty — all registered students, announcements, results, etc. disappear. This
is a limitation of Render's free plan, not a bug in the code.

### Important code fix needed for Render/gunicorn hosting
The database only initializes correctly if `init_db()` is called outside the
`if __name__ == "__main__":` block in `app.py`, like this:
```python
init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
```
Without this, gunicorn (used by Render) never creates the database tables.

---

## 5. Hosting on PythonAnywhere (final, working, permanent-storage hosting)

Switched to PythonAnywhere because its free tier has **real, permanent file
storage** — no more data disappearing.

### Steps:
1. Create a free "Beginner" account at pythonanywhere.com — choose your username carefully, since it becomes part of your site's address
2. Go to **Files**, create a new directory: `student_portal`
3. Upload the 4 root files one at a time (no multi-select on PythonAnywhere)
4. Create a `templates` directory inside it, upload all 26 `.html` files
5. Create a `static` directory inside it, upload `style.css` and `logo.jpg`
6. Go to the **Web** tab → **Add a new web app**
7. Choose **Manual configuration** (not the Flask quick-setup)
8. Choose Python 3.10 (or closest available)
9. Fill in:
   - **Source code:** `/home/YOUR-USERNAME/student_portal`
   - **Static files — URL:** `/static/`
   - **Static files — Directory:** `/home/YOUR-USERNAME/student_portal/static`
10. Edit the **WSGI configuration file** — delete everything in it, replace with:
    ```python
    import sys
    path = '/home/YOUR-USERNAME/student_portal'
    if path not in sys.path:
        sys.path.append(path)

    from app import app as application
    ```
11. Save the WSGI file
12. Tap the green **Reload** button on the Web tab

### Your live site:
```
https://YOUR-USERNAME.pythonanywhere.com
```

### ⚠️ Free plan reminder
PythonAnywhere's free tier requires logging in **once a month** and tapping
**"Run until 1 month from today"**, or the site gets disabled. Set yourself a
monthly reminder for this.

### Useful troubleshooting tool: the Bash console
From the **Consoles** tab, opening a Bash console lets you run commands like:
```bash
ls -la ~/student_portal
ls -la ~/student_portal/static/
ls -la ~/student_portal/templates/ | cat -A
```
`cat -A` shows a `$` at the very end of each line, which helps catch invisible
trailing spaces in folder/file names — a repeated cause of errors in this project.

---

## 6. Live Links (Current)

**Student Portal:**
```
https://YOUR-USERNAME.pythonanywhere.com/login
```

**Admin Portal:**
```
https://YOUR-USERNAME.pythonanywhere.com/admin/login
```

---

## 7. Known Unresolved Issue (as of this guide)

On the PythonAnywhere-hosted version, the `/login` and dashboard pages are
loading **without their CSS styling** (looks like plain unstyled HTML, huge
logo, default purple/blue links) even though:
- The static file mapping is set up correctly
- `style.css` loads perfectly when visited directly at `/static/style.css`
- The admin pages (`/admin/login`) load with full, correct styling
- The HTML `<link rel="stylesheet">` tag is coded identically on every page — confirmed by checking the source code directly

This points to a caching or timing issue on PythonAnywhere's side rather than
a code problem, but it was not fully resolved in this session. **Next steps to
try when revisiting this:**
1. View the raw page source (`view-source:` prefix in Chrome) on `/login` and
   compare the exact `<link>` tag URL against the one on `/admin/login`
2. Try reloading the web app multiple times with a few minutes' gap between each
3. Try clearing Chrome's cache completely (Settings → Privacy → Clear browsing data)
4. Check the **Error log** and **Server log** links on the Web tab for any
   clues logged at the time `/login` is requested

---

## 8. General Lessons Learned

- **Trailing spaces in folder names** are invisible on screen but break
  everything — caused the exact same "TemplateNotFound" error multiple times.
  Always check by renaming and looking closely at the very end of the text, or
  use `ls -la | cat -A` in a Bash console to be 100% sure.
- **A zip file is only as good as what's actually inside it** — always verify
  contents after zipping/uploading, don't assume.
- **Restarting the server fully** (not just refreshing the browser) is often
  needed after changing files, especially in Pydroid 3.
- **Free hosting always has a tradeoff** — Render sleeps and loses data;
  PythonAnywhere stays permanent but needs a monthly check-in and has a small
  traffic/CPU limit on the free tier.
