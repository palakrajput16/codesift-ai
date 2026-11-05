
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from codesift.benchmark import BENCHMARK
from codesift.experiment_runner import run_case
from codesift.models import GeminiProvider


ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT / "reports"

MAX_TESTS = 8

EXPERIMENT_DESIGN = "paired_shared_initial_suite_v1"
GENERATION_PROMPT_VERSION = "test_generation_v2"
FEEDBACK_PROMPT_VERSION = "execution_feedback_v1"
EVALUATOR_VERSION = "type_aware_float_tolerance_v1"
BENCHMARK_VERSION = "benchmark_v3_1"


def save_report(report, output_file):
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def create_report(provider, trial_id):
    return {
        "project": "CodeSift",
        "experiment": "Baseline vs Execution Feedback",
        "trial_id": trial_id,
        "experiment_design": EXPERIMENT_DESIGN,
        "generation_prompt_version": GENERATION_PROMPT_VERSION,
        "feedback_prompt_version": FEEDBACK_PROMPT_VERSION,
        "evaluator_version": EVALUATOR_VERSION,
        "benchmark_version": BENCHMARK_VERSION,
        "benchmark_case_count": len(BENCHMARK),
        "benchmark_case_ids": [
            case.bug_id for case in BENCHMARK
        ],
        "model": provider.model,
        "max_tests_per_suite": MAX_TESTS,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": None,
        "results": [],
        "errors": [],
    }


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--trial",
        type=int,
        required=True,
        choices=range(1, 6),
        help="Trial number from 1 to 5.",
    )

    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume the selected trial report.",
    )

    parser.add_argument(
        "--case",
        choices=[case.bug_id for case in BENCHMARK],
        help="Run only the selected benchmark case.",
    )

    args = parser.parse_args()

    trial_id = f"trial_{args.trial:02d}"

    output_file = (
        REPORTS_DIR
        / f"experiment_results_v3_1_{trial_id}.json"
    )

    provider = GeminiProvider()

    if args.resume and output_file.exists():
        report = json.loads(
            output_file.read_text(encoding="utf-8")
        )

        expected_metadata = {
            "trial_id": trial_id,
            "model": provider.model,
            "max_tests_per_suite": MAX_TESTS,
            "experiment_design": EXPERIMENT_DESIGN,
            "generation_prompt_version": GENERATION_PROMPT_VERSION,
            "feedback_prompt_version": FEEDBACK_PROMPT_VERSION,
            "evaluator_version": EVALUATOR_VERSION,
            "benchmark_version": BENCHMARK_VERSION,
            "benchmark_case_count": len(BENCHMARK),
            "benchmark_case_ids": [
                case.bug_id for case in BENCHMARK
            ],
        }

        for key, expected_value in expected_metadata.items():
            if report.get(key) != expected_value:
                raise ValueError(
                    f"Existing report has incompatible {key}: "
                    f"{report.get(key)!r}. "
                    f"Expected {expected_value!r}."
                )

        print(f"Resuming {trial_id}.")

    else:
        if output_file.exists():
            raise FileExistsError(
                f"{output_file} already exists. "
                "Use --resume to continue it."
            )

        report = create_report(provider, trial_id)

    selected_cases = [
        case for case in BENCHMARK
        if args.case is None or case.bug_id == args.case
    ]

    completed_ids = {
        result["bug_id"]
        for result in report["results"]
    }

    print(f"Trial: {trial_id}")
    print(f"Model: {provider.model}")
    print(f"Experiment design: {EXPERIMENT_DESIGN}")
    print(f"Benchmark version: {BENCHMARK_VERSION}")
    print(f"Selected cases: {len(selected_cases)}")
    print(f"Maximum tests per suite: {MAX_TESTS}")

    for case in selected_cases:
        if case.bug_id in completed_ids:
            print(
                f"\nSkipping {case.bug_id}: already completed."
            )
            continue

        print(f"\n{'=' * 50}")
        print(f"Starting {case.bug_id}: {case.description}")
        print("=" * 50)

        try:
            result = run_case(
                case=case,
                provider=provider,
                max_tests=MAX_TESTS,
            )

            result["trial_id"] = trial_id
            result["trial_timestamp"] = (
                datetime.now(timezone.utc).isoformat()
            )

            report["results"].append(result)

            print(
                f"\nBaseline detected bug: "
                f"{result['baseline']['evaluation']['bug_detected']}"
            )

            print(
                f"Feedback detected bug: "
                f"{result['feedback']['revised_evaluation']['bug_detected']}"
            )

        except Exception as exc:
            error = {
                "bug_id": case.bug_id,
                "trial_id": trial_id,
                "error": f"{type(exc).__name__}: {exc}",
            }

            report["errors"].append(error)
            print(f"\nERROR: {error['error']}")

        save_report(report, output_file)
        print(f"Progress saved to: {output_file}")

    report["completed_at"] = datetime.now(
        timezone.utc
    ).isoformat()

    save_report(report, output_file)

    print("\n========== EXPERIMENT STATUS ==========")
    print(f"Trial: {trial_id}")
    print(f"Completed cases: {len(report['results'])}")
    print(f"Failed cases: {len(report['errors'])}")
    print(f"Selected cases: {len(selected_cases)}")
    print(f"Report: {output_file}")


if __name__ == "__main__":
    main()
