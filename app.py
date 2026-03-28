from flask import Flask, render_template, request, redirect, session
import sqlite3
import datetime

app = Flask(__name__)
app.secret_key = "secret123"

# ---------------- DB ----------------
def init_db():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
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
    CREATE TABLE IF NOT EXISTS todos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        task TEXT,
        status TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------------- SUGGESTION ----------------
def suggest_skill(progress):
    if progress < 30:
        return "Start basics"
    elif progress < 70:
        return "Practice more"
    else:
        return "Build projects 🚀"

# ---------------- ROUTES ----------------
@app.route('/')
def home():
    return redirect('/login')

# -------- REGISTER --------
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO users(username,password) VALUES(?,?)",(u,p))
        conn.commit()
        conn.close()

        return redirect('/login')
    return render_template('register.html')

# -------- LOGIN --------
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=? AND password=?",(u,p))
        user = cur.fetchone()
        conn.close()

        if user:
            session['user_id'] = user[0]
            return redirect('/dashboard')

    return render_template('login.html')

# -------- DASHBOARD --------
@app.route('/dashboard', methods=['GET','POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    # ADD SKILL
    if request.method == 'POST':
        name = request.form['name']
        progress = request.form['progress']
        cur.execute("INSERT INTO skills(user_id,name,progress) VALUES(?,?,?)",
                    (user_id,name,progress))
        conn.commit()

    # FETCH SKILLS
    cur.execute("SELECT * FROM skills WHERE user_id=?", (user_id,))
    skills = cur.fetchall()

    # FETCH TODOS
    cur.execute("SELECT * FROM todos WHERE user_id=?", (user_id,))
    todos = cur.fetchall()

    conn.close()

    # Suggestions
    suggestions = [suggest_skill(s[3]) for s in skills]

    # Graph
    skill_names = [s[2] for s in skills]
    skill_progress = [s[3] for s in skills]

    # Streak (simple)
    streak = len(skills)

    return render_template("index.html",
                           skills=skills,
                           suggestions=suggestions,
                           skill_names=skill_names,
                           skill_progress=skill_progress,
                           streak=streak,
                           todos=todos)

# -------- ADD TODO --------
@app.route('/add_todo', methods=['POST'])
def add_todo():
    user_id = session['user_id']
    task = request.form['task']

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("INSERT INTO todos(user_id,task,status) VALUES(?,?,?)",
                (user_id,task,"pending"))
    conn.commit()
    conn.close()

    return redirect('/dashboard')

# -------- DELETE TODO --------
@app.route('/delete_todo/<int:id>')
def delete_todo(id):
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM todos WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/dashboard')

# -------- LOGOUT --------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == "__main__":
    app.run(debug=True)

