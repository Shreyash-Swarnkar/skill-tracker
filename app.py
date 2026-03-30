from flask import Flask, render_template, request, redirect, session, send_from_directory
import sqlite3
from datetime import datetime, timedelta, date

# =========================
# 🚀 APP INIT
# =========================
app = Flask(__name__, template_folder='.', static_folder='.')

# 🔥 FIXED SESSION CONFIG
app.config['SECRET_KEY'] = 'supersecretkey123'
app.config['SESSION_PERMANENT'] = True


# =========================
# 📁 STATIC FILES
# =========================
@app.route('/style.css')
def style():
    return send_from_directory('.', 'style.css')

@app.route('/script.js')
def script():
    return send_from_directory('.', 'script.js')


# =========================
# 🗄️ DATABASE INIT
# =========================
def init_db():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS skills(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        name TEXT,
        progress INTEGER
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS activity(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        date TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()


# =========================
# 🔥 STREAK FUNCTION
# =========================
def calculate_streak(user_id):
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("SELECT DISTINCT date FROM activity WHERE user_id=? ORDER BY date DESC", (user_id,))
    dates = [row[0] for row in cur.fetchall()]

    conn.close()

    streak = 0
    today = datetime.today()

    for i, d in enumerate(dates):
        if datetime.strptime(d, "%Y-%m-%d").date() == (today - timedelta(days=i)).date():
            streak += 1
        else:
            break

    return streak


# =========================
# 🏠 HOME
# =========================
@app.route("/")
def home():
    return redirect("/login")


# =========================
# 🔐 LOGIN PAGE
# =========================
@app.route("/login")
def login():
    return render_template("login.html")


# =========================
# 🔐 GOOGLE LOGIN (FIXED)
# =========================
@app.route("/google_login", methods=["POST"])
def google_login():

    print("🔥 GOOGLE LOGIN HIT")

    email = request.json["email"]
    print("EMAIL:", email)

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    # Check if user exists
    cur.execute("SELECT * FROM users WHERE email=?", (email,))
    user = cur.fetchone()

    # Create if not exists
    if not user:
        cur.execute("INSERT INTO users (email) VALUES (?)", (email,))
        conn.commit()

        cur.execute("SELECT * FROM users WHERE email=?", (email,))
        user = cur.fetchone()

    # 🔥 IMPORTANT FIX
    session["user_id"] = user[0]
    session.permanent = True

    print("SESSION SET:", session.get("user_id"))

    conn.close()

    return "OK"


# =========================
# 📊 DASHBOARD
# =========================
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():

    print("SESSION IN DASHBOARD:", session.get("user_id"))

    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    # ➕ ADD SKILL
    if request.method == "POST":
        name = request.form["name"]
        progress = request.form["progress"]

        cur.execute("""
        INSERT INTO skills (user_id, name, progress)
        VALUES (?, ?, ?)
        """, (user_id, name, progress))

        # 🔥 SAVE ACTIVITY (STREAK)
        today = str(date.today())
        cur.execute("""
        INSERT INTO activity (user_id, date)
        VALUES (?, ?)
        """, (user_id, today))

        conn.commit()

    # 📊 FETCH SKILLS
    cur.execute("SELECT * FROM skills WHERE user_id=?", (user_id,))
    skills = cur.fetchall()

    conn.close()

    # 📈 GRAPH DATA
    skill_names = [s[2] for s in skills]
    skill_progress = [s[3] for s in skills]

    # 🧠 SUGGESTIONS
    suggestions = []
    for s in skills:
        if s[3] < 30:
            suggestions.append("Start with basics")
        elif s[3] < 70:
            suggestions.append("Practice more problems")
        else:
            suggestions.append("Build real projects 🚀")

    # 🔥 STREAK
    streak = calculate_streak(user_id)

    return render_template(
        "index.html",
        skills=skills,
        skill_names=skill_names,
        skill_progress=skill_progress,
        suggestions=suggestions,
        streak=streak
    )


# =========================
# ✏️ EDIT
# =========================
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    if request.method == "POST":
        name = request.form["name"]
        progress = request.form["progress"]

        cur.execute("""
        UPDATE skills SET name=?, progress=?
        WHERE id=?
        """, (name, progress, id))

        conn.commit()
        conn.close()

        return redirect("/dashboard")

    cur.execute("SELECT * FROM skills WHERE id=?", (id,))
    skill = cur.fetchone()

    conn.close()

    return render_template("edit.html", skill=skill)


# =========================
# 🗑 DELETE
# =========================
@app.route("/delete/<int:id>")
def delete(id):

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("DELETE FROM skills WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/dashboard")


# =========================
# 🚪 LOGOUT
# =========================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# =========================
# 🚀 RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)



    