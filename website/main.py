from flask import Flask, render_template, request
import google.generativeai as genai

app = Flask(__name__)

genai.configure(api_key="AIzaSyCqZiA0pNqc52G7BZiSW2MkEtk_s7pa85U")
model = genai.GenerativeModel(model_name="gemini-pro")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_playlists', methods=['POST'])
def generate_playlists():
    if request.method == 'POST':
        user_input = request.form['input_text']
        response = model.generate_content(f"You will give me five songs and their artists. Add a '-' between the song and the artist. Separate each song with nothing but a '%'. Each song has to be related to this prompt: {user_input}.")
        playlists = response.text.split("%")
        return render_template('result.html', playlists=playlists)

if __name__ == '__main__':
    app.run(debug=True)
