import os
import openai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve API key from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("❌ API key not found! Make sure it's set in the .env file.")

# Initialize OpenAI client
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# File to upload
FILE_NAME = "spontanai_train.jsonl"

def upload_file():
    try:
        if not os.path.exists(FILE_NAME):
            print(f"Error: {FILE_NAME} not found in the current directory.")
            return

        print(f"Uploading {FILE_NAME} to OpenAI for fine-tuning...")

        # Upload file
        with open(FILE_NAME, "rb") as file:
            response = client.files.create(file=file, purpose="fine-tune")

        # Get file ID
        file_id = response.id
        print(f"✅ Upload successful! File ID: {file_id}")

        return file_id

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    upload_file()
