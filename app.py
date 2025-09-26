import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import google.generativeai as genai
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

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

# Spotify config
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = "https://playitout.onrender.com/spotify/callback"
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

@app.route("/gemini", methods=["GET","POST"])
def gemini():
    if "user_id" not in session:
        return redirect(url_for("login"))

    response_text = ""
    song_list = []

    if request.method == "POST":
        user_input = request.form["message"]
        try:
            model = genai.GenerativeModel('gemini-2.5-flash')
            prompt = f"""
            The user said: {user_input}.
            Generate a playlist of songs matching this vibe.
            Reply ONLY with a comma-separated list of song titles and artist names.
            """
            response = model.generate_content(prompt)
            response_text = response.text.strip()

            # Build song list
            song_list = []
            for s in response_text.split(','):
                if '-' in s:
                    title, artist = s.strip().split('-', 1)
                    song_list.append({
                        "title": title.strip(),
                        "artist": artist.strip()
                    })

            session["song_list"] = song_list  # store for Spotify playlist

        except Exception as e:
            flash(f"Failed to generate playlist: {e}", "error")

    return render_template("gemini.html", response=response_text, songs=song_list)

@app.route("/spotify/login")
def spotify_login():
    if "user_id" not in session:
        return redirect(url_for("login"))
    sp_oauth = SpotifyOAuth(
        SPOTIFY_CLIENT_ID,
        SPOTIFY_CLIENT_SECRET,
        SPOTIFY_REDIRECT_URI,
        scope=SCOPE
    )
    return redirect(sp_oauth.get_authorize_url())

@app.route("/spotify/callback")
def spotify_callback():
    sp_oauth = SpotifyOAuth(
        SPOTIFY_CLIENT_ID,
        SPOTIFY_CLIENT_SECRET,
        SPOTIFY_REDIRECT_URI,
        scope=SCOPE
    )
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session["spotify_token"] = token_info['access_token']
    return redirect(url_for("gemini"))

@app.route("/create_spotify_playlist", methods=["POST"])
def create_spotify_playlist():
    if "spotify_token" not in session or "song_list" not in session:
        flash("Connect Spotify and generate a playlist first!", "error")
        return redirect(url_for("gemini"))

    songs = session["song_list"]
    sp = spotipy.Spotify(auth=session["spotify_token"])
    user_id = sp.current_user()['id']

    # Create Spotify playlist
    playlist = sp.user_playlist_create(user_id, name="Gemini AI Playlist", public=True)

    track_uris = []
    for song in songs:
        query = f"{song['title']} {song['artist']}"
        results = sp.search(q=query, limit=1, type='track')
        if results['tracks']['items']:
            track_uris.append(results['tracks']['items'][0]['uri'])

    if track_uris:
        sp.playlist_add_items(playlist['id'], track_uris)

    # ⬇️ Instead of redirecting OUT, render your player
    return render_template("playlist.html", songs=songs, playlist_url=playlist['external_urls']['spotify'])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
