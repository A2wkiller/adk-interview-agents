"""Agent 1 - Support Ticket Triage (single agent + tools).

Business use case: a small cloud company gets support tickets by email/chat.
This agent reads a ticket, classifies it, checks the customer's plan, and
assigns a priority - the boring first pass a human L1 engineer does today.
"""

from google.adk.agents import Agent

# --- Mock data: in production this comes from a CRM / database ---
CUSTOMER_PLANS = {
    "acme": "enterprise",
    "globex": "startup",
    "initech": "free",
}


def classify_ticket(ticket_text: str) -> dict:
    """Classifies a raw support ticket into a category.

    Args:
        ticket_text: The full text of the customer's support ticket.

    Returns:
        dict with 'category' (billing | technical | account) and 'keywords' found.
    """
    text = ticket_text.lower()
    if any(w in text for w in ("invoice", "charged", "billing", "refund", "payment")):
        return {"category": "billing", "keywords": "money-related words found"}
    if any(w in text for w in ("down", "error", "500", "crash", "timeout", "slow")):
        return {"category": "technical", "keywords": "incident-related words found"}
    return {"category": "account", "keywords": "no strong signal, default bucket"}


def get_customer_plan(company_name: str) -> dict:
    """Looks up which pricing plan a customer company is on.

    Args:
        company_name: The customer's company name (e.g. 'Acme').

    Returns:
        dict with 'plan' (enterprise | startup | free | unknown).
    """
    plan = CUSTOMER_PLANS.get(company_name.lower(), "unknown")
    return {"company": company_name, "plan": plan}


def set_priority(category: str, plan: str) -> dict:
    """Decides ticket priority from its category and the customer's plan.

    Args:
        category: Ticket category from classify_ticket (billing | technical | account).
        plan: Customer plan from get_customer_plan (enterprise | startup | free | unknown).

    Returns:
        dict with 'priority' (P1-P4) and the 'reason' for that choice.
    """
    if category == "technical" and plan == "enterprise":
        return {"priority": "P1", "reason": "paying enterprise customer with a live incident"}
    if category == "technical":
        return {"priority": "P2", "reason": "technical issue, non-enterprise plan"}
    if category == "billing" and plan in ("enterprise", "startup"):
        return {"priority": "P2", "reason": "billing issue for a paying customer"}
    return {"priority": "P3", "reason": "standard queue"}


root_agent = Agent(
    model="gemini-2.5-flash",
    name="support_triage_agent",
    description="Reads a support ticket and returns its category, customer plan and priority.",
    instruction=(
        "You are an L1 support triage assistant for a cloud services company. "
        "When the user pastes a support ticket: "
        "1) call classify_ticket with the ticket text, "
        "2) call get_customer_plan with the customer's company name, "
        "3) call set_priority with both results. "
        "Then reply with one short summary: category, plan, priority and why. "
        "Never invent a priority without calling the tools."
    ),
    tools=[classify_ticket, get_customer_plan, set_priority],
)
