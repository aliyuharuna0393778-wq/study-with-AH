from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import os
import re

app = Flask(__name__)
app.secret_key = "change-this-to-a-random-secret-key"  # change before real use

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "students.db")

# ---- Branding (edit these two lines to customize) ----
SCHOOL_NAME = "Study with AH"
SCHOOL_INITIALS = "AH"

# ---- First admin account created automatically the first time the app runs.
# CHANGE THIS PASSWORD, then you can add more admins from inside the site. ----
DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "changeme123"


@app.context_processor
def inject_branding():
    return {"school_name": SCHOOL_NAME, "school_initials": SCHOOL_INITIALS}


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            phone_number TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS announcements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            body TEXT NOT NULL,
            posted_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS lessons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            url TEXT NOT NULL,
            description TEXT,
            posted_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS login_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_type TEXT NOT NULL,
            identifier TEXT NOT NULL,
            ip_address TEXT,
            success INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            course_title TEXT NOT NULL,
            score TEXT,
            grade TEXT,
            semester TEXT,
            posted_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            due_date TEXT,
            link TEXT,
            posted_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS assignment_submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            assignment_id INTEGER NOT NULL,
            student_id TEXT NOT NULL,
            submission_text TEXT,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create the first admin automatically if no admins exist yet
    existing = conn.execute("SELECT COUNT(*) AS c FROM admins").fetchone()
    if existing["c"] == 0:
        conn.execute(
            "INSERT INTO admins (username, password_hash) VALUES (?, ?)",
            (DEFAULT_ADMIN_USERNAME, generate_password_hash(DEFAULT_ADMIN_PASSWORD))
        )

    conn.commit()
    conn.close()


def is_valid_phone(phone):
    # accepts digits, spaces, +, -, at least 7 digits total
    digits = re.sub(r"[^\d]", "", phone)
    return len(digits) >= 7


def get_client_ip():
    if request.headers.get("X-Forwarded-For"):
        return request.headers.get("X-Forwarded-For").split(",")[0].strip()
    return request.remote_addr


def log_login(user_type, identifier, success):
    conn = get_db()
    conn.execute(
        "INSERT INTO login_log (user_type, identifier, ip_address, success) VALUES (?, ?, ?, ?)",
        (user_type, identifier, get_client_ip(), 1 if success else 0)
    )
    conn.commit()
    conn.close()


def admin_required():
    return session.get("is_admin") and session.get("admin_username")


# ---------------- Student routes ----------------

@app.route("/")
def home():
    if "student_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        student_id = request.form.get("studentId", "").strip()
        full_name = request.form.get("fullName", "").strip()
        phone_number = request.form.get("phoneNumber", "").strip()
        password = request.form.get("password", "")

        errors = []
        if not student_id:
            errors.append("Student ID / Matric number is required.")
        if not full_name:
            errors.append("Full name is required.")
        if not is_valid_phone(phone_number):
            errors.append("Enter a valid phone number.")
        if len(password) < 6:
            errors.append("Password must be at least 6 characters.")

        if errors:
            for e in errors:
                flash(e, "error")
            return render_template("register.html", form=request.form)

        conn = get_db()
        try:
            conn.execute(
                "INSERT INTO students (student_id, full_name, phone_number, password_hash) VALUES (?, ?, ?, ?)",
                (student_id, full_name, phone_number, generate_password_hash(password))
            )
            conn.commit()
        except sqlite3.IntegrityError:
            flash("That student ID or phone number is already registered.", "error")
            conn.close()
            return render_template("register.html", form=request.form)
        conn.close()

        flash("Account created. You can sign in now.", "success")
        return redirect(url_for("login"))

    return render_template("register.html", form={})


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        identifier = request.form.get("identifier", "").strip()
        password = request.form.get("password", "")

        conn = get_db()
        row = conn.execute(
            "SELECT * FROM students WHERE student_id = ? OR phone_number = ?",
            (identifier, identifier)
        ).fetchone()
        conn.close()

        if row and check_password_hash(row["password_hash"], password):
            session["student_id"] = row["student_id"]
            session["full_name"] = row["full_name"]
            log_login("student", identifier, True)
            return redirect(url_for("dashboard"))
        else:
            log_login("student", identifier, False)
            flash("Incorrect matric number/phone number, or password.", "error")

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if "student_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    announcements = conn.execute(
        "SELECT * FROM announcements ORDER BY created_at DESC LIMIT 3"
    ).fetchall()
    lesson_count = conn.execute("SELECT COUNT(*) AS c FROM lessons").fetchone()["c"]
    result_count = conn.execute(
        "SELECT COUNT(*) AS c FROM results WHERE student_id = ?", (session["student_id"],)
    ).fetchone()["c"]
    assignment_count = conn.execute("SELECT COUNT(*) AS c FROM assignments").fetchone()["c"]
    student = conn.execute(
        "SELECT created_at FROM students WHERE student_id = ?", (session["student_id"],)
    ).fetchone()
    conn.close()

    return render_template(
        "dashboard.html",
        active_page="dashboard",
        full_name=session.get("full_name"),
        student_id=session.get("student_id"),
        announcements=announcements,
        lesson_count=lesson_count,
        result_count=result_count,
        assignment_count=assignment_count,
        joined_on=student["created_at"] if student else ""
    )


