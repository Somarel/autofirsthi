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
    manager_email: str
) -> dict:
    """Generate onboarding tasks using DemoTech company policies."""

    print("Tool executed: onboarding_plan_tool()")

    employee = {
        "department": department,
        "work_arrangement": work_arrangement,
        "employee_email": employee_email,
        "manager": manager,
        "manager_email": manager_email
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

    prompt = f"""
    Prepare an onboarding plan for this employee.

    Department: {employee.get("department", "")}
    Work arrangement: {employee.get("work_arrangement", "")}
    Employee email: {employee.get("employee_email", "")}
    Manager: {employee.get("manager", "")}
    Manager email: {employee.get("manager_email", "")}

    Use onboarding_plan_tool to generate the tasks.
    Explain which tasks are blocked and why.
    Follow the tool results exactly.
    Do not claim any emails or invitations have been sent.
    """

    response = chat.send_message(prompt)

    return response.text or "No AI response was generated."

