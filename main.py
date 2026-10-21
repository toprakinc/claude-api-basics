from dotenv import load_dotenv
from anthropic import Anthropic, APIConnectionError, APIStatusError

load_dotenv()
client = Anthropic()

try:
    response = client.messages.create(
        model="claude-haiku-5-5",
        max_tokens=200,
        messages=[
            {"role": "user", "content": "Hello! Introduce yourself in one sentence."}
        ],
    )
    print(response.content[0].text)
except APIConnectionError:
    print("Could not connect to the API. Check your internet connection.")
except APIStatusError as e:
    print(f"API error ({e.status_code}): {e.message}")