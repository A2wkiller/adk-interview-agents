"""Agent 2 - Cloud Ops Assistant (one agent, several infra tools).

Business use case: an internal assistant for a cloud support team.
It answers 'is the VM down?', restarts a VM, lists open incidents and
summarizes a customer's bill - against a mock inventory standing in for
real cloud APIs (Azure/AWS SDK calls in production).
"""

from google.adk.agents import Agent

# --- Mock infrastructure: in production these are Azure/AWS/GCP API calls ---
VMS = {
    "vm-web-01": {"status": "running", "region": "ap-south-1", "restarts": 0},
    "vm-db-01": {"status": "stopped", "region": "ap-south-1", "restarts": 0},
    "vm-cache-01": {"status": "running", "region": "us-east-1", "restarts": 2},
}

INCIDENTS = [
    {"id": "INC-1042", "title": "Elevated latency on vm-cache-01", "severity": "medium"},
    {"id": "INC-1044", "title": "Disk 90% full on vm-db-01", "severity": "high"},
]


def check_vm_status(vm_name: str) -> dict:
    """Checks whether a virtual machine is running.

    Args:
        vm_name: Name of the VM, e.g. 'vm-web-01'.

    Returns:
        dict with 'status' ('running'/'stopped') or an 'error_message' if unknown.
    """
    vm = VMS.get(vm_name)
    if not vm:
        return {"status": "error", "error_message": f"No VM named '{vm_name}' in inventory."}
    return {"status": "success", "vm": vm_name, "vm_status": vm["status"], "region": vm["region"]}


def restart_vm(vm_name: str) -> dict:
    """Restarts a virtual machine and confirms the new state.

    Args:
        vm_name: Name of the VM to restart, e.g. 'vm-db-01'.

    Returns:
        dict with the restart result or an 'error_message' if unknown.
    """
    vm = VMS.get(vm_name)
    if not vm:
        return {"status": "error", "error_message": f"No VM named '{vm_name}' in inventory."}
    vm["status"] = "running"
    vm["restarts"] += 1
    return {"status": "success", "vm": vm_name, "vm_status": "running", "restart_count": vm["restarts"]}


def list_open_incidents() -> dict:
    """Lists all currently open infrastructure incidents.

    Returns:
        dict with a list of open incidents (id, title, severity).
    """
    return {"status": "success", "open_incidents": INCIDENTS, "count": len(INCIDENTS)}


root_agent = Agent(
    model="gemini-2.5-flash",
    name="cloud_ops_agent",
    description="Checks VM health, restarts VMs and lists open incidents for a cloud ops team.",
    instruction=(
        "You are a cloud operations assistant. Use check_vm_status for health questions, "
        "restart_vm only when the user clearly asks for a restart (state what you did afterwards), "
        "and list_open_incidents for incident overviews. "
        "If a VM name is unknown, say so and list the VMs you do know. Keep answers to 2-3 lines."
    ),
    tools=[check_vm_status, restart_vm, list_open_incidents],
)
