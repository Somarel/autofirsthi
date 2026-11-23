
import json
import subprocess
import sys
import time
from pathlib import Path

RUNS = 3
DELAY_SECONDS = 30

for i in range(RUNS):
    print(f"\nEvaluation {i + 1}/{RUNS}", flush=True)

    # Execute one evaluation and save its result
    subprocess.run(
        [sys.executable, "run_evaluation.py"],
        check=True
    )

    # Read the result of the latest evaluation
    results = json.loads(
        Path("eval_results.json").read_text(
            encoding="utf-8"
        )
    )

    latest = results[-1]

    # Avoid repeatedly calling an overloaded model
    if not latest["api_success"]:
        print("API failure detected. Stopping batch.")
        break

    # Wait before sending another independent request
    if i < RUNS - 1:
        print(f"Waiting {DELAY_SECONDS} seconds...")
        time.sleep(DELAY_SECONDS)

print("\nBatch evaluation finished.")
