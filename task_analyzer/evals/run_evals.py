import json
import sys
import requests
from pathlib import Path

CASES_PATH = Path(__file__).parent / "cases.json"
ENDPOINT = "http://127.0.0.1:8000/task-analyzer"


def run_case(case: dict) -> tuple[bool, dict | str]:
    """
    Returns the metrics for success or failure of evals.
    """
    try:
        res = requests.post(ENDPOINT, json={"text": case["text"]}, timeout=35)
    except requests.RequestException as exc:
        return False, f"request failed: {exc}"

    if res.status_code != 200:
        return False, f"HTTP {res.status_code}: {res.text}"

    actual = res.json()
    expected = case["expected"]

    for field, expected_value in expected.items():
        actual_value = actual.get(field)
        if isinstance(expected_value, list):
            if actual_value not in expected_value:
                return False, actual
        else:
            if actual_value != expected_value:
                return False, actual

    return True, actual


def main():
    cases = json.loads(CASES_PATH.read_text())
    results = []

    for case in cases:
        passed, actual = run_case(case)
        results.append({"id": case["id"], "text": case["text"], "passed": passed, "actual": actual})
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] case {case['id']}: {case['text'][:60]}")

    passed_count = sum(r["passed"] for r in results)
    total = len(results)
    pct = round(100 * passed_count / total, 1)

    print(f"\n{passed_count}/{total} passed ({pct}%)\n")

    failed = [r for r in results if not r["passed"]]
    if failed:
        print("Failed cases:")
        for r in failed:
            print(f"  - case {r['id']}: {r['text']}")
            print(f"    expected: {[c['expected'] for c in cases if c['id'] == r['id']][0]}")
            print(f"    actual:   {r['actual']}")

    sys.exit(0 if passed_count == total else 1)

if __name__ == "__main__":
    main()