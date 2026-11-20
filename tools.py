import json

def check_missing_info(employee):
    required_fields = {
        "employee_email": "Employee email",
        "manager": "Manager name",
        "manager_email": "Manager email"
    }

    missing = []

    for field, label in required_fields.items():
        if not employee.get(field):
            missing.append(label)

    return missing

def get_policy():
    with open("policies/general.json", "r") as file:
        data = json.load(file)
    return data

def select_policy(employee):
    policy = get_policy()
    selected_rules = []

    for rule in policy["rules"]:
        conditions = rule["applies_to"]
        if conditions.get("all") == True:
            selected_rules.append(rule)
        elif ("department" in conditions and
          conditions["department"] == employee.get("department")):
            selected_rules.append(rule)
        elif ("work_arrangement" in conditions and
          conditions["work_arrangement"] == employee.get("work_arrangement")):
            selected_rules.append(rule)
        elif "missing_any" in conditions and any(
            not employee.get(field) for field in conditions["missing_any"]):
            selected_rules.append(rule)

    return selected_rules


def prepare_tasks(employee, selected_rules):
    tasks = []

    for rule in selected_rules:
        task_name = rule["task"]
        required = rule.get("requires", [])

        if any(not employee.get(field) for field in required):
            status = "Blocked"
        else:
            status = "Pending"

        task = {"name": task_name, "status": status}

        tasks.append(task)

    return tasks



def draft_welcome_email(employee) -> dict:

    first_name = employee.get("first_name")
    email = employee.get("employee_email")
    manager = employee.get("manager")
    manager_email = employee.get("manager_email")

    # Check whether the email address is missing
    if not email:
        return {"error": "Employee email is missing"}

    # Create the email subject
    subject = f"Welcome to DemoTech, {first_name}!"

    
    if manager:
        manager_text = (
            f"Your manager, {manager}, will support you "
            "during your onboarding."
        )
    else:
        manager_text = (
            "We will share your manager's details "
            "once they are confirmed."
        )

    body = (
        f"Dear {first_name},\n\n"
        "Welcome to DemoTech! We are excited to have you joining us.\n\n"
        f"{manager_text}\n\n"
        "As part of your onboarding, we will coordinate "
        "an introductory meeting with your manager.\n\n"
        "Best regards,\n"
        "DemoTech HR Team"
    )


    # Return the draft for HR review
    return {
        "to": email,
        "cc": manager_email or "",
        "subject": subject,
        "body": body,
        "approval_status": "Awaiting HR approval"
    }

