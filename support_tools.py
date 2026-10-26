import os
import json
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

MODEL = "claude-haiku-5-5"

# Fake order database (a real project would query a database or the store's API)
ORDERS = {
    "1001": {"status": "shipped", "carrier": "UPS", "eta": "2026-10-29"},
    "1002": {"status": "processing", "carrier": None, "eta": None},
}


def get_order_status(order_id):
    """Return the order details, or an error if the order doesn't exist."""
    order = ORDERS.get(order_id)
    if order is None:
        return {"error": f"Order {order_id} not found"}
    return order


# Describe the tool so Claude knows what it does and what input it needs
TOOLS = [
    {
        "name": "get_order_status",
        "description": "Look up the current status of a customer's order by its order ID.",
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "The order ID, for example '1001'",
                }
            },
            "required": ["order_id"],
        },
    }
]

messages = [{"role": "user", "content": "Where is my order 1001?"}]

# First call: Claude decides whether it needs a tool
response = client.messages.create(
    model=MODEL, max_tokens=1000, tools=TOOLS, messages=messages
)

if response.stop_reason == "tool_use":
    # Keep Claude's tool request in the history so it remembers what it asked for
    messages.append({"role": "assistant", "content": response.content})

    tool_results = []
    for block in response.content:
        if block.type == "tool_use":
            # Run our real Python function with the input Claude chose
            result = get_order_status(block.input["order_id"])
            print("Tool result:", result)
            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result),
                }
            )

    # Tool results are sent back to Claude as a user message
    messages.append({"role": "user", "content": tool_results})

    # Second call: Claude writes the final answer using the tool result
    response = client.messages.create(
        model=MODEL, max_tokens=1000, tools=TOOLS, messages=messages
    )

for block in response.content:
    if block.type == "text":
        print("Claude:", block.text)
