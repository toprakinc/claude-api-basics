import json
from datetime import date

# Fake order database (a real project would query a database or the store's API)
ORDERS = {
    "1001": {"status": "shipped", "carrier": "UPS", "eta": "2026-10-29"},
    "1002": {"status": "processing", "carrier": None, "eta": None},
    "1003": {"status": "delivered", "delivered_on": "2026-10-20"},
    "1004": {"status": "delivered", "delivered_on": "2026-09-01"},
}

RETURN_WINDOW_DAYS = 30

# Return requests created while the program runs (a real project would save these)
RETURNS = {}

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
    },
    {
        "name": "create_return_request",
        "description": (
            "Create a return request for a delivered order. "
            "Only call this after the customer has explicitly confirmed they want the return."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "The order ID to return",
                },
                "reason": {
                    "type": "string",
                    "description": "The customer's reason for the return, in a few words",
                },
            },
            "required": ["order_id", "reason"],
        },
    },
]


def get_order_status(order_id):
    """Return the order details, or an error if the order doesn't exist."""
    order = ORDERS.get(order_id)
    if order is None:
        return {"error": f"Order {order_id} not found"}
    return order


def create_return_request(order_id, reason):
    """Create a return if the order is eligible; otherwise explain why not."""
    # Business rules are checked here in code, not left to the model
    order = ORDERS.get(order_id)
    if order is None:
        return {"error": f"Order {order_id} not found"}

    if order["status"] != "delivered":
        return {
            "error": f"Order {order_id} has not been delivered yet, so it can't be returned"
        }

    days_since_delivery = (
        date.today() - date.fromisoformat(order["delivered_on"])
    ).days
    if days_since_delivery > RETURN_WINDOW_DAYS:
        return {
            "error": f"Order {order_id} was delivered {days_since_delivery} days ago; "
            f"returns are only accepted within {RETURN_WINDOW_DAYS} days"
        }

    if order_id in RETURNS:
        return {
            "error": f"A return for order {order_id} already exists: {RETURNS[order_id]['return_id']}"
        }

    return_id = f"R-{order_id}"
    RETURNS[order_id] = {"return_id": return_id, "reason": reason}
    return {"return_id": return_id, "status": "created"}


def run_tools(content):
    """Run every tool Claude asked for and return the results in API format."""
    results = []
    for block in content:
        if block.type == "tool_use":
            # Shown only for debugging, so we can see when the bot uses a tool
            print(f"  [tool] {block.name}({block.input})")
            if block.name == "get_order_status":
                result = get_order_status(block.input["order_id"])
            elif block.name == "create_return_request":
                result = create_return_request(
                    block.input["order_id"], block.input["reason"]
                )
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
