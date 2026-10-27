import os
import json
from dotenv import load_dotenv
from anthropic import Anthropic

# Minimal tool calling example: one question, one tool call, one answer
from store_tools import TOOLS, get_order_status

load_dotenv()
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

MODEL = "claude-haiku-5-5"

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
