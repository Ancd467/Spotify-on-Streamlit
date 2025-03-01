import streamlit as st
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# 🔹 Spotify API Credentials (Replace with your own)
CLIENT_ID = "00ae56a088814adc92a252519a6b33ec"
CLIENT_SECRET = "7c638e88d3214940b20b443ed6ea0886"
REDIRECT_URI = "http://localhost:8501"  # No need for "/callback" in Streamlit

# 🔹 Define Spotify OAuth Scope (Requires Premium for full playback control)
SCOPE = "user-read-playback-state user-modify-playback-state user-read-currently-playing playlist-read-private"

# 🔹 Initialize Spotify OAuth
sp_oauth = SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI, scope=SCOPE)

st.title("🎵 Spotify Player in Streamlit 🎵")

# 🔹 Step 1: Check if the user has an auth token
query_code = st.query_params.get("code")  # Extract code safely
if query_code and "token_info" not in st.session_state:
    token_info = sp_oauth.get_access_token(query_code)
    if token_info:
        st.session_state["token_info"] = token_info
        st.rerun()  # ✅ Fix: Use st.rerun() instead of experimental_rerun()

# 🔹 Step 2: If no token, show login button
if "token_info" not in st.session_state:
    auth_url = sp_oauth.get_authorize_url()
    st.markdown(f"[🔗 Click here to log in with Spotify]({auth_url})")
    st.stop()

# 🔹 Step 3: Fetch & Refresh Access Token
token_info = st.session_state["token_info"]

if sp_oauth.is_token_expired(token_info):
    token_info = sp_oauth.refresh_access_token(token_info["refresh_token"])
    st.session_state["token_info"] = token_info

sp = spotipy.Spotify(auth=token_info["access_token"])

# 🔹 Step 4: Fetch User's Playlists
st.subheader("🎶 Your Spotify Playlists")
playlists = sp.current_user_playlists()
playlist_options = {pl["name"]: pl["id"] for pl in playlists["items"]}

if not playlist_options:
    st.error("No playlists found. Make sure your Spotify account has at least one playlist.")
    st.stop()

selected_playlist = st.selectbox("Select a Playlist:", list(playlist_options.keys()))

# 🔹 Step 5: Fetch Playlist Songs
if selected_playlist:
    playlist_id = playlist_options[selected_playlist]
    tracks = sp.playlist_tracks(playlist_id)["items"]
    track_options = {t["track"]["name"]: t["track"]["id"] for t in tracks}

    if not track_options:
        st.error("This playlist has no songs.")
        st.stop()

    selected_track = st.selectbox("Select a Song:", list(track_options.keys()))

    if st.button("▶ Play Song"):
        track_id = track_options[selected_track]
        devices = sp.devices()["devices"]

        if not devices:
            st.error("No active Spotify device found. Open Spotify on your phone or PC and try again.")
        else:
            device_id = devices[0]["id"]  # Get user's active Spotify device
            sp.start_playback(device_id=device_id, uris=[f"spotify:track:{track_id}"])
            st.success(f"Playing 🎶 {selected_track} on Spotify!")

# 🔹 Step 6: Playback Controls
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("⏸ Pause"):
        sp.pause_playback()
        st.warning("Playback Paused.")

with col2:
    if st.button("⏩ Next Track"):
        sp.next_track()
        st.success("Skipped to Next Track!")

with col3:
    if st.button("⏪ Previous Track"):
        sp.previous_track()
        st.success("Playing Previous Track.")
