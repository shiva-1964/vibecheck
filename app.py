from flask import Flask, request, jsonify, send_from_directory, session
import requests
import sqlite3
import json


app = Flask(__name__, static_folder='.')

app.secret_key = "supersecretkey"

# ─── HuggingFace API Setup ─────────────────────────────────

HF_TOKEN = "your_token_here"

HEADERS = {
    "Authorization": f"Bearer {HF_TOKEN}"
}

TOXICITY_URL = "https://api-inference.huggingface.co/models/unitary/toxic-bert"

EMOTION_URL = "https://api-inference.huggingface.co/models/j-hartmann/emotion-english-distilroberta-base"


# ─── Routes ────────────────────────────────────────────────

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('.', path)


@app.route('/dashboard')
def dashboard_page():

    return send_from_directory('.', 'dashboard.html')


@app.route('/history')
def history_page():

    return send_from_directory('.', 'history.html')


# ─── Signup Page ───────────────────────────────────────────

@app.route('/signup-page')
def signup_page():

    return send_from_directory('.', 'signup.html')


# ─── Login Page ────────────────────────────────────────────

@app.route('/login')
def login_page():

    return send_from_directory('.', 'login.html')


# ─── Signup API ────────────────────────────────────────────

@app.route('/signup', methods=['POST'])
def signup():

    data = request.get_json()

    username = data.get('username')

    password = data.get('password')

    try:

        conn = sqlite3.connect('database.db')

        cursor = conn.cursor()

        cursor.execute('''
        INSERT INTO users (username, password)
        VALUES (?, ?)
        ''', (
            username,
            password
        ))

        conn.commit()

        conn.close()

        return jsonify({
            "success": True,
            "message": "Account created successfully!"
        })

    except Exception:

        return jsonify({
            "success": False,
            "message": "Username already exists."
        })


# ─── Login API ─────────────────────────────────────────────

@app.route('/login', methods=['POST'])
def login():

    data = request.get_json()

    username = data.get('username')

    password = data.get('password')

    conn = sqlite3.connect('database.db')

    cursor = conn.cursor()

    cursor.execute('''
    SELECT * FROM users
    WHERE username = ? AND password = ?
    ''', (
        username,
        password
    ))

    user = cursor.fetchone()

    conn.close()

    if user:

        session['username'] = username

        return jsonify({
            "success": True,
            "message": "Login successful!"
        })

    else:

        return jsonify({
            "success": False,
            "message": "Invalid credentials."
        })


