from flask import Flask, render_template, request
import google.generativeai as genai

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_text', methods=['POST'])
def process_text():
    if request.method == 'POST':
        job_desc = request.form['input_text']
        # Put Gemini Code Here
        processed_text = job_desc.upper()  # Example: Convert text to uppercase
        return render_template('result.html', processed_text=processed_text)

if __name__ == '__main__':
    app.run(debug=True)

'''
import google.generativeai as genai

genai.configure(api_key="AIzaSyCqZiA0pNqc52G7BZiSW2MkEtk_s7pa85U")

model = genai.GenerativeModel(model_name="gemini-pro")

response = model.generate_content("Tell me a story about a magic backpack.")

print(response.text)

from PIL import Image
img = Image.open("~/cat.jpg")
'''