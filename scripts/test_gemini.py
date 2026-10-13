import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
key = os.getenv("GEMINI_API_KEY")
print("Key loaded:", bool(key))

client = genai.Client(api_key=key)
reply = client.models.generate_content(
    model="gemini-3.5-flash-lite",
    contents="Reply with exactly: Gemini works.",
)
print(reply.text)