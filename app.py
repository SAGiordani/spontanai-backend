import os
import openai
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend compatibility

# Set OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

# ✅ Home route for testing
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Flask app is running!"})

# ✅ Updated OpenAI API request
@app.route("/suggest", methods=["POST"])
def suggest_activity():
    try:
        data = request.get_json()
        user_input = data.get("interest", "something fun")

        # ✅ OpenAI's new API format
        client = openai.Client(api_key=openai.api_key)
        response = client.chat.completions.create(
            model="gpt-4",  # or "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": "You are an AI that suggests fun activities."},
                {"role": "user", "content": f"Suggest a fun and engaging activity for someone interested in {user_input}."}
            ]
        )

        suggestion = response.choices[0].message.content
        return jsonify({"suggestion": suggestion})

    except Exception as e:
        print("Error:", str(e))  # Debugging
        return jsonify({"error": str(e)}), 500

# ✅ Run the app
if __name__ == "__main__":
    app.run(debug=True)
