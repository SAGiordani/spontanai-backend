import openai
import os
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Replace with your actual file ID from the upload step
file_id = "file-C121JJd86VGcrtEMbmcqj3"

# Start fine-tuning process
try:
    fine_tune_response = openai.fine_tuning.jobs.create(
        training_file=file_id,
        model="gpt-3.5-turbo"
    )

    print(f"✅ Fine-tuning job started! Job ID: {fine_tune_response.id}")
    print("Check progress at: https://platform.openai.com/fine-tunes")

except Exception as e:
    print(f"❌ Error starting fine-tuning: {e}")
