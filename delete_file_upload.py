import openai
from dotenv import load_dotenv
import os

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Replace with your old file ID
file_id = "file-QZSWYdkF6cCUWefw2hAYv3"

openai.files.delete(file_id)
print(f"✅ Deleted old training file: {file_id}")
