from flask import Flask, render_template_string
import os

app = Flask(__name__)

# Read HTML files
def read_html_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"<h1>Page not found: {filename}</h1>"

@app.route('/')
def home():
    html_content = read_html_file('index.html')
    return render_template_string(html_content)

@app.route('/terms')
def terms():
    html_content = read_html_file('terms.html')
    return render_template_string(html_content)

@app.route('/privacy')
def privacy():
    html_content = read_html_file('privacy.html')
    return render_template_string(html_content)

@app.route('/health')
def health():
    return {"status": "ok"}, 200

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
