from flask import Flask, render_template, request, redirect, session
import datetime
import requests
import google.generativeai as genai

app = Flask(__name__)
app.secret_key = "secret"

SPOTIFY_CLIENT_ID = "4b3ee564403d4f949f881d65692a0e57"
SPOTIFY_CLIENT_SECRET = "83eb71d8880e46e3a53e6052e319f3cc"
SPOTIFY_REDIRECT_URI = "http://127.0.0.1:5000/callback"
SCOPES = ['playlist-modify-private', 'playlist-modify-public', 'ugc-image-upload']
SCOPES_URL = "%20".join(SCOPES)

genai.configure(api_key="AIzaSyCqZiA0pNqc52G7BZiSW2MkEtk_s7pa85U")
model = genai.GenerativeModel(model_name="gemini-pro")

@app.route('/')
def index():
    return render_template('index.html', token = session['access_token'])

@app.route('/authenticate')
def authenticate():
    auth_url=(
        "https://accounts.spotify.com/authorize" +
        "?client_id=" + SPOTIFY_CLIENT_ID +
        "&response_type=token" +
        "&redirect_uri=" + SPOTIFY_REDIRECT_URI +
        "&scope=" + SCOPES_URL +
        "&show_dialog=true"
    )
    return redirect(auth_url)

@app.route('/callback')
def callback():
    if request.args.get('error'):
        return "ERROR: " + request.args.get('error')
    
    return render_template('callback.html')

@app.route('/process_callback')
def process_callback():
    access_token = request.args.get('access_token')
    if access_token:
        session['access_token'] = access_token
        return redirect('/')
    else:
        return "Error: Access token not provided in callback URL"


@app.route('/generate_playlist', methods=['POST'])
def generate_playlist():
    if request.method == 'POST':
        user_input = request.form['input_text']
        genai_response = model.generate_content(f"You will give me five songs and their artists. Add a '-' between the song and the artist. Insert a '%' after each song to separate them. Do not include a '%' after the last song. Do not include multiple songs from the same artist. Each song has to reflect or be related to this prompt: {user_input}. Be sympathetic.")
        playlist = genai_response.text.split("%")
        session['playlist'] = playlist
    if 'access_token' not in session:
        return "ERROR: Access Token Not Found in Session"
    if len(playlist) != 1:    
        access_token = session['access_token']
        get_id_headers = {
            "Authorization": "Bearer " + access_token,
        }
        create_playlist_headers = {
            "Authorization": "Bearer " + access_token,
            "Content-Type": 'application/json'
        }
        playlist_name = f"LeSunshine {datetime.date.today()}"
        data = {
            "name": playlist_name,
            "description": "A playlist generated by LeSunshine, for you."
        }

        spotify_id= requests.get("https://api.spotify.com/v1/me", headers=get_id_headers).json()['id']
        playlist_response = requests.post(f"https://api.spotify.com/v1/users/{spotify_id}/playlists", headers=create_playlist_headers, json=data)
        if playlist_response.status_code==201:
            session['playlist_id'] = playlist_response.json()['id']
            print("playlist_id: " + session['playlist_id'])
            return redirect('/add_songs')
        else:
            return "ERROR CREATING PLAYLIST" + playlist_response.text
    else: 
        return redirect('/generation_complete')
        
    
@app.route('/add_songs')    
def add_songs():
    playlist = session['playlist']
    song_id_uri = []
    for song in playlist:
        params = {
            "q": song,
            "type": "track",
            "limit": 1
        }
        search_headers = {
            "Authorization": "Bearer " + session['access_token']
        }
        search_response = requests.get("https://api.spotify.com/v1/search", params=params, headers=search_headers)
        song_search_results = search_response.json().get("tracks", {}).get("items", [])
        if len(song_search_results) > 0:
            current_id = str(song_search_results[0]['id'])
            song_id_uri.append("spotify:track:" + current_id)
    print("Track URIs: " + ", ".join(song_id_uri))
    data = {
        "uris": song_id_uri
    }
    add_songs_headers = {
        "Authorization": "Bearer " + session['access_token'],
        "Content-Type": "application/json"
    }
    add_songs_response = requests.post('https://api.spotify.com/v1/playlists/' + session['playlist_id'] + '/tracks', headers=add_songs_headers, json=data)
    if add_songs_response.status_code == 200:
        return redirect('/generation_complete')
    else:
        return "ERROR CODE: " + str(add_songs_response.status_code)
    
    
@app.route('/generation_complete')
def generation_complete():
    return render_template('result.html', playlist=session['playlist'])

if __name__ == '__main__':
    app.run(debug=True)
