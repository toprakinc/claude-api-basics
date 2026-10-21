from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic()

history = []

while True:
    user_text = input("You: ")
    if user_text == "quit":
        print("Bye!")
        break

    history.append({"role": "user", "content": user_text})

    response = client.messages.create(
        model="claude-haiku-5-5",
        max_tokens=1024,
        messages=history,
    )

    reply = ""
    for block in response.content:
        if block.type == "text":
            reply += block.text

    print("Claude:", reply)
    history.append({"role": "assistant", "content": reply})