<<<<<<< HEAD
import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import google.generativeai as genai 
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
import spotipy

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

# Configure Gemini
try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
except Exception as e:
    print(f"Error configuring Gemini API: {e}")
    flash("API key not configured. Gemini functionality may not work.", "error")

# Spotify config
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = "http://127.0.0.1:5000/spotify/callback"
SCOPE = "playlist-modify-public playlist-modify-private"

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

# Gemini AI route
@app.route("/gemini", methods=["GET","POST"])
def gemini():
    if "user_id" not in session:
        return redirect(url_for("login"))

    response_text = ""
    if request.method == "POST":
        user_input = request.form["message"]
        try:
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(user_input)
            response_text = response.text
        except Exception as e:
            response_text = f"An error occurred: {e}"
            flash("Failed to get a response from Gemini. Please check your API key and network connection.", "error")

    return render_template("gemini.html", response=response_text, username=session["username"])

# Spotify login
@app.route("/spotify/login")
def spotify_login():
    if "user_id" not in session:
        return redirect(url_for("login"))
    sp_oauth = SpotifyOAuth(
        SPOTIFY_CLIENT_ID,
        SPOTIFY_CLIENT_SECRET,
        SPOTIFY_REDIRECT_URI,
        scope=SCOPE,
        cache_path=f".cache-{session['username']}"
    )
    return redirect(sp_oauth.get_authorize_url())

@app.route("/spotify/callback")
def spotify_callback():
    sp_oauth = SpotifyOAuth(
        SPOTIFY_CLIENT_ID,
        SPOTIFY_CLIENT_SECRET,
        SPOTIFY_REDIRECT_URI,
        scope=SCOPE,
        cache_path=f".cache-{session['username']}"
    )
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session["spotify_token"] = token_info['access_token']
    return redirect(url_for("gemini"))

@app.route("/create_spotify_playlist", methods=["POST"])
def create_spotify_playlist():
    if "spotify_token" not in session:
        flash("Connect your Spotify account first!", "error")
        return redirect(url_for("gemini"))

    songs = request.form["songs"].split(',')
    token = session["spotify_token"]
    sp = spotipy.Spotify(auth=token)
    user_id = sp.current_user()['id']
    playlist = sp.user_playlist_create(user=user_id, name="Gemini AI Playlist", public=True)

    track_uris = []
    for song in songs:
        results = sp.search(q=song.strip(), limit=1, type='track')
        if results['tracks']['items']:
            track_uris.append(results['tracks']['items'][0]['uri'])

    if track_uris:
        sp.playlist_add_items(playlist['id'], track_uris)
        flash("Playlist created on Spotify!", "success")
    else:
        flash("No tracks found for these songs.", "error")

    return redirect(url_for("gemini"))

if __name__ == "__main__":
    app.run(debug=True)
=======
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
>>>>>>> 866814961c062d2ffa52ba62ffa5f29751ab00a9
