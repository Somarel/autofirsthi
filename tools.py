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
