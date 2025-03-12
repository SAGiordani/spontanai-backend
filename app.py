from flask import Flask, request, jsonify, render_template
import openai
import os
import json  # ✅ Import JSON module for safe parsing
from dotenv import load_dotenv
from flask_cors import CORS
from datetime import datetime
import csv

# Initialize Flask app
app = Flask(__name__, template_folder="templates")
CORS(app)  # Allow frontend to talk to backend

# ✅ Load environment variables
load_dotenv()

# ✅ Initialize OpenAI Client using the latest API format
openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ✅ Set up logging
LOG_FILE = "logs/activity_logs.csv"
os.makedirs("logs", exist_ok=True)  # Ensure logs directory exists

def log_to_csv(user_data, ai_response, stage="initial"):
    """Logs user requests and AI responses into a CSV file."""
    log_exists = os.path.isfile(LOG_FILE)

    try:
        with open(LOG_FILE, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            if not log_exists:
                writer.writerow(["Timestamp", "Stage", "User Data", "AI Response"])
            
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                stage,  
                json.dumps(user_data),  # ✅ Ensure JSON format
                json.dumps(ai_response)  # ✅ Ensure JSON format
            ])
        
        print(f"✅ Log saved successfully for {stage} stage!")

    except Exception as e:
        print(f"❌ Error writing to log file: {e}")

@app.route("/")
def home():
    """Serves the main webpage."""
    return render_template("index.html")

import json  # Ensure JSON module is imported

@app.route("/get_activity_options", methods=["POST"])
def get_activity_options():
    """Generates 3 structured activity suggestions based on user preferences and location."""
    try:
        data = request.json
        latitude = data.get("latitude", None)
        longitude = data.get("longitude", None)

        print(f"🔹 User Preferences: {data}")
        print(f"📍 User Location: {latitude}, {longitude}")

        # ✅ Force OpenAI to return structured JSON format
        user_prompt = (
            "You are an AI assistant that provides structured JSON responses."
            " Your task is to suggest three fun and unique activities based on user interest."
            " Always return a valid JSON object exactly in this format:"
            '{ "activities": ['
            '{ "title": "Activity 1", "summary": "Brief description of activity 1." },'
            '{ "title": "Activity 2", "summary": "Brief description of activity 2." },'
            '{ "title": "Activity 3", "summary": "Brief description of activity 3." }'
            ']}'
        )

        if latitude and longitude:
            user_prompt += f" The user is located at latitude {latitude} and longitude {longitude}, so prioritize local activities."

        response = openai_client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": user_prompt}],
            temperature=0.7,
            max_tokens=500
        )

        ai_response = response.choices[0].message.content
        print(f"🟢 Raw AI Response (Before Parsing): {ai_response}")  # Debugging

        # ✅ Validate JSON before parsing
        try:
            suggestions = json.loads(ai_response)
            print(f"✅ Successfully Parsed JSON: {suggestions}")  # Debugging
        except json.JSONDecodeError as e:
            print(f"❌ JSON Parsing Error: {e}")
            print(f"🔍 Attempting Manual Cleanup...")
            
            # ✅ Strip unnecessary formatting (e.g., triple backticks)
            ai_response_fixed = ai_response.strip("```json").strip("```").strip()
            try:
                suggestions = json.loads(ai_response_fixed)
                print(f"✅ Successfully Parsed JSON after cleanup: {suggestions}")
            except json.JSONDecodeError as e:
                print(f"❌ JSON Parsing Failed Again: {e}")
                return jsonify({"error": "AI returned invalid JSON format"}), 500

        # ✅ Log user request and AI response
        log_to_csv(data, suggestions, stage="initial")

        return jsonify(suggestions)

    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({"error": "AI processing failed"}), 500


@app.route("/get_final_activity", methods=["POST"])
def get_final_activity():
    """Generates a detailed activity plan for the user's chosen activity."""
    try:
        data = request.json
        chosen_activity = data["chosen_activity"]
        print(f"🔹 User selected activity: {chosen_activity}")

        response = openai_client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": f"Give a detailed plan for: {chosen_activity}"}],
            temperature=0.9,
            max_tokens=1000
        )

        final_suggestion = response.choices[0].message.content
        print(f"✅ Final activity details received!")

        # ✅ Log expanded activity details
        log_to_csv({"chosen_activity": chosen_activity}, final_suggestion, stage="final")

        return jsonify({"suggestion": final_suggestion})

    except Exception as e:
        print(f"❌ Error in final activity generation: {e}")
        return jsonify({"error": "AI processing failed"}), 500

if __name__ == "__main__":
    app.run(debug=True)