@app.route("/notice-board")
def notice_board():
    if "student_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    announcements = conn.execute("SELECT * FROM announcements ORDER BY created_at DESC").fetchall()
    conn.close()

    return render_template(
        "notice_board.html",
        active_page="notices",
        full_name=session.get("full_name"),
        student_id=session.get("student_id"),
        announcements=announcements
    )


@app.route("/my-results")
def student_results():
    if "student_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    results = conn.execute(
        "SELECT * FROM results WHERE student_id = ? ORDER BY created_at DESC",
        (session["student_id"],)
    ).fetchall()
    conn.close()

    return render_template(
        "student_results.html",
        active_page="results",
        full_name=session.get("full_name"),
        student_id=session.get("student_id"),
        results=results
    )


@app.route("/e-learning")
def student_lessons():
    if "student_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    lessons = conn.execute("SELECT * FROM lessons ORDER BY created_at DESC").fetchall()
    conn.close()

    return render_template(
        "student_lessons.html",
        active_page="lessons",
        full_name=session.get("full_name"),
        student_id=session.get("student_id"),
        lessons=lessons
    )


@app.route("/assignments", methods=["GET", "POST"])
def student_assignments():
    if "student_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        assignment_id = request.form.get("assignment_id")
        submission_text = request.form.get("submission_text", "").strip()

        if submission_text:
            conn = get_db()
            conn.execute(
                "INSERT INTO assignment_submissions (assignment_id, student_id, submission_text) VALUES (?, ?, ?)",
                (assignment_id, session["student_id"], submission_text)
            )
            conn.commit()
            conn.close()
            flash("Submission sent.", "success")
        else:
            flash("Write something before submitting.", "error")
        return redirect(url_for("student_assignments"))

    conn = get_db()
    assignments = conn.execute("SELECT * FROM assignments ORDER BY created_at DESC").fetchall()
    my_submissions = conn.execute(
        "SELECT assignment_id FROM assignment_submissions WHERE student_id = ?",
        (session["student_id"],)
    ).fetchall()
    conn.close()

    submitted_ids = {row["assignment_id"] for row in my_submissions}

    return render_template(
        "student_assignments.html",
        active_page="assignments",
        full_name=session.get("full_name"),
        student_id=session.get("student_id"),
        assignments=assignments,
        submitted_ids=submitted_ids
    )


