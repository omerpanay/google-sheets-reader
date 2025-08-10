import os
from dotenv import load_dotenv

def setup_environment():
    """Set up the environment variables."""
    # Load .env file
    load_dotenv()
    
    # Google credentials will be handled dynamically
    # os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"
    
    # Ensure OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️ Warning: OPENAI_API_KEY not found in environment")