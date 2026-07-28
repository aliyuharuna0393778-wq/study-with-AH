# Study with AH — Complete Step-by-Step Journey (Everything We Did)

This is a full record of every step taken from the very beginning to now,
explained in order, with the reasoning behind each one. Read this top to
bottom to relearn the whole process yourself.

---

## PHASE 1 — Designing the Login Form

**Step 1.1 — First request**
You asked for a login form for university students to enter their details.

**What I built:** A single HTML file (`student-login.html`) with a styled
sign-in form — fields for Student ID, University Email, Password — using a
navy blue and gold color scheme to feel like a real institution. At this
stage it was just the *visual* form. It didn't save data anywhere yet; tapping
"Sign In" only checked that the fields weren't empty (client-side validation).

**Why:** You need to see and approve the *look* of something before building
the harder, invisible backend logic behind it.

**Step 1.2 — You couldn't view it**
You said "I try to view it but I found nothing inside."

**What I did:** Checked the file wasn't empty on my end (it wasn't — confirmed
310 lines, 7.6KB). Explained that opening an HTML file requires a **browser**
app (like Chrome), not a text editor or Pydroid 3, and that tapping the file
link in our chat should open a preview.

**Why this matters:** HTML files are code — they only "look like a form" when
a browser reads and renders them. Opening them any other way just shows raw text.

**Step 1.3 — You confirmed it worked in Chrome**
You opened it successfully in Chrome and could see the form.

---

## PHASE 2 — Building the Real Backend (Flask + SQLite)

**Step 2.1 — You asked for the backend**
You wanted the form to actually work — real accounts, real login checking.

**What I built:** A Python **Flask** application (`app.py`) plus a **SQLite
database** (`students.db`, created automatically). This included:
- `/register` — creates a new student account, storing a securely **hashed**
  password (never the real password in plain text)
- `/login` — checks student ID + email + password against the database
- `/dashboard` — a page only reachable after logging in
- `/logout`

I chose Flask because it's Python (matches your existing pygame/Pydroid 3
experience) and can run directly inside Pydroid 3 for testing.

**Why hashed passwords matter:** if anyone ever saw the database file, they
still couldn't read anyone's actual password — only a scrambled, one-way version.

**Step 2.2 — Folder structure explained**
I explained Flask requires a specific folder layout to find its pages:
```
student_portal/
├── app.py
├── templates/   ← all .html pages Flask displays
└── static/      ← CSS, images
```
This structure is **mandatory** — Flask automatically looks for a folder
named exactly `templates` sitting right next to `app.py`. This rule caused
several errors later, explained below.

**Step 2.3 — Step-by-step instructions to run it in Pydroid 3**
1. Download all files, arrange in the folder structure above
2. Open Pydroid 3 → Pip menu → install `flask`
3. Open `app.py` → tap ▶️ Run
4. Open Chrome → go to `http://127.0.0.1:5000`

**Why `127.0.0.1`:** this is a special address meaning "this same device" —
since Flask was running locally inside Pydroid 3 on your phone, your phone's
own browser could reach it at that address, but no other device could.

---

## PHASE 3 — First Round of Errors (Learning the Folder Rules)

**Screenshot 6882.jpg** — showed Flask's startup message: *"Serving Flask
app... Running on http://127.0.0.1:5000"*. This confirmed Flask itself
started correctly, no errors yet.

**Screenshot 6883.jpg** — showed your first real error:
`jinja2.exceptions.TemplateNotFound: login.html`

**Why this happened:** Flask looks for `templates/login.html`. This error
means it searched and didn't find it — either the file was missing, or the
`templates` folder wasn't positioned correctly.

**Screenshot 6886.jpg** — you sent a screenshot of your file manager. This
revealed the real problem: your `static` and `templates` folders were sitting
**outside** the `student portal` folder, as siblings to it — not inside it.
Since `app.py` was inside `student portal`, it couldn't see folders sitting
next to that outer folder.

**The fix:** move `templates` and `static` folders to sit directly inside
`student portal`, alongside `app.py`.

**Screenshots 6953.jpg and 6954.jpg** — after the fix, these showed a
successful registration and a working dashboard reading "Welcome, Aliyu
Haruna" with your student ID "PSC/2025/41127" — confirming the fix worked
completely.

---

## PHASE 4 — Adding the First Batch of Features

**Step 4.1 — You asked to proceed with 4 things**
You wanted: (1) an admin view, (2) forgot password, (3) real hosting, (4)
branding/style improvements. I asked which first; you said "I need all of them."

**Step 4.2 — Branding: you shared your logo**
You uploaded an image of your "STUDY with AH" logo (a brain/lightbulb design
with an open book). I saved this as `static/logo.jpg` and set the site's name
to "Study with AH" throughout every page, replacing a placeholder "UN" circle.

**Step 4.3 — What was built:**
- **Admin panel** — a separate login (`/admin/login`) with its own username/password, completely apart from student accounts, so only you could manage the site
- **Forgot password** — a student proves their identity, then sets a new password themselves
- **Hosting preparation files** — `requirements.txt` (list of what the site needs installed), `Procfile` (tells a hosting service how to start the app), and `DEPLOY.md` (a written guide for hosting later)

**Why a separate admin login:** keeping admin access completely separate from
student accounts is a basic security principle — a student account being
compromised should never accidentally grant admin powers.

---

## PHASE 5 — Multi-Admin, Announcements, and Lessons

**Step 5.1 — You asked how to add content, and about multiple admins**
Two separate needs: letting you *post things* students would see, and letting
*other people* help manage the site as admins too.

**Step 5.2 — I asked what kind of content**
You chose: announcements/notices, and links to lessons/videos.

**Step 5.3 — What was built:**
- **Multiple admins** — instead of one hardcoded admin, admins became their
  own database table. Anyone with an admin account could add more admin
  accounts (with a username + password), or remove one (except themselves,
  and never the very last admin — so you could never accidentally lock
  yourself out completely).
- **Announcements** — admin writes a title + message, saved to the database;
  every student sees it on their dashboard.
- **Lesson links** — admin adds a title, a link (e.g. YouTube), and an
  optional description; students see a list they can tap to open.

---

## PHASE 6 — Admin Self-Management (Logout, Profile, Student Control)

**Step 6.1 — You said admin couldn't log out, edit their own profile, or
reset a student's password**

I tested all three directly by writing and running test code. Two of them
(**logout** and **resetting a student's password**) already worked correctly
— they'd been built earlier. But you were right about one real gap: **there
was genuinely no way for an admin to change their own username/password.**

**Step 6.2 — What was built:** a new **"My Profile"** page in the admin
panel. It requires typing your **current password** before allowing any
change — this stops someone who finds an unlocked/logged-in device from
hijacking the account by just changing the password.

---

## PHASE 7 — Removing Email, Adding Phone-Based Login

**Step 7.1 — You reminded me: no Gmail/email for login, ever**
This was a firm requirement stated more than once.

**Step 7.2 — What was changed:**
- Registration now asks for: matric number, full name, **phone number**,
  password — no email field anywhere
- Login now accepts **either matric number or phone number**, plus password
- Forgot password now verifies identity using matric number + phone number

**Step 7.3 — Two more features added at the same time:**
- **Login Activity Log** — every login attempt (student or admin), whether
  it succeeded or failed, gets recorded with the date, time, and the visitor's
  IP address. This lets you spot suspicious repeated failed attempts.
- **Backup & Restore** — a button to download your entire database as a
  single file (a safety copy), and a way to upload that file later to restore
  everything if something ever goes wrong.

**Why this required deleting the database:** Since the *structure* of the
students table changed (email column removed, phone number column added),
the old `students.db` file was no longer compatible and had to be rebuilt
fresh, meaning any previously registered test accounts were lost.

---

## PHASE 8 — Files Going Missing (The Zip Investigation)

**Screenshots 8420.jpg / 8510.jpg** — you ran the app after building a new
folder ("My real portal") and got the exact same `TemplateNotFound: login.html`
error again.

**Screenshot 8543.jpg** — your file manager screenshot this time showed
`templates` correctly sitting inside `student portal`, which itself sat
inside "My real portal" — visually, everything looked right.

**The hidden problem:** I asked you to zip the whole folder and upload it
(`My_real_portal_.zip`) so I could inspect it directly myself. Extracting it
revealed the real issue: your folder names had **invisible trailing spaces**
— e.g. the folder was actually named `"templates "` (with a space at the very
end) instead of `"templates"`. Since this space doesn't show visually on a
phone screen, it looked correct but wasn't.

**Why this breaks things:** Flask looks for a folder named *exactly*
`templates` — character for character. A trailing space makes it a
technically different name, so Flask can't find it, even though it's sitting
right there.

**The fix:** renaming both folders, carefully deleting the invisible space
at the very end of each name.

---

## PHASE 9 — The Corrupted Logo

**Screenshots 8576/8575/8574.jpg** — you showed me the portal running nicely
now (login page, dashboard, contact page) — but the logo circle showed a
small broken-image icon instead of your actual picture.

**Investigation:** I inspected the actual `logo.jpg` file from your zip using
low-level file tools. Its very first bytes should have started with a JPEG
signature — instead they showed a pattern (`ef bf bd` repeated) that's the
telltale sign of a file being accidentally passed through a text-encoding
step that corrupts binary image data. This most likely happened somewhere in
the phone's zip/transfer process.

**The fix:** Since my original saved copy of your logo was still intact and
untouched, I just re-shared that clean copy directly, and you replaced the
corrupted one.

---

## PHASE 10 — Accessing the Admin Portal

You asked how to reach the admin section. I gave you the direct address:
```
127.0.0.1:5000/admin/login
```
with the default login (`admin` / `changeme123`), and reminded you to change
that password immediately once inside, via the new "My Profile" page.

---

## PHASE 11 — Studying FUDMA's Real Portal, Then a Full Redesign

**Screenshots 8839/8833/8844.jpg** — you sent screenshots of Federal
University Dutsin-Ma's actual student portal (your real school account) —
showing its dashboard cards, left sidebar menu (Course Registration, Results,
Personal Data, etc.), notice board, and overall layout style.

**Step 11.1 — You asked for your portal to look "exactly" like this, with
only the colors changed, plus new free features**

**What was rebuilt:**
- **Layout redesign** — added a top header bar (logo, school name, student
  info, logout) and a left sidebar navigation, matching FUDMA's structure,
  but kept your existing navy-and-gold color scheme instead of copying theirs.
  On phone screens, the sidebar collapses behind a ☰ menu button since a
  permanent sidebar doesn't fit a narrow screen.
- **New pages added**, each needing a new database table:
  - **Notice Board** — a dedicated page for all announcements
  - **Results & Grades** — admin enters a student's course score/grade;
    each student sees only their own results, never anyone else's
  - **Assignments** — admin posts an assignment (title, description, due
    date, optional link); students submit either written text or a link as
    their answer; admin can view every submission per assignment
  - **My Personal Data** — a student's own registered details displayed
    back to them (name, matric number, phone, registration date)
  - **Portal Help** — a static page explaining how to use the site

**Why rebuild the whole layout instead of just adding pages:** for the new
pages to feel like one consistent portal (not a patchwork of different
styles), every student page needed to share the same header/sidebar. I built
this as two reusable template pieces (`_student_header.html` and
`_student_footer.html`) that every other student page "includes," so a
change to the sidebar only needs to happen in one place, not copy-pasted
across a dozen files.

---

## PHASE 12 — Re-Organizing Into a Brand New Project Folder

You decided to build this newest version as a completely separate project
rather than editing your existing one, to avoid mixing old and new files.

**Step 12.1 — I gave you the full folder map** listing all 31 files and
exactly which subfolder each belongs in.

**Step 12.2 — You asked which files to delete vs keep** — I explained the
difference between brand-new files, changed files, and untouched files, but
recommended just replacing everything wholesale since mixing versions was
the root cause of repeated errors so far.

**Step 12.3 — I resent all 31 files** in two batches so you had a clean,
complete, current set to work from without hunting through old messages.

---

## PHASE 13 — More TemplateNotFound Errors, and the Admin Files Going Missing

**Screenshot 9207.jpg / 9208.jpg** — even after rebuilding the folder, you
hit `TemplateNotFound: admin_login.html` again. Your file manager screenshot
this time showed the file genuinely sitting there correctly named.

This time the cause was different: **Pydroid 3 itself was still running an
old cached copy** of the app from before the files were updated — simply
refreshing the browser doesn't force Pydroid to reload changed files. The fix
was to fully **stop the server, close Pydroid 3 completely (swipe it away
from recent apps), reopen it, and manually browse to the correct `app.py`
file** rather than trusting "Recent."

**Step 13.2 — the same error returned once more**, and this time you sent a
zip of the whole project (`Real_student_portal.zip`) for direct inspection.

**What I found this time:** genuinely different from before — **none of your
12 `admin_*.html` files existed anywhere in the zip at all.** Not a naming
issue, not a folder issue — they were simply never saved into the `templates`
folder in the first place, even though an earlier screenshot had shown them
there (likely from a different folder attempt).

**The fix:** rather than asking you to download 12 separate files one at a
time (error-prone on mobile), I packaged all 12 admin templates into a single
`admin_templates.zip` file, so you could extract them all into `templates` in
one action.

**Step 13.3 — you confirmed all 12 files were present** (screenshot 9208.jpg),
but the error still happened. Once again, this turned out to be Pydroid 3
running a stale cached process — **fully closing and reopening Pydroid 3
fixed it for good.**

---

## PHASE 14 — Admin Profile Feature, Round Two

You separately asked about the exact same admin logout/edit-profile/reset
concern raised back in Phase 6. I re-confirmed the code was correct (logout
and reset-password both worked in direct testing), and re-shared all 12
current `admin_*.html` files together as one complete, verified batch to
eliminate any lingering mismatch from your file replacements.

---

## PHASE 15 — Hosting Online: GitHub + Render (First Attempt)

**Why hosting was needed:** until this point, the site only worked at
`127.0.0.1` — meaning only *your own phone* could ever reach it. No other
student could register or log in from their own device. Hosting puts the
code on a server anyone can reach via a real internet address.

**Step 15.1 — a required code fix before hosting**
I found that `init_db()` (the function that creates the database tables) was
written to only run when *you* directly ran `app.py` yourself. Hosting
services use a different tool called `gunicorn` to start the app, which never
triggers that specific line — meaning the database would never get created
on a live host. Fixed by moving that line so it always runs, regardless of
how the app starts.

**Step 15.2 — Creating a GitHub account and repository**
GitHub is a free place to store your code online, which Render (the hosting
service) then reads from. You created an account, then a new public
repository named `study-with-AH`.

**Step 15.3 — Uploading files to GitHub, folder by folder**
Multi-file upload on mobile doesn't let you create new folders directly by
picking files — so I taught you a trick: typing a special web address
directly into Chrome, like:
```
github.com/YOUR-USERNAME/YOUR-REPO/upload/main/templates
```
Visiting this exact address opens an upload page that automatically creates
a `templates` folder and puts every file you upload there inside it — even
though the folder didn't exist a moment before. You did this once for the 4
root files (no folder needed), once for `templates`, and once for `static`.

**Step 15.4 — Verifying the upload**
You sent screenshots of the `templates` folder listing on GitHub; I compared
it character-by-character against my own local list of 26 expected files and
confirmed every single one matched — nothing missing.

**Step 15.5 — Creating a Render account and web service**
Render reads directly from your GitHub repository. You signed up (using
GitHub login, the fastest option), then created a **New Web Service**,
connected it to your `study-with-AH` repo. Render automatically detected the
correct Build Command (`pip install -r requirements.txt`) and Start Command
(`gunicorn app:app`) from your `Procfile` and `requirements.txt` — you didn't
need to type these manually.

**Step 15.6 — Region question**
You asked if "Oregon (US West)" was correct. I explained this only affects
physical server location/tiny latency differences, not functionality — fine
to leave as-is since Render has no African region anyway.

**Step 15.7 — Deployment succeeded**
Screenshot 9239.jpg showed "study-with-AH is live!" — your first real, public
web address: `study-with-ah.onrender.com`.

**Step 15.8 — "Not Found" error immediately after**
You visited the link and got a "Not Found" page. I asked you to check
Render's logs (which showed the service was actually running fine — "All
services are up and running"), then guided you to tap the **exact link Render
itself provided** rather than retyping the address, and to **wait up to a
minute** without refreshing. This worked — Render's free tier "sleeps" after
inactivity and takes time to wake up on the very first visit, which is normal
behavior, not a bug.

**Step 15.9 — Confirmed fully working**
You tested registering, logging in, and reaching the admin panel — all
successful on the real public link.

**Step 15.10 — A security reminder**
Since your GitHub repository is **public**, anyone could technically view
your `app.py` source code — including the default admin password sitting in
plain text. I strongly recommended (and you should confirm you did) changing
the admin username/password via "My Profile" immediately, and ideally
updating the `secret_key` value in the code too.

---

## PHASE 16 — Discovering Render's Data-Loss Problem

**Step 16.1 — You correctly identified a real limitation yourself**
You noticed that when Render's free instance goes to sleep and wakes back up,
all registered student data disappears.

**Why this happens:** Render's free tier doesn't include permanent storage.
When the service restarts (which happens on every sleep/wake cycle on the
free plan), it starts from a completely fresh copy of your uploaded code —
and your `students.db` file, which was never saved anywhere lasting, resets
to empty.

**Step 16.2 — I explained two free fixes and asked you to choose:**
- **Option A:** switch hosting entirely to **PythonAnywhere**, whose free
  tier includes genuine permanent file storage — no code changes needed, but
  you'd get a new web address
- **Option B:** stay on Render, but switch the database itself to a free
  cloud database service — keeps your current link, but needs real code changes

**You chose Option A.**

---

## PHASE 17 — Migrating to PythonAnywhere

**Step 17.1 — Creating the account**
You signed up for PythonAnywhere's free "Beginner" plan, choosing a username
(`Aliyubnharoun123`) that would become part of your permanent site address.

**Step 17.2 — Recreating the folder structure using their Files page**
Unlike GitHub, PythonAnywhere's mobile upload only handles one file at a
time and doesn't support the folder-creation-via-URL trick the same way.
So the process was: create a `student_portal` directory, upload the 4 root
files individually, create a `templates` directory inside it and upload all
26 `.html` files one at a time, then create a `static` directory and upload
`style.css` and `logo.jpg`.

**Step 17.3 — You briefly got lost navigating back**
After going "back," you ended up at PythonAnywhere's home Files page instead
of inside your project folder. I explained your files were completely safe
(nothing gets deleted by navigating), and showed you the `student_portal/`
entry to tap back into it.

**Step 17.4 — Checking for the trailing-space problem again (proactively)**
Given it had caused real errors twice before, you specifically wanted to
double check your folder name wasn't affected this time. I introduced you to
PythonAnywhere's **Bash console** — a black terminal screen where you can
type direct commands. We used:
```
ls -la
```
to list files, then:
```
ls -la | cat -A
```
which adds a visible `$` marker at the very end of every line — making any
invisible trailing space impossible to hide. This confirmed your folder names
were completely clean this time.

**Step 17.5 — Setting up the actual website (the "Web" tab)**
This is PythonAnywhere's equivalent of Render's automatic setup, but done
manually:
1. **Add a new web app**, confirmed your domain would be
   `Aliyubnharoun123.pythonanywhere.com`
2. Chose **"Manual configuration"** (rather than an automatic Flask template,
   since we already had a specific, working `app.py`)
3. Chose Python version 3.10

**Step 17.6 — Filling in the Code section**
- **Source code path:** told PythonAnywhere exactly where your `app.py` lives:
  `/home/Aliyubnharoun123/student_portal`

**Step 17.7 — Filling in Static Files**
Told PythonAnywhere that any web request starting with `/static/` should be
answered directly from your `static` folder on disk — much faster than
routing every image/CSS request through Python code:
- **URL:** `/static/`
- **Directory:** `/home/Aliyubnharoun123/student_portal/static`

**Step 17.8 — Editing the WSGI configuration file**
This is the one file that actually tells PythonAnywhere's server *how* to
start your specific app. It comes with default placeholder text that must be
completely deleted and replaced with:
```python
import sys
path = '/home/Aliyubnharoun123/student_portal'
if path not in sys.path:
    sys.path.append(path)

from app import app as application
```
This tells Python where to find your code, and specifically which variable
inside `app.py` (called `app`, renamed here to `application`) is the actual
website to run. You had difficulty selecting/deleting all the existing text
on a mobile keyboard — solved by holding the backspace key down continuously
until the box was empty, then typing the new code in.

**Step 17.9 — Reloading**
Every single change on the Web tab (static files, WSGI file, anything)
requires tapping the green **Reload** button before it takes effect — this
step was repeated several times throughout setup.

**Step 17.10 — First successful load**
Visiting `Aliyubnharoun123.pythonanywhere.com` showed your actual dashboard
content (sidebar links, "Developed by Aliyu Bn Haroon" credit, your logo) —
confirming the Python code itself was working correctly on this new host.
However, it displayed with **no styling** — plain unformatted HTML, oversized
logo, default blue/purple link colors instead of your navy/gold theme.

**Step 17.11 — Diagnosing the missing CSS**
Several checks were run to isolate the cause:
- Directly visiting `Aliyubnharoun123.pythonanywhere.com/static/style.css`
  showed the CSS file's actual content loading perfectly — meaning the file
  itself was fine and reachable
- Using the Bash console, `ls -la` confirmed both `style.css` and `logo.jpg`
  genuinely existed in the correct `static` folder
- Reviewing the actual template code confirmed `dashboard.html` and
  `admin_login.html` both reference the stylesheet in exactly the same way —
  ruling out a coding mistake
- You reported that the **admin pages loaded with correct styling**, while
  student-facing pages (like `/login`) did not — despite using identical code
- Tried Incognito mode to rule out simple browser caching — the problem persisted even there

**Status: this specific issue was not fully resolved in this session.** It
behaves like some kind of caching or timing inconsistency specific to
PythonAnywhere's serving of certain pages, since the underlying file and code
were both verified correct. Suggested next steps for whenever you return to
this: compare the raw page source (`view-source:` prefix) of a broken page
against a working one side-by-side, try several reloads spaced a few minutes
apart, fully clear Chrome's cache, and check PythonAnywhere's own Error/Server
logs for that specific request.

**Step 17.12 — Final links given**
```
Student Portal: Aliyubnharoun123.pythonanywhere.com/login
Admin Portal:   Aliyubnharoun123.pythonanywhere.com/admin/login
```

---

## PHASE 18 — This Document

You asked for this full written record so you could relearn everything later
without needing to scroll back through the entire conversation.

---

## Quick-Reference: Every Screenshot's Role

| Screenshot(s) | What it showed | What it told us |
|---|---|---|
| 6882.jpg | Successful Flask startup | Server itself was fine |
| 6883.jpg | TemplateNotFound error | Folder structure problem |
| 6886.jpg | File manager, wrong nesting | templates/static outside main folder |
| 6953/6954.jpg | Working dashboard | Fix confirmed successful |
| 8420/8510.jpg | Same TemplateNotFound, new folder | Needed deeper investigation |
| 8543.jpg | File manager, looked correct | Led to requesting a zip for direct inspection |
| 8576/8575/8574.jpg | Working portal, broken logo icon | Led to discovering file corruption |
| 8839/8833/8844.jpg | FUDMA's real portal | Design inspiration for full redesign |
| 9207/9208.jpg | TemplateNotFound again, files present | Led to discovering Pydroid caching issue |
| 9241/9248/9249.jpg | Render dashboard/service details | Confirmed Render deployment succeeded |
| 9240.jpg | "Not Found" on live Render link | Free tier waking-up behavior, not a bug |
| 10063–10193.jpg | PythonAnywhere setup screens | Guided each configuration field precisely |

---

## Key Lessons to Remember Going Forward

1. **Folder names must be exact** — no trailing spaces, correct spelling,
   correct case. When in doubt, use a Bash console with `ls -la | cat -A`.
2. **A server needs a real restart, not just a browser refresh**, after files
   change underneath it.
3. **Zipping and inspecting a project directly is the fastest way to
   diagnose a mystery error** — screenshots can look correct while something
   is still wrong underneath.
4. **Free hosting always has a tradeoff.** Render sleeps and loses data;
   PythonAnywhere stays permanent but needs a monthly check-in.
5. **Security matters even on a "just testing" project** — default passwords
   and secret keys should always be changed before sharing a real link.
