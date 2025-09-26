# 🎵 Play It Out

AI-powered music assistant that lets you chat, generate playlists, and connect with Spotify.  
Built with **Flask**, **Spotipy**, **Google Generative AI**, and deployed on **Render**.

## 🚀 Features
- 💬 **AI Chat** – Ask Gemini AI to suggest music or create playlists.  
- 🎧 **Playlist Management** – View and play tracks inside the app.  
- 🔗 **Spotify Integration** – Login and export playlists to your Spotify account.  
- 🎨 **Modern UI** – Transparent panels with a custom background image.  
- 🌐 **Deployed on Render** – Easy one-click deployment.

## 📝 Project Description
Play It Out is a web application that combines AI-generated music recommendations with Spotify integration. Users can chat with the AI, generate playlists based on mood or prompts, and export these playlists directly to their Spotify account.  



## ⚙️ Setup Instructions
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/play-it-out.git
   cd play-it-out
Create a virtual environment and activate it:

bash
Copy code
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install dependencies:

bash
Copy code
pip install -r requirements.txt
Set environment variables in a .env file:

env
Copy code
FLASK_SECRET_KEY=your_secret_key
GEMINI_API_KEY=your_gemini_api_key
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
Run the app locally:

bash
Copy code
flask run
Access at: http://127.0.0.1:5000/

🛠 Technology Stack
Backend: Python, Flask

AI: Google Generative AI (Gemini)

Spotify Integration: Spotipy

Database: SQLite

Deployment: Render

✅ Features Implemented
User signup/login with hashed passwords

Chat with Gemini AI to generate playlists

Spotify login and playlist export

Playlist creation and display inside the app

🔗 Demo Links
Live Website: https://playitout.onrender.com


