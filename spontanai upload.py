import openai
import os

# Set your OpenAI API Key
OPENAI_API_KEY = "your-openai-api-key"  # Replace with your actual API key

# Set the file name
FILE_NAME = "spontanai_train.jsonl"

def upload_file():
    try:
        # Set API key
        openai.api_key = OPENAI_API_KEY

        # Check if file exists
        if not os.path.exists(FILE_NAME):
            print(f"Error: {FILE_NAME} not found in the current directory.")
            return

        print(f"Uploading {FILE_NAME} to OpenAI for fine-tuning...")
        
        # Upload file
        response = openai.File.create(
            file=open(FILE_NAME, "rb"),
            purpose="fine-tune"
        )

        # Get the file ID
        file_id = response["id"]
        print(f"✅ Upload successful! File ID: {file_id}")

        return file_id

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    upload_file()
