from google import genai
from google.genai import types
from tools import get_policy, select_policy, prepare_tasks

def policy_tool() -> dict:
    """Read the official DemoTech employee onboarding policy."""
    print("Tool executed: get_policy()")
    return get_policy()


def onboarding_plan_tool(
    department: str,
    work_arrangement: str,
    employee_email: str,
    manager: str,
    manager_email: str,
    laptop: str,
    phone: str
) -> dict:
    """Generate onboarding tasks using DemoTech company policies."""

    print("Tool executed: onboarding_plan_tool()")

    employee = {
        "department": department,
        "work_arrangement": work_arrangement,
        "employee_email": employee_email,
        "manager": manager,
        "manager_email": manager_email,
        "equipment_preferences": {
            "laptop": laptop,
            "phone": phone
        } if laptop and phone else None
        }

    selected_rules = select_policy(employee)

    tasks = prepare_tasks(employee, selected_rules)

    return {"tasks": tasks}


def run_onboarding_agent(employee: dict) -> str:
    client = genai.Client()

    chat = client.chats.create(
        model="gemini-3.5-flash-lite",
        config=types.GenerateContentConfig(
            tools=[policy_tool, onboarding_plan_tool]
        )
    )

    preferences = employee.get("equipment_preferences") or {}

    prompt = f"""
    Prepare an onboarding plan for this employee.

    Department: {employee.get("department", "")}
    Work arrangement: {employee.get("work_arrangement", "")}
    Employee email: {employee.get("employee_email", "")}
    Manager: {employee.get("manager", "")}
    Manager email: {employee.get("manager_email", "")}

    Laptop: {preferences.get("laptop", "")}
    Phone: {preferences.get("phone", "")}

    Use onboarding_plan_tool to generate the tasks.
    Explain which tasks are blocked and why.
    Follow the tool results exactly.

    IMPORTANT:
    The task statuses returned by onboarding_plan_tool
    are the authoritative results.

    A task is Blocked ONLY when its status in the
    tool result is "Blocked".

    Do not invent additional dependencies.
    Do not interpret Pending tasks as Blocked.

    If equipment_preferences are provided,
    equipment_preparation is Pending.

    If no tasks have status "Blocked",
    explicitly state: "No blocked tasks."

    Human approval is required before sending emails
    or calendar invitations, but this does not
    automatically make a Pending task Blocked.

    Do not claim any emails or invitations have been sent.
    """


    # Let Gemini execute the available tools
    chat.send_message(prompt)

    # Calculate authoritative task statuses using Python
    selected_rules = select_policy(employee)
    tasks = prepare_tasks(employee, selected_rules)

    lines = ["### Verified Onboarding Plan"]

    for task in tasks:
        lines.append(
            f"- {task['name']}: **{task['status']}**"
        )

    blocked_tasks = [
        task for task in tasks
        if task["status"] == "Blocked"
    ]

    lines.append("\n### Blocked Tasks")

    if not blocked_tasks:
        lines.append("No blocked tasks.")
    else:
        for task in blocked_tasks:
            rule = next(
                r for r in selected_rules
                if r["task"] == task["name"]
            )

            missing = [
                field for field in rule.get("requires", [])
                if not employee.get(field)
            ]

            lines.append(
                f"- {task['name']}: Missing {', '.join(missing)}"
            )

    return "\n".join(lines)
