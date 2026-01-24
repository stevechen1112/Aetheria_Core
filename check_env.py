from dotenv import load_dotenv
import os

load_dotenv()

key = os.getenv('GEMINI_API_KEY')

print(f'Key exists: {key is not None}')
print(f'Key value: {repr(key)}')
print(f'Key length: {len(key) if key else 0}')
if key:
    print(f'First 10 chars: {key[:10]}')
    print(f'Stripped: {repr(key.strip())}')
