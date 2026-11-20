
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
    """Generate onboarding tasks based on DemoTech policies."""
    
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

    print("DEBUG manager:", repr(manager))
    print("DEBUG manager_email:", repr(manager_email))
    print("DEBUG generated tasks:", tasks)


    return {"tasks": tasks}


client = genai.Client()

chat = client.chats.create(
    model="gemini-3.5-flash-lite",
    config=types.GenerateContentConfig(
        tools=[policy_tool, onboarding_plan_tool]
    )
)

response = chat.send_message(
    """
    Prepare onboarding for Alex Smith.

    Department: Engineering
    Work arrangement: Remote
    Employee email: alex@example.com
    Manager: ""
    Manager email: ""

    Use onboarding_plan_tool to generate the checklist.
    Explain which tasks are blocked and why.
    """
)

print("Gemini:", response.text)
