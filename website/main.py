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
