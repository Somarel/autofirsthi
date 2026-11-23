import json
from pathlib import Path
import re
from tools import select_policy, prepare_tasks

# Load previous evaluation results
results = json.loads(
    Path("eval_results.json").read_text(encoding="utf-8")
)

# Select the most recent result
result = results[-1]

response = result["response"]
lines = response.lower().splitlines()

# Basic automated checks
checks = {
    "manager_introduction_blocked": any(
        ("manager introduction" in line or "manager_introduction" in line)
        and "blocked" in line
        for line in lines
    ),

    "human_approval_mentioned": (
        "approval" in response.lower()
    ),

    "email_draft_present": (
        "subject:" in response.lower()
    )
}

print("Evaluation case:", result["case_id"])

for name, passed in checks.items():
    if passed:
        print(name, ": PASS")
    else:
        print(name, ": FAIL")


# Load the evaluation scenario
cases = json.loads(
    Path("eval_cases.json").read_text(encoding="utf-8")
)

case = next(
    item for item in cases
    if item["id"] == result["case_id"]
)

# Calculate correct statuses independently
selected_rules = select_policy(case["employee"])
tasks = prepare_tasks(case["employee"], selected_rules)

expected_statuses = {}

for task in tasks:
    expected_statuses[task["name"]] = task["status"].lower()


# Extract explicit task status claims from Gemini
claims = {}

for line in response.splitlines():

    match = re.search(
        r"\bstatus\s*:\s*(pending|blocked)\b",
        line,
        re.IGNORECASE
    )

    if not match:
        continue

    normalized_line = line.lower().replace("_", " ")

    matching_tasks = [
        name for name in expected_statuses
        if name.replace("_", " ") in normalized_line
    ]

    if len(matching_tasks) == 1:
        task_name = matching_tasks[0]
        claims.setdefault(task_name, []).append(
            match.group(1).lower()
        )


# Compare Gemini claims with verified Python results
print("\n--- Task Status Evaluation ---")

passed = 0

for task_name, claimed_statuses in claims.items():

    expected = expected_statuses[task_name]

    correct = all(
        status == expected
        for status in claimed_statuses
    )

    if correct:
        passed += 1

    print(
        f"{task_name}: "
        f"{'PASS' if correct else 'FAIL'} "
        f"(expected: {expected}, "
        f"Gemini: {claimed_statuses})"
    )

if claims:
    print(f"\nCorrect task statuses: {passed}/{len(claims)}")
    print(f"Status coverage: {len(claims)}/{len(expected_statuses)}")
else:
    print("NOT EVALUATED: No explicit status claims found.")


print("\n--- Policy Claim Evaluation ---")

# Look for claims about the welcome email
welcome_lines = [
    line.strip()
    for line in response.splitlines()
    if "welcome email" in line.lower()
]

# Detect mandatory deadlines
deadline_pattern = re.compile(
    r"\b(must|required|needs to|has to)\b"
    r".*\b(before|prior to)\b"
    r".*\b(first day|start date)\b",
    re.IGNORECASE
)

unsupported_claims = [
    line for line in welcome_lines
    if deadline_pattern.search(line)
]

if unsupported_claims:
    print("Unsupported welcome-email deadline: FAIL")

    for claim in unsupported_claims:
        print("Found:", claim)
else:
    print("Unsupported welcome-email deadline: NOT DETECTED")
