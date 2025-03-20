from flask import Flask, request, jsonify, render_template
import openai
import os
import json
import psycopg2  # ✅ PostgreSQL client
from dotenv import load_dotenv
from flask_cors import CORS
from datetime import datetime
from psycopg2 import pool

# Initialize Flask app
app = Flask(__name__, template_folder="templates")
CORS(app)  # Allow frontend to talk to backend

# ✅ Load environment variables
load_dotenv()

# ✅ Initialize OpenAI Client
openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ✅ Set up PostgreSQL connection using Render's DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")  # Render provides this in environment variables


# ✅ Use a connection pool with up to 10 connections
db_pool = pool.SimpleConnectionPool(1, 10, dsn=DATABASE_URL)

def get_db_connection():
    return db_pool.getconn()

def release_db_connection(conn):
    db_pool.putconn(conn)


# Function to connect to the database
def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode="require")  # Render requires SSL

# ✅ Create table if it doesn’t exist
def init_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_logs (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                stage TEXT NOT NULL,
                user_data JSONB NOT NULL,
                ai_response JSONB NOT NULL
            );
        """)
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Database initialized successfully!")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")

# ✅ Replace CSV logging with PostgreSQL logging
def log_to_db(user_data, ai_response, stage="initial"):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        truncated_response = ai_response[:500] if isinstance(ai_response, str) else json.dumps(ai_response)[:500]

        cursor.execute(
            "INSERT INTO api_logs (stage, user_data, ai_response) VALUES (%s, %s, %s)",
            (stage, json.dumps(user_data), truncated_response)
        )
        
        conn.commit()
        cursor.close()
        release_db_connection(conn)  # ✅ Release connection back to the pool
        print(f"✅ Log saved successfully for {stage} stage!")
    except Exception as e:
        print(f"❌ Error writing to database: {e}")

# ✅ Initialize the database on startup
init_db()

@app.route("/")
def home():
    """Serves the main webpage."""
    return render_template("index.html")

@app.route("/get_activity_options", methods=["POST"])
def get_activity_options():
    """Generates 3 structured activity suggestions based on user preferences."""
    try:
        data = request.json
        latitude = data.get("latitude")
        longitude = data.get("longitude")

        print(f"🔹 User Preferences: {data}")
        print(f"📍 User Location: {latitude}, {longitude}")

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
        print(f"🟢 Raw AI Response: {ai_response}")

        # ✅ Validate JSON before parsing
        try:
            suggestions = json.loads(ai_response)
        except json.JSONDecodeError:
            print("❌ AI response is not valid JSON.")
            return jsonify({"error": "AI returned invalid JSON format"}), 500

        # ✅ Log user request and AI response in PostgreSQL
        log_to_db(data, suggestions, stage="initial")

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

        # ✅ Log expanded activity details in PostgreSQL
        log_to_db({"chosen_activity": chosen_activity}, final_suggestion, stage="final")

        return jsonify({"suggestion": final_suggestion})

    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({"error": "AI processing failed"}), 500

if __name__ == "__main__":
    app.run(debug=True)
