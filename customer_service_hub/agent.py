"""Agent 3 - Customer Service Hub (multi-agent system).

Business use case: one front-desk chatbot that routes a customer to the
right specialist. A root 'orchestrator' agent understands the request and
delegates to sub-agents: billing or technical support. Each sub-agent has
its own instruction and tools, so each stays simple and testable.
"""

from google.adk.agents import Agent

# --- Mock data ---
INVOICES = {
    "inv-1001": {"amount": "Rs 4,999", "status": "paid", "period": "Sep 2026"},
    "inv-1002": {"amount": "Rs 4,999", "status": "unpaid", "period": "Oct 2026"},
}


def get_invoice_status(invoice_id: str) -> dict:
    """Retrieves the status and amount of an invoice.

    Args:
        invoice_id: The invoice number, e.g. 'INV-1002'.

    Returns:
        dict with amount/status/period, or an 'error_message' if not found.
    """
    inv = INVOICES.get(invoice_id.lower())
    if not inv:
        return {"status": "error", "error_message": f"Invoice '{invoice_id}' not found."}
    return {"status": "success", "invoice_id": invoice_id.upper(), **inv}


def run_diagnostics(service_name: str) -> dict:
    """Runs a basic health check on a named service.

    Args:
        service_name: The service the customer is asking about, e.g. 'api-gateway'.

    Returns:
        dict with a simple diagnostic report.
    """
    # Mock: everything is healthy except a known degraded service.
    if service_name.lower() == "api-gateway":
        return {"status": "success", "service": service_name, "report": "degraded: 12% error rate in last hour"}
    return {"status": "success", "service": service_name, "report": "healthy: no errors in last 24h"}


billing_agent = Agent(
    model="gemini-2.5-flash",
    name="billing_agent",
    description="Handles invoices, payments, refunds and pricing questions.",
    instruction=(
        "You are the billing specialist. For invoice questions, call get_invoice_status "
        "and report amount, period and paid/unpaid status in one line. "
        "If the question is not about billing, say so - the orchestrator will re-route."
    ),
    tools=[get_invoice_status],
)

tech_support_agent = Agent(
    model="gemini-2.5-flash",
    name="tech_support_agent",
    description="Handles outages, errors and service health questions.",
    instruction=(
        "You are the technical support specialist. For any error/outage/health question, "
        "call run_diagnostics for the service and explain the report in plain language. "
        "If it is degraded, suggest opening an incident ticket. Keep answers to 2-3 lines."
    ),
    tools=[run_diagnostics],
)

root_agent = Agent(
    model="gemini-2.5-flash",
    name="customer_service_hub",
    description="Front-desk assistant that routes customers to billing or technical support.",
    instruction=(
        "You are the front desk of a cloud company's support chat. "
        "Read the customer's message and delegate: "
        "billing_agent for anything about invoices, payments, refunds or pricing; "
        "tech_support_agent for outages, errors and service health. "
        "If it is neither, answer briefly yourself. "
        "Always tell the customer which specialist handled their request."
    ),
    sub_agents=[billing_agent, tech_support_agent],
)