@app.route("/personal-data")
def personal_data():
    if "student_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    student = conn.execute(
        "SELECT * FROM students WHERE student_id = ?", (session["student_id"],)
    ).fetchone()
    conn.close()

    return render_template(
        "personal_data.html",
        active_page="personal",
        full_name=session.get("full_name"),
        student_id=session.get("student_id"),
        student=student
    )


@app.route("/help")
def portal_help():
    if "student_id" not in session:
        return redirect(url_for("login"))

    return render_template(
        "portal_help.html",
        active_page="help",
        full_name=session.get("full_name"),
        student_id=session.get("student_id")
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ---------------- Forgot password ----------------

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        student_id = request.form.get("studentId", "").strip()
        phone_number = request.form.get("phoneNumber", "").strip()

        conn = get_db()
        row = conn.execute(
            "SELECT * FROM students WHERE student_id = ? AND phone_number = ?",
            (student_id, phone_number)
        ).fetchone()
        conn.close()

        if row:
            session["reset_student_id"] = row["student_id"]
            return redirect(url_for("reset_password"))
        else:
            flash("No account matches that student ID and phone number.", "error")

    return render_template("forgot_password.html")


@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    if "reset_student_id" not in session:
        return redirect(url_for("forgot_password"))

    if request.method == "POST":
        new_password = request.form.get("password", "")
        confirm = request.form.get("confirmPassword", "")

        if len(new_password) < 6:
            flash("Password must be at least 6 characters.", "error")
            return render_template("reset_password.html")
        if new_password != confirm:
            flash("Passwords do not match.", "error")
            return render_template("reset_password.html")

        conn = get_db()
        conn.execute(
            "UPDATE students SET password_hash = ? WHERE student_id = ?",
            (generate_password_hash(new_password), session["reset_student_id"])
        )
        conn.commit()
        conn.close()

        session.pop("reset_student_id", None)
        flash("Password updated. You can sign in now.", "success")
        return redirect(url_for("login"))

    return render_template("reset_password.html")


# ---------------- Contact ----------------

@app.route("/contact")
def contact():
    return render_template("contact.html")


# ---------------- Admin auth ----------------

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        conn = get_db()
        row = conn.execute("SELECT * FROM admins WHERE username = ?", (username,)).fetchone()
        conn.close()

        if row and check_password_hash(row["password_hash"], password):
            session["is_admin"] = True
            session["admin_username"] = row["username"]
            log_login("admin", username, True)
            return redirect(url_for("admin_students"))
        else:
            log_login("admin", username, False)
            flash("Incorrect admin username or password.", "error")

    return render_template("admin_login.html")


@app.route("/admin/logout")
def admin_logout():
    session.pop("is_admin", None)
    session.pop("admin_username", None)
    return redirect(url_for("admin_login"))


# ---------------- Admin: students ----------------

@app.route("/admin/students")
def admin_students():
    if not admin_required():
        return redirect(url_for("admin_login"))

    conn = get_db()
    students = conn.execute(
        "SELECT student_id, full_name, phone_number, created_at FROM students ORDER BY created_at DESC"
    ).fetchall()
    conn.close()

    return render_template("admin_students.html", students=students)


@app.route("/admin/students/delete/<student_id>")
def admin_delete_student(student_id):
    if not admin_required():
        return redirect(url_for("admin_login"))

    conn = get_db()
    conn.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
    conn.commit()
    conn.close()

    flash(f"Removed student {student_id}.", "success")
    return redirect(url_for("admin_students"))


@app.route("/admin/students/reset-password/<student_id>", methods=["GET", "POST"])
def admin_reset_student_password(student_id):
    if not admin_required():
        return redirect(url_for("admin_login"))

    conn = get_db()
    student = conn.execute("SELECT * FROM students WHERE student_id = ?", (student_id,)).fetchone()

    if not student:
        conn.close()
        flash("Student not found.", "error")
        return redirect(url_for("admin_students"))

    if request.method == "POST":
        new_password = request.form.get("password", "")
        if len(new_password) < 6:
            flash("Password must be at least 6 characters.", "error")
        else:
            conn.execute(
                "UPDATE students SET password_hash = ? WHERE student_id = ?",
                (generate_password_hash(new_password), student_id)
            )
            conn.commit()
            conn.close()
            flash(f"Password updated for {student_id}.", "success")
            return redirect(url_for("admin_students"))

    conn.close()
    return render_template("admin_reset_student.html", student=student)


# ---------------- Admin: announcements ----------------

@app.route("/admin/announcements", methods=["GET", "POST"])
def admin_announcements():
    if not admin_required():
        return redirect(url_for("admin_login"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        body = request.form.get("body", "").strip()

        if not title or not body:
            flash("Title and message are both required.", "error")
        else:
            conn = get_db()
            conn.execute(
                "INSERT INTO announcements (title, body, posted_by) VALUES (?, ?, ?)",
                (title, body, session.get("admin_username"))
            )
            conn.commit()
            conn.close()
            flash("Announcement posted.", "success")
            return redirect(url_for("admin_announcements"))

    conn = get_db()
    announcements = conn.execute("SELECT * FROM announcements ORDER BY created_at DESC").fetchall()
    conn.close()

    return render_template("admin_announcements.html", announcements=announcements)


@app.route("/admin/announcements/delete/<int:item_id>")
def admin_delete_announcement(item_id):
    if not admin_required():
        return redirect(url_for("admin_login"))

    conn = get_db()
    conn.execute("DELETE FROM announcements WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()

    flash("Announcement removed.", "success")
    return redirect(url_for("admin_announcements"))


# ---------------- Admin: lesson links ----------------

@app.route("/admin/lessons", methods=["GET", "POST"])
def admin_lessons():
    if not admin_required():
        return redirect(url_for("admin_login"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        url_value = request.form.get("url", "").strip()
        description = request.form.get("description", "").strip()

        if not title or not url_value:
            flash("Title and link are both required.", "error")
        else:
            conn = get_db()
            conn.execute(
                "INSERT INTO lessons (title, url, description, posted_by) VALUES (?, ?, ?, ?)",
                (title, url_value, description, session.get("admin_username"))
            )
            conn.commit()
            conn.close()
            flash("Lesson link added.", "success")
            return redirect(url_for("admin_lessons"))

    conn = get_db()
    lessons = conn.execute("SELECT * FROM lessons ORDER BY created_at DESC").fetchall()
    conn.close()

    return render_template("admin_lessons.html", lessons=lessons)


@app.route("/admin/lessons/delete/<int:item_id>")
def admin_delete_lesson(item_id):
    if not admin_required():
        return redirect(url_for("admin_login"))

    conn = get_db()
    conn.execute("DELETE FROM lessons WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()

    flash("Lesson link removed.", "success")
    return redirect(url_for("admin_lessons"))


@app.route("/admin/profile", methods=["GET", "POST"])
def admin_profile():
    if not admin_required():
        return redirect(url_for("admin_login"))

    conn = get_db()
    me = conn.execute(
        "SELECT * FROM admins WHERE username = ?", (session.get("admin_username"),)
    ).fetchone()

    if request.method == "POST":
        current_password = request.form.get("current_password", "")
        new_username = request.form.get("new_username", "").strip()
        new_password = request.form.get("new_password", "")

        if not me or not check_password_hash(me["password_hash"], current_password):
            flash("Current password is incorrect.", "error")
            conn.close()
            return render_template("admin_profile.html", me=me)

        if not new_username:
            flash("Username cannot be empty.", "error")
            conn.close()
            return render_template("admin_profile.html", me=me)

        if new_password and len(new_password) < 6:
            flash("New password must be at least 6 characters.", "error")
            conn.close()
            return render_template("admin_profile.html", me=me)

        try:
            if new_password:
                conn.execute(
                    "UPDATE admins SET username = ?, password_hash = ? WHERE id = ?",
                    (new_username, generate_password_hash(new_password), me["id"])
                )
            else:
                conn.execute(
                    "UPDATE admins SET username = ? WHERE id = ?",
                    (new_username, me["id"])
                )
            conn.commit()
            session["admin_username"] = new_username
            flash("Profile updated.", "success")
        except sqlite3.IntegrityError:
            flash("That username is already taken.", "error")
        conn.close()
        return redirect(url_for("admin_profile"))

    conn.close()
    return render_template("admin_profile.html", me=me)


# ---------------- Admin: manage other admins ----------------

@app.route("/admin/admins", methods=["GET", "POST"])
def admin_admins():
    if not admin_required():
        return redirect(url_for("admin_login"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or len(password) < 6:
            flash("Username is required and password must be at least 6 characters.", "error")
        else:
            conn = get_db()
            try:
                conn.execute(
                    "INSERT INTO admins (username, password_hash) VALUES (?, ?)",
                    (username, generate_password_hash(password))
                )
                conn.commit()
                flash(f"Admin '{username}' added.", "success")
            except sqlite3.IntegrityError:
                flash("That username is already taken.", "error")
            conn.close()
            return redirect(url_for("admin_admins"))

    conn = get_db()
    admins = conn.execute("SELECT id, username, created_at FROM admins ORDER BY created_at ASC").fetchall()
    conn.close()

    return render_template("admin_admins.html", admins=admins, current_admin=session.get("admin_username"))


@app.route("/admin/admins/delete/<int:item_id>")
def admin_delete_admin(item_id):
    if not admin_required():
        return redirect(url_for("admin_login"))

    conn = get_db()
    count = conn.execute("SELECT COUNT(*) AS c FROM admins").fetchone()["c"]
    target = conn.execute("SELECT username FROM admins WHERE id = ?", (item_id,)).fetchone()

    if count <= 1:
        flash("Cannot remove the last remaining admin.", "error")
    elif target and target["username"] == session.get("admin_username"):
        flash("You cannot remove your own account while signed in.", "error")
    else:
        conn.execute("DELETE FROM admins WHERE id = ?", (item_id,))
        conn.commit()
        flash("Admin removed.", "success")

    conn.close()
    return redirect(url_for("admin_admins"))


# ---------------- Admin: results ----------------

@app.route("/admin/results", methods=["GET", "POST"])
def admin_results():
    if not admin_required():
        return redirect(url_for("admin_login"))

    if request.method == "POST":
        student_id = request.form.get("student_id", "").strip()
        course_title = request.form.get("course_title", "").strip()
        score = request.form.get("score", "").strip()
        grade = request.form.get("grade", "").strip()
        semester = request.form.get("semester", "").strip()

        if not student_id or not course_title:
            flash("Student ID and course title are required.", "error")
        else:
            conn = get_db()
            exists = conn.execute("SELECT 1 FROM students WHERE student_id = ?", (student_id,)).fetchone()
            if not exists:
                flash("No student found with that ID.", "error")
            else:
                conn.execute(
                    "INSERT INTO results (student_id, course_title, score, grade, semester, posted_by) VALUES (?, ?, ?, ?, ?, ?)",
                    (student_id, course_title, score, grade, semester, session.get("admin_username"))
                )
                conn.commit()
                flash("Result added.", "success")
            conn.close()
            return redirect(url_for("admin_results"))

    conn = get_db()
    results = conn.execute("SELECT * FROM results ORDER BY created_at DESC").fetchall()
    conn.close()

    return render_template("admin_results.html", results=results)


@app.route("/admin/results/delete/<int:item_id>")
def admin_delete_result(item_id):
    if not admin_required():
        return redirect(url_for("admin_login"))

    conn = get_db()
    conn.execute("DELETE FROM results WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()

    flash("Result removed.", "success")
    return redirect(url_for("admin_results"))


# ---------------- Admin: assignments ----------------

@app.route("/admin/assignments", methods=["GET", "POST"])
def admin_assignments():
    if not admin_required():
        return redirect(url_for("admin_login"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        due_date = request.form.get("due_date", "").strip()
        link = request.form.get("link", "").strip()

        if not title:
            flash("Title is required.", "error")
        else:
            conn = get_db()
            conn.execute(
                "INSERT INTO assignments (title, description, due_date, link, posted_by) VALUES (?, ?, ?, ?, ?)",
                (title, description, due_date, link, session.get("admin_username"))
            )
            conn.commit()
            conn.close()
            flash("Assignment posted.", "success")
            return redirect(url_for("admin_assignments"))

    conn = get_db()
    assignments = conn.execute("SELECT * FROM assignments ORDER BY created_at DESC").fetchall()
    submission_counts = conn.execute(
        "SELECT assignment_id, COUNT(*) AS c FROM assignment_submissions GROUP BY assignment_id"
    ).fetchall()
    conn.close()

    counts_by_id = {row["assignment_id"]: row["c"] for row in submission_counts}

    return render_template("admin_assignments.html", assignments=assignments, counts_by_id=counts_by_id)


@app.route("/admin/assignments/delete/<int:item_id>")
def admin_delete_assignment(item_id):
    if not admin_required():
        return redirect(url_for("admin_login"))

    conn = get_db()
    conn.execute("DELETE FROM assignments WHERE id = ?", (item_id,))
    conn.execute("DELETE FROM assignment_submissions WHERE assignment_id = ?", (item_id,))
    conn.commit()
    conn.close()

    flash("Assignment removed.", "success")
    return redirect(url_for("admin_assignments"))


@app.route("/admin/assignments/<int:item_id>/submissions")
def admin_view_submissions(item_id):
    if not admin_required():
        return redirect(url_for("admin_login"))

    conn = get_db()
    assignment = conn.execute("SELECT * FROM assignments WHERE id = ?", (item_id,)).fetchone()
    submissions = conn.execute("""
        SELECT sub.*, st.full_name FROM assignment_submissions sub
        LEFT JOIN students st ON st.student_id = sub.student_id
        WHERE sub.assignment_id = ?
        ORDER BY sub.submitted_at DESC
    """, (item_id,)).fetchall()
    conn.close()

    if not assignment:
        flash("Assignment not found.", "error")
        return redirect(url_for("admin_assignments"))

    return render_template("admin_submissions.html", assignment=assignment, submissions=submissions)


# ---------------- Admin: login activity log ----------------

@app.route("/admin/login-log")
def admin_login_log():
    if not admin_required():
        return redirect(url_for("admin_login"))

    conn = get_db()
    logs = conn.execute(
        "SELECT * FROM login_log ORDER BY created_at DESC LIMIT 200"
    ).fetchall()
    conn.close()

    return render_template("admin_login_log.html", logs=logs)


# ---------------- Admin: backup & restore ----------------

@app.route("/admin/backup")
def admin_backup():
    if not admin_required():
        return redirect(url_for("admin_login"))

    return send_file(DB_PATH, as_attachment=True, download_name="students_backup.db")


@app.route("/admin/restore", methods=["GET", "POST"])
def admin_restore():
    if not admin_required():
        return redirect(url_for("admin_login"))

    if request.method == "POST":
        file = request.files.get("backupFile")
        if not file or file.filename == "":
            flash("Choose a backup file first.", "error")
            return redirect(url_for("admin_restore"))

        if not file.filename.endswith(".db"):
            flash("That doesn't look like a valid backup file (.db).", "error")
            return redirect(url_for("admin_restore"))

        file.save(DB_PATH)
        session.clear()
        flash("Database restored successfully. Please sign in again.", "success")
        return redirect(url_for("admin_login"))

    return render_template("admin_restore.html")


init_db()

if __name__ == "__main__":
    # host="0.0.0.0" lets you open it from your phone's browser at http://127.0.0.1:5000
    app.run(host="0.0.0.0", port=5000, debug=True)
