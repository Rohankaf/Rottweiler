import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY  = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY     = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY     = os.getenv("GOOGLE_API_KEY")
GROQ_API_KEY       = os.getenv("GROQ_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
