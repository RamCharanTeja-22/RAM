from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS  # Import the CORS module

app = Flask(__name__, static_folder='static', static_url_path='')

# Enable CORS for all routes
CORS(app)

# Backend Content
EXPLANATIONS = {
    "Grammar": {
        "text": "Grammar Explanation\n\nWords are categorized into Nouns, Pronouns, Verbs, Adjectives, etc.\n\nExamples:\n\n- Nouns: Names of people, places, or things (e.g., teacher).\n- Verbs: Action words (e.g., run, jump).\n- Adjectives: Describe nouns (e.g., happy, red)."
    },
    "Prefix": {
        "text": "Prefix Explanation\n\nA prefix is a group of letters placed at the beginning of a word to modify its meaning.\n\nExamples:\n\n- Un-: Not (e.g., unhappy).\n- Re-: Again (e.g., rewrite)."
    }
}

@app.route("/content/<topic>")
def get_content(topic):
    explanation = EXPLANATIONS.get(topic, {"text": "No content available"})
    return jsonify({"text": explanation["text"]})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
