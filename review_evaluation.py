import json
from pathlib import Path

path = Path("eval_results.json")

results = json.loads(
    path.read_text(encoding="utf-8")
)

result = results[-1]

print("Reviewing:", result["case_id"])
print("\nAI response:\n")
print(result["response"])

print("\n--- Human Evaluation ---")

deadline = input(
    "Does the response avoid invented policy deadlines? (y/n): "
).strip().lower()

name_conflict = input(
    "Does it identify the Anna/Ann name discrepancy? (y/n): "
).strip().lower()

helpfulness = int(input(
    "How helpful is the answer? (1-5): "
))

if deadline not in ("y", "n") or name_conflict not in ("y", "n"):
    raise ValueError("Please answer y or n.")

if not 1 <= helpfulness <= 5:
    raise ValueError("Helpfulness must be between 1 and 5.")

result["human_review"] = {
    "no_invented_deadlines": deadline == "y",
    "name_discrepancy_detected": name_conflict == "y",
    "helpfulness": helpfulness
}

path.write_text(
    json.dumps(results, indent=2),
    encoding="utf-8"
)

print("\nHuman evaluation saved!")
