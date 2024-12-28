from flask import Flask, render_template_string, jsonify

app = Flask(__name__)

# HTML, CSS, and JS directly integrated
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EdTech Platform</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
        }
        header {
            background-color: #0073e6;
            color: white;
            padding: 10px 20px;
            text-align: center;
        }
        .grades, .subjects, .topics {
            text-align: center;
            margin: 20px;
        }
        button {
            margin: 10px;
            padding: 10px 20px;
            border: none;
            color: white;
            background-color: #0073e6;
            border-radius: 5px;
            cursor: pointer;
        }
        button:hover {
            background-color: #005bb5;
        }
        .hidden {
            display: none;
        }
        .content-box {
            margin: 20px auto;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 5px;
            max-width: 600px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        h3 {
            color: #0073e6;
        }
        #explanation {
            animation: fadeIn 0.5s steps(1, end) both;
            white-space: pre-wrap;
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
    </style>
</head>
<body>
    <header>
        <h1>EdTech Platform</h1>
    </header>

    <!-- Grade Selection -->
    <section class="grades">
        <h2>Select Your Grade</h2>
        <button onclick="loadSubjects('10th')">10th Grade</button>
        <button onclick="loadSubjects('11th')">11th Grade</button>
        <button onclick="loadSubjects('12th')">12th Grade</button>
    </section>

    <!-- Subjects -->
    <section class="subjects hidden" id="subjects-section">
        <h2>Subjects</h2>
        <div id="subjects"></div>
    </section>

    <!-- Topics -->
    <section class="topics hidden" id="topics-section">
        <h2>Topics</h2>
        <div id="topics"></div>
    </section>

    <!-- Content Section -->
    <section class="content-box hidden" id="content-box">
        <h3 id="content-title"></h3>
        <div id="explanation"></div>
        <button class="hidden" id="mark-complete" onclick="showVideo()">Mark as Complete</button>
        <video id="video-player" width="100%" controls class="hidden">
            <source src="{{ url_for('static', filename='videos/WhatsApp Video 2024-12-17 at 20.44.25_206b2bae.mp4') }}" type="video/mp4">
            Your browser does not support the video tag.
        </video>
    </section>

    <script>
        function loadSubjects(grade) {
            const subjects = {
                "10th": ["English", "Maths", "Science", "Social"],
                "11th": ["English", "Physics", "Chemistry"],
                "12th": ["English", "Physics", "Chemistry"]
            };
            const subjectDiv = document.getElementById("subjects");
            subjectDiv.innerHTML = "";
            subjects[grade].forEach(subject => {
                subjectDiv.innerHTML += `<button onclick="loadTopics('${subject}')">${subject}</button>`;
            });
            document.getElementById("subjects-section").classList.remove("hidden");
            document.getElementById("topics-section").classList.add("hidden");
            document.getElementById("content-box").classList.add("hidden");
        }

        function loadTopics(subject) {
            const topics = {
                "English": ["Grammar", "Prefix"],
                "Maths": ["Algebra", "Geometry"],
                "Science": ["Physics Basics", "Chemistry Basics"]
            };
            const topicsDiv = document.getElementById("topics");
            topicsDiv.innerHTML = "";
            (topics[subject] || []).forEach(topic => {
                topicsDiv.innerHTML += `<button onclick="loadContent('${topic}')">${topic}</button>`;
            });
            document.getElementById("topics-section").classList.remove("hidden");
            document.getElementById("content-box").classList.add("hidden");
        }

        function loadContent(topic) {
            fetch(`/content/${topic}`)
                .then(response => response.json())
                .then(data => {
                    const explanationDiv = document.getElementById("explanation");
                    const markCompleteButton = document.getElementById("mark-complete");
                    document.getElementById("content-title").innerText = topic;
                    explanationDiv.innerHTML = "";
                    markCompleteButton.classList.add("hidden");
                    document.getElementById("video-player").classList.add("hidden");

                    const words = data.text.split(" ");
                    let index = 0;
                    const interval = setInterval(() => {
                        explanationDiv.innerHTML += words[index] + " ";
                        index++;
                        if (index >= words.length) {
                            clearInterval(interval);
                            markCompleteButton.classList.remove("hidden");
                        }
                    }, 200);
                    document.getElementById("content-box").classList.remove("hidden");
                });
        }

        function showVideo() {
            document.getElementById("video-player").classList.remove("hidden");
        }
    </script>
</body>
</html>
"""

# Backend Content
EXPLANATIONS = {
    "Grammar": {
        "text": "Grammar Explanation\n\nWords are categorized into Nouns, Pronouns, Verbs, Adjectives, etc.\n\nExamples:\n\n- Nouns: Names of people, places, or things (e.g., teacher).\n- Verbs: Action words (e.g., run, jump).\n- Adjectives: Describe nouns (e.g., happy, red)."
    },
    "Prefix": {
        "text": "Prefix Explanation\n\nA prefix is a group of letters placed at the beginning of a word to modify its meaning.\n\nExamples:\n\n- Un-: Not (e.g., unhappy).\n- Re-: Again (e.g., rewrite)."
    }
}

@app.route("/")
def index():
    return render_template_string(HTML_PAGE)

@app.route("/content/<topic>")
def get_content(topic):
    explanation = EXPLANATIONS.get(topic, {"text": "No content available"})
    return jsonify({"text": explanation["text"]})

if __name__ == "__main__":
    app.run(debug=True)
