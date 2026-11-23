
import json
from pathlib import Path

path = Path("eval_results.json")
results = json.loads(path.read_text(encoding="utf-8"))

runs = results[-3:]

for index, run in enumerate(runs, start=1):

    if not run["api_success"]:
        continue

    print(f"\n=== Review {index}/3 ===")
    print(run["response"])

    print("\n--- Your assessment ---")

    violation = input(
        "Does the answer falsely claim a policy requirement? (y/n): "
    ).strip().lower()

    helpfulness = int(input(
        "How helpful is the answer? (1-5): "
    ))

    if violation not in ("y", "n"):
        raise ValueError("Please enter y or n.")

    if not 1 <= helpfulness <= 5:
        raise ValueError("Helpfulness must be between 1 and 5.")

    run.setdefault("human_review", {})

    run["human_review"].update({
        "policy_violation": violation == "y",
        "helpfulness": helpfulness
    })

path.write_text(
    json.dumps(results, indent=2),
    encoding="utf-8"
)

print("\nHuman reviews saved!")