# ─── Analyze Route ─────────────────────────────────────────
@app.route('/analyze', methods=['POST'])
def analyze():

    try:

        data = request.get_json()

        text = data.get('text', '').strip()

        if not text:

            return jsonify({
                'error': 'No text provided'
            }), 400


        # ─── Dynamic Emotion Logic ───────────────────────

        text_lower = text.lower()

        # Default neutral values

        toxicity_score = 0.1

        emotions = {
            "anger": 0.05,
            "sadness": 0.05,
            "joy": 0.1,
            "neutral": 0.8
        }

        # Angry comments

        if any(word in text_lower for word in [

            "stupid",
            "idiot",
            "hate",
            "useless",
            "dumb",
            "shut up"

        ]):

            toxicity_score = 0.85

            emotions = {
                "anger": 0.8,
                "sadness": 0.1,
                "joy": 0.1
            }

        # Sad comments

        elif any(word in text_lower for word in [

            "sad",
            "lonely",
            "depressed",
            "cry",
            "upset"

        ]):

            toxicity_score = 0.3

            emotions = {
                "anger": 0.1,
                "sadness": 0.8,
                "joy": 0.1
            }

        # Happy comments

        elif any(word in text_lower for word in [

            "happy",
            "amazing",
            "love",
            "excited",
            "beautiful",
            "great"

        ]):

            toxicity_score = 0.05

            emotions = {
                "anger": 0.05,
                "sadness": 0.05,
                "joy": 0.9
            }


        score_pct = toxicity_score * 100


        # ─── Verdict Logic ────────────────────────────────

        if score_pct < 20:

            verdict_icon = "✅"

            verdict = (
                "This text looks healthy and respectful."
            )

        elif score_pct < 50:

            verdict_icon = "⚠️"

            verdict = (
                "Mild toxicity detected."
            )

        elif score_pct < 75:

            verdict_icon = "🔴"

            verdict = (
                "High toxicity detected."
            )

        else:

            verdict_icon = "☠️"

            verdict = (
                "Extreme toxicity detected."
            )


        # ─── Positive Rewrite Suggestion ──────────────────

        rewrite = generate_rewrite(text, score_pct)


        # ─── Save to Database ─────────────────────────────

        username = session.get('username', 'guest')

        conn = sqlite3.connect('database.db')

        cursor = conn.cursor()

        cursor.execute('''
        INSERT INTO analyses
        (username, text, toxicity_score, emotions, verdict)
        VALUES (?, ?, ?, ?, ?)
        ''', (
            username,
            text,
            toxicity_score,
            json.dumps(emotions),
            verdict
        ))

        conn.commit()

        conn.close()


        # ─── Final Response ───────────────────────────────

        return jsonify({

            'toxicity_score': round(toxicity_score, 3),

            'emotions': emotions,

            'verdict_icon': verdict_icon,

            'verdict': verdict,

            'rewrite': rewrite

        })

    except Exception as e:

        print("SERVER ERROR:", str(e))

        return jsonify({
            "error": str(e)
        }), 500

        # ─── Verdict Logic ────────────────────────────────

        if score_pct < 20:

            verdict_icon = "✅"

            verdict = (
                "This text looks healthy and respectful."
            )

        elif score_pct < 50:

            verdict_icon = "⚠️"

            verdict = (
                "Mild toxicity detected."
            )

        elif score_pct < 75:

            verdict_icon = "🔴"

            verdict = (
                "High toxicity detected."
            )

        else:

            verdict_icon = "☠️"

            verdict = (
                "Extreme toxicity detected."
            )

        # ─── Positive Rewrite Suggestion ──────────────────

        rewrite = generate_rewrite(text, score_pct)

        # ─── Save to Database ─────────────────────────────

        username = session.get('username', 'guest')

        conn = sqlite3.connect('database.db')

        cursor = conn.cursor()

        cursor.execute('''
        INSERT INTO analyses
        (username, text, toxicity_score, emotions, verdict)
        VALUES (?, ?, ?, ?, ?)
        ''', (
            username,
            text,
            toxicity_score,
            json.dumps(emotions),
            verdict
        ))

        conn.commit()

        conn.close()

        # ─── Final Response ───────────────────────────────

        return jsonify({

            'toxicity_score': round(toxicity_score, 3),

            'emotions': emotions,

            'verdict_icon': verdict_icon,

            'verdict': verdict,

            'rewrite': rewrite

        })

    except Exception as e:

        print("SERVER ERROR:", str(e))

        return jsonify({
            "error": str(e)
        }), 500


# ─── History Data Route ────────────────────────────────────

@app.route('/history-data')
def history_data():

    username = session.get('username', 'guest')

    conn = sqlite3.connect('database.db')

    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute('''
    SELECT * FROM analyses
    WHERE username = ?
    ORDER BY timestamp DESC
    ''', (username,))

    rows = cursor.fetchall()

    conn.close()

    data = []

    for row in rows:

        data.append({
            "id": row["id"],
            "text": row["text"],
            "toxicity_score": row["toxicity_score"],
            "verdict": row["verdict"],
            "timestamp": row["timestamp"]
        })

    return jsonify(data)


# ─── Rewrite Function ──────────────────────────────────────

def generate_rewrite(text, score):

    if score < 20:

        return "No rewrite needed."

    replacements = {

        "stupid": "misinformed",

        "idiot": "person",

        "hate": "dislike",

        "useless": "could improve",

        "dumb": "unaware",

        "shut up": "please listen",

        "worst": "not very good"

    }

    rewritten = text.lower()

    for bad, good in replacements.items():

        rewritten = rewritten.replace(bad, good)

    return rewritten.capitalize()


# ─── Logout ────────────────────────────────────────────────

@app.route('/logout')
def logout():

    session.clear()

    return send_from_directory('.', 'login.html')


# ─── Run App ───────────────────────────────────────────────

if __name__ == '__main__':
    app.run(debug=True, port=5000)