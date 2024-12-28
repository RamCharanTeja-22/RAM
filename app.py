from flask import Flask, jsonify, send_from_directory
import os
from flask_cors import CORS  # Importing CORS for handling cross-origin requests

app = Flask(__name__, static_folder='static', static_url_path='/static')  # Static folder configuration
CORS(app)  # Enable CORS to allow frontend to communicate with this backend

# Backend Content for explanations
EXPLANATIONS = {
    "Grammar": {
        "text": "Grammar Explanation\n\nWords are categorized into Nouns, Pronouns, Verbs, Adjectives, etc.\n\nExamples:\n\n- Nouns: Names of people, places, or things (e.g., teacher).\n- Verbs: Action words (e.g., run, jump).\n- Adjectives: Describe nouns (e.g., happy, red)."
    },
    "Prefix": {
        "text": "Prefix Explanation\n\nA prefix is a group of letters placed at the beginning of a word to modify its meaning.\n\nExamples:\n\n- Un-: Not (e.g., unhappy).\n- Re-: Again (e.g., rewrite)."
    }
}

# Route to serve the index.html from the static folder
@app.route("/")
def index():
    return send_from_directory('static', 'index.html')

# Route to serve content for a specific topic
@app.route("/content/<topic>")
def get_content(topic):
    explanation = EXPLANATIONS.get(topic, {"text": "No content available"})
    return jsonify({"text": explanation["text"]})

if __name__ == "__main__":
    # Ensure the app runs on the correct port for deployment
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
