import json
from pathlib import Path
from statistics import mean
import re

results = json.loads(
    Path("eval_results.json").read_text(encoding="utf-8")
)

# Analyze only our latest batch
runs = results[-3:]

total = len(runs)

successful = sum(
    run["api_success"] for run in runs
)

first_attempt_success = sum(
    run["api_success"] and run.get("attempts", 1) == 1
    for run in runs
)

overload_errors = sum(
    run.get("transient_503_count", 0)
    for run in runs
)

average_latency = mean(
    run["response_time_seconds"]
    for run in runs
)

print("=== AutoFirstHi Evaluation Summary ===")
print(f"Total runs: {total}")
print(f"Successful runs: {successful}/{total}")
print(f"First-attempt success: {first_attempt_success}/{total}")
print(f"503 errors: {overload_errors}")
print(f"Average latency: {average_latency:.2f} seconds")


print("\n=== Response Quality Summary ===")

successful_runs = [
    run for run in runs
    if run["api_success"]
]

# Detect possible unsupported welcome-email deadlines
deadline_pattern = re.compile(
    r"welcome[\s_]*email.*"
    r"\b(before|prior to)\b.*"
    r"\b(first day|start date)\b",
    re.IGNORECASE
)

flagged_runs = 0

for index, run in enumerate(successful_runs, start=1):

    response = run["response"]

    suspicious_lines = [
        line.strip()
        for line in response.splitlines()
        if deadline_pattern.search(line)
    ]

    if suspicious_lines:
        flagged_runs += 1
        print(f"Run {index}: REVIEW NEEDED")

        for line in suspicious_lines:
            print("  Potential issue:", line)

    else:
        print(f"Run {index}: No matching deadline claim detected")

print(
    f"\nPotential deadline issues: "
    f"{flagged_runs}/{len(successful_runs)} successful runs"
)
