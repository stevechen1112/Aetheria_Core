from dotenv import load_dotenv
import os

load_dotenv()

key = os.getenv('GEMINI_API_KEY')

print(f'Key exists: {key is not None}')
print(f'Key length: {len(key) if key else 0}')
if key:
    masked = f"{key[:4]}...{key[-4:]}" if len(key) >= 8 else "****"
    print(f'Key masked: {masked}')
    # Avoid printing the full key value
