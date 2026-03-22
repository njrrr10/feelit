# Feelit – AI Music Recommender

## Setup

### 1. Clone repo
git clone <link>

### 2. Backend
cd backend
pip install -r requirements.txt

Create a Spotify Developer application

1. Go to: [https://developer.spotify.com/dashboard](https://developer.spotify.com/dashboard)
2. Log in with your Spotify account
3. Click **Create app**
4. Complete the fields:
   - **App name:** Feelit
   - **App description:** AI music recommender
5. Click **Create**
6. Open the created app
7. Copy:
   - **Client ID**
   - **Client Secret**


Create a `.env` file with:
SPOTIPY_CLIENT_ID=your_id
SPOTIPY_CLIENT_SECRET=your_secret

Run:
python -m uvicorn app.main:app --reload

### 3. Frontend
cd frontend
npm install
npm run dev

Open:
http://localhost:5173