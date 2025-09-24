import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import google.generativeai as genai 
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "your_secret_key_here")

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.db")

# Initialize database
def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT,
                    password TEXT NOT NULL)""")
    conn.close()

init_db()

def get_db_connection():
    return sqlite3.connect(DB_PATH)


try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
except Exception as e:
    print(f"Error configuring Gemini API: {e}")
    print("Please ensure you have set the GEMINI_API_KEY environment variable.")
    flash("API key not configured. Gemini functionality may not work.", "error")

# Routes
@app.route("/")
def index():
    return redirect(url_for("login"))

@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form.get("email", "")
        password = generate_password_hash(request.form["password"])
        conn = get_db_connection()
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username,email,password) VALUES (?,?,?)",
                      (username,email,password))
            conn.commit()
            flash("Account created! Please log in.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Username already exists!", "error")
            return redirect(url_for("signup"))
        finally:
            conn.close()
    return render_template("signup.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        user = c.fetchone()
        conn.close()
        if user and check_password_hash(user[3], password):
            session["user_id"] = user[0]
            session["username"] = user[1]
            return redirect(url_for("home"))
        flash("Invalid username or password!", "error")
        return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/home")
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("home.html", username=session["username"])

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/gemini", methods=["GET","POST"])
def gemini():
    if "user_id" not in session:
        return redirect(url_for("login"))

    response_text = ""
    if request.method == "POST":
        user_input = request.form["message"]
        try:
            # Use a GenerativeModel for text generation
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(user_input)
            response_text = response.text
        except Exception as e:
            response_text = f"An error occurred: {e}"
            flash("Failed to get a response from Gemini. Please check your API key and network connection.", "error")

    return render_template("gemini.html", response=response_text, username=session["username"])

if __name__ == "__main__":
    app.run(debug=True)
