import json
import time
from datetime import datetime, timezone
from pathlib import Path
from google.genai import errors
from agent import ask_onboarding_agent


# Load our evaluation dataset
with open("eval_cases.json", encoding="utf-8") as file:
    cases = json.load(file)

case = cases[0]

# Measure how long Gemini takes

start_time = time.perf_counter()

response = ""
error = None
attempts = 0
transient_503_count = 0

for attempt in range(1, 4):
    attempts = attempt

    try:
        response = ask_onboarding_agent(
            case["employee"],
            case["question"]
        )
        break

    except errors.APIError as exc:
        if exc.code == 503:
            transient_503_count += 1

            if attempt < 3:
                delay = 2 ** (attempt - 1)
                print(f"Gemini overloaded. Retrying in {delay}s...")
                time.sleep(delay)
                continue

        error = f"{exc.code}: {exc.message}"
        break

    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"
        break

elapsed_time = round(
    time.perf_counter() - start_time, 2
)

# Record the evaluation run
result = {
    "case_id": case["id"],
    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "response_time_seconds": elapsed_time,
    "api_success": error is None,
    "response": response,
    "error": error,
    "attempts": attempts,
    "transient_503_count": transient_503_count
}


# Save results without losing previous runs
results_path = Path("eval_results.json")

if results_path.exists():
    results = json.loads(results_path.read_text(encoding="utf-8"))
else:
    results = []

results.append(result)

results_path.write_text(
    json.dumps(results, indent=2),
    encoding="utf-8"
)

print("Case:", result["case_id"])
print("API success:", result["api_success"])
print("Response time:", result["response_time_seconds"], "seconds")
print("\nGemini response:\n")
print(response if response else error)
print("Attempts:", attempts)
print("Transient 503 errors:", transient_503_count)