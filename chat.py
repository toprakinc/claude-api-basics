from dotenv import load_dotenv
from anthropic import Anthropic, APIConnectionError, APIStatusError

load_dotenv()
client = Anthropic()

SYSTEM_PROMPT = """You are a friendly customer support assistant for an online shoe store called StepUp.
Keep answers short.
If a question is not about the store, politely say you can only help with StepUp orders and products.

Store information:
- Returns are accepted within 30 days if the shoes are unworn.
- Shipping takes 2-4 business days.
- Shipping is free for orders over $50.
- Support email: support@stepup.example
"""

history = []

while True:
    user_text = input("You: ")
    if user_text == "quit":
        print("Bye!")
        break

    history.append({"role": "user", "content": user_text})

    try:
        response = client.messages.create(
            model="claude-haiku-5-5",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=history,
        )
    except APIConnectionError:
        print("Claude: Connection problem. Please try again.")
        history.pop()
        continue
    except APIStatusError as e:
        print(f"Claude: Something went wrong ({e.status_code}). Please try again.")
        history.pop()
        continue

    reply = ""
    for block in response.content:
        if block.type == "text":
            reply += block.text

    print("Claude:", reply)
    history.append({"role": "assistant", "content": reply})