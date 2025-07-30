from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DB_PATH = os.getenv("DB_PATH", "action_log.db")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set. Please set it in the .env file.")
