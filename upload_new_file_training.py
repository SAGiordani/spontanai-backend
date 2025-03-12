import openai
import os
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# File to upload
file_name = "spontanai_train.jsonl"

# Check if file exists
if not os.path.exists(file_name):
    raise FileNotFoundError(f"❌ Error: {file_name} not found in the current directory.")

# Upload new training file
with open(file_name, "rb") as file:
    response = openai.files.create(file=file, purpose="fine-tune")

# Get the new file ID
new_file_id = response.id
print(f"✅ New training file uploaded! File ID: {new_file_id}")
