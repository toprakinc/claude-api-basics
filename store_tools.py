import json

# Fake order database (a real project would query a database or the store's API)
ORDERS = {
    "1001": {"status": "shipped", "carrier": "UPS", "eta": "2026-10-29"},
    "1002": {"status": "processing", "carrier": None, "eta": None},
}

# Tool descriptions sent to Claude
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


def get_order_status(order_id):
    """Return the order details, or an error if the order doesn't exist."""
    order = ORDERS.get(order_id)
    if order is None:
        return {"error": f"Order {order_id} not found"}
    return order


def run_tools(content):
    """Run every tool Claude asked for and return the results in API format."""
    results = []
    for block in content:
        if block.type == "tool_use":
            # Shown only for debugging, so we can see when the bot uses a tool
            print(f"  [tool] {block.name}({block.input})")
            if block.name == "get_order_status":
                result = get_order_status(block.input["order_id"])
            else:
                result = {"error": f"Unknown tool: {block.name}"}
            results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result),
                }
            )
    return results
