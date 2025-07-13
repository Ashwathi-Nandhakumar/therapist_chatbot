from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from groq import Groq
import sqlite3
import os
import json
from flask import flash

# Load environment variables
load_dotenv()
language = str()
groq_api_key = os.getenv("GROQ_API_KEY")
secret_key = os.getenv("SECRET_KEY", "supersecretkey")

if not groq_api_key:
    raise RuntimeError("Missing GROQ_API_KEY in environment variables")

# Flask setup
app = Flask(__name__,static_folder='static')
app.secret_key = secret_key

# Groq client setup
groq_client = Groq(api_key=groq_api_key)

# System prompt
system_prompt_template = {
    "role": "system",
    "content": (
        "You are a kind, empathetic CBT therapist and friend who always speaks in {lang}. "
        "You talk like the user to make them feel comfortable and understood. "
        "Keep responses short, empathetic, and comforting. You listen more than you speak."
    )
}
system_prompt = dict(system_prompt_template)



# Database setup
DB_PATH = 'therapist_app.db'

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                language TEXT DEFAULT 'en',
                history TEXT
            )
        ''')
        conn.commit()

init_db()

# Helper function to get user

def get_user(username):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        return cursor.fetchone()

# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        language = request.form.get('language', 'en')

        if not username or not password:
            return "Username and password are required.", 400

        if get_user(username):
            return "Username already exists.", 400

        hashed_password = generate_password_hash(password)

        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password, language, history) VALUES (?, ?, ?, ?)",
                           (username, hashed_password, language, json.dumps([system_prompt])))
            conn.commit()

        return redirect(url_for('login'))

    return render_template('signup.html')

system_prompt["content"] = system_prompt["content"].format(lang=language)



@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    user = get_user(username)
    if not user:
        return redirect(url_for('logout'))

    language = user[3]
    history = json.loads(user[4]) if user[4] else [system_prompt]
    display_messages = []

    if request.method == 'POST':
        user_input = request.form['message'].strip()
        if user_input:
            history.append({"role": "user", "content": user_input})
            try:
                response = groq_client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=history + [{"role": "system", "content": f"Reply in {language}."}]
                )
                reply = response.choices[0].message.content
                history.append({"role": "assistant", "content": reply})
                # Save full history in DB
                with sqlite3.connect(DB_PATH) as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE users SET history = ? WHERE username = ?",
                                   (json.dumps(history), username))
                    conn.commit()
                # Show only last pair
                display_messages = [history[-2], history[-1]]
            except Exception as e:
                display_messages = [{"role": "assistant", "content": f"Error: {str(e)}"}]
    return render_template('chat.html', messages=display_messages)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        user = get_user(username)

        if user and check_password_hash(user[2], password):
            session['username'] = username
            return redirect(url_for('chat'))
        else:
            error = "Invalid credentials. Please try again."
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
