from flask import Flask
from pyngrok import ngrok

# Create a minimal Flask app
app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello, World!"

if __name__ == '__main__':
    # Start ngrok tunnel
    public_url = ngrok.connect(5000).public_url
    print(f" * ngrok tunnel \"{public_url}\" -> \"http://127.0.0.1:5000\"")
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000) 