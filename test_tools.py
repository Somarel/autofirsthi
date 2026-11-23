from datetime import date
from tools import (
    prepare_tasks,
    select_policy,
    get_allowed_meeting_dates,
    draft_welcome_email,
    draft_manager_meeting
)


def test_equipment_blocked_without_preferences():

    employee = {
        "equipment_preferences": None
    }

    rules = [
        {
            "task": "equipment_preparation",
            "requires": ["equipment_preferences"]
        }
    ]

    tasks = prepare_tasks(employee, rules)

    assert tasks[0]["status"] == "Blocked"

def test_equipment_ready_with_preferences():

    employee = {
        "equipment_preferences": {
            "laptop": "MacBook",
            "phone": "iPhone"
        }
    }

    rules = [
        {
            "task": "equipment_preparation",
            "requires": ["equipment_preferences"]
        }
    ]

    tasks = prepare_tasks(employee, rules)

    assert tasks[0]["status"] == "Pending"


def test_remote_engineering_policy():

    employee = {
        "department": "Engineering",
        "work_arrangement": "Remote",
        "manager": "Mike",
        "manager_email": "mike@example.com"
    }

    selected_rules = select_policy(employee)

    rule_ids = [rule["id"] for rule in selected_rules]

    assert "R5" in rule_ids

    assert "R6" in rule_ids

    assert "R7" not in rule_ids


def test_missing_manager_policy():

    employee = {
        "department": "Engineering",
        "work_arrangement": "Remote",
        "manager": "",
        "manager_email": ""
    }

    selected_rules = select_policy(employee)

    rule_ids = [rule["id"] for rule in selected_rules]

    assert "R7" in rule_ids
    assert "R4" in rule_ids

    tasks = prepare_tasks(employee, selected_rules)

    manager_introduction_task = next(
        task for task in tasks
        if task["name"] == "manager_introduction"
    )

    assert manager_introduction_task["status"] == "Blocked"


def test_meeting_dates_skip_weekend():

    allowed_dates = get_allowed_meeting_dates("2026-11-20")

    assert date(2026, 11, 20) in allowed_dates

    assert date(2026, 11, 23) in allowed_dates

    assert date(2026, 11, 21) not in  allowed_dates

    assert len(allowed_dates) == 2


def test_welcome_email_missing_address():

    employee = {
        "first_name": "Anna",
        "employee_email": ""
    }
    result = draft_welcome_email(employee)

    assert result["error"] == "Employee email is missing"


def test_welcome_email_with_valid_address():

    employee = {
        "first_name": "Anna",
        "employee_email": "anna@example.com",
        "manager": "Mike",
        "manager_email": "mike@example.com"
    }

    result = draft_welcome_email(employee)

    assert result["to"] == "anna@example.com"

    assert result["cc"] == "mike@example.com"

    assert result["approval_status"] == "Awaiting HR approval"


def test_manager_meeting_missing_email():

    employee = {
        "first_name": "Anna",
        "employee_email": "anna@example.com",
        "manager": "Mike",
        "manager_email": ""
    }

    result = draft_manager_meeting(employee)

    assert result["error"] == "Manager or manager email is missing"


def test_manager_meeting_valid():

    employee = {
        "first_name": "Anna",
        "employee_email": "anna@example.com",
        "manager": "Mike",
        "manager_email": "mike@example.com"
    }

    result = draft_manager_meeting(employee)

    assert "anna@example.com" in result["attendees"]

    assert "mike@example.com" in result["attendees"]

    assert result["approval_status"] == "Awaiting HR approval"


def test_complete_onboarding_scenario():

    employee = {
        "first_name": "Anna",
        "department": "Engineering",
        "work_arrangement": "Remote",
        "employee_email": "anna@example.com",
        "manager": "",
        "manager_email": "",
        "equipment_preferences": {
            "laptop": "MacBook",
            "phone": "iPhone"
        }
    }

    selected_rules = select_policy(employee)

    tasks = prepare_tasks(employee, selected_rules)

    task_statuses = {}

    for task in tasks:
        task_statuses[task["name"]] = task["status"]

    assert task_statuses["welcome_email"] == "Pending"
    assert task_statuses["equipment_preparation"] == "Pending"
    assert task_statuses["manager_introduction"] == "Blocked"
    assert task_statuses["request_manager_details"] == "Pending"


def test_manager_meeting_missing_employee_email():

    employee = {
        "first_name": "Anna",
        "employee_email": "",
        "manager": "Mike",
        "manager_email": "mike@example.com"
    }

    result = draft_manager_meeting(employee)

    assert result["error"]
    assert "attendees" not in result
