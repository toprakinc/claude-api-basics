from dotenv import load_dotenv
from anthropic import Anthropic, APIConnectionError, APIStatusError

# Store tools live in one place, shared by every script that needs them
from store_tools import TOOLS, run_tools

load_dotenv()
client = Anthropic()

MODEL = "claude-haiku-5-5"

SYSTEM_PROMPT = """You are a friendly customer support assistant for an online shoe store called StepUp.
Keep answers short.
If a question is not about the store, politely say you can only help with StepUp orders and products.

When a customer asks about an order, use the get_order_status tool. Never guess order details.
If an order is not found, ask the customer to double-check the order number.
If they still need help, they can email support@stepup.example.

Store information:
- Returns are accepted within 30 days if the shoes are unworn.
- Shipping takes 2-4 business days.
- Shipping is free for orders over $50.
"""


def call_claude(history):
    """Send the whole conversation to Claude, with the store's tools available."""
    return client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        tools=TOOLS,
        messages=history,
    )


if __name__ == "__main__":
    history = []

    while True:
        user_text = input("You: ")
        if user_text == "quit":
            print("Bye!")
            break

        # Remember where this turn starts, so we can undo it if a request fails
        turn_start = len(history)
        history.append({"role": "user", "content": user_text})

        try:
            response = call_claude(history)
            # Claude may need several tool calls before it can answer
            while response.stop_reason == "tool_use":
                history.append({"role": "assistant", "content": response.content})
                history.append({"role": "user", "content": run_tools(response.content)})
                response = call_claude(history)
        except APIConnectionError:
            print("Claude: Connection problem. Please try again.")
            del history[turn_start:]
            continue
        except APIStatusError as e:
            print(f"Claude: Something went wrong ({e.status_code}). Please try again.")
            del history[turn_start:]
            continue

        reply = ""
        for block in response.content:
            if block.type == "text":
                reply += block.text

        print("Claude:", reply)
        history.append({"role": "assistant", "content": reply})
