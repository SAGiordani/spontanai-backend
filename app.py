from flask import Flask, request, jsonify, send_from_directory
import os
import openai
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, static_folder="static")
CORS(app)  # Enable CORS for frontend compatibility

# Set OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/")
def serve_frontend():
    return send_from_directory("static", "index.html")

@app.route("/suggest", methods=["POST"])
def suggest_activity():
    try:
        data = request.get_json()
        user_input = data.get("interest", "something fun")

        client = openai.Client(api_key=openai.api_key)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an AI that suggests fun activities."},
                {"role": "user", "content": f"Suggest a fun and engaging activity for someone interested in {user_input}."}
            ]
        )

        suggestion = response.choices[0].message.content
        return jsonify({"suggestion": suggestion})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
