"""Benchmark Evaluator: Compares Bot outputs against Seeded Ground Truth."""
from typing import Dict, Any
from bot.orchestrator import PRReviewOrchestrator
from benchmark.seeded_pr_diff import get_seeded_benchmark_pr, get_clean_benchmark_pr
from benchmark.ground_truth import SEEDED_DEFECTS

def run_benchmark_evaluation() -> Dict[str, Any]:
    orchestrator = PRReviewOrchestrator()
    pr = get_seeded_benchmark_pr()
    review_result = orchestrator.run_review(pr)

    findings = review_result.findings
    total_seeded = len(SEEDED_DEFECTS)
    caught_defects = 0
    matched_ids = []

    for defect in SEEDED_DEFECTS:
        # Check if a finding matches this defect by category and target file
        match = any(
            f.category == defect["category"] and f.file_path == defect["file_path"]
            for f in findings
        )
        if match:
            caught_defects += 1
            matched_ids.append(defect["id"])

    # False alarm calculation: findings that do not correspond to any known defect
    false_alarms = 0
    for f in findings:
        matched = any(
            f.category == defect["category"] and f.file_path == defect["file_path"]
            for defect in SEEDED_DEFECTS
        )
        if not matched:
            false_alarms += 1

    # Also evaluate clean PR for false alarm verification
    clean_pr = get_clean_benchmark_pr()
    clean_result = orchestrator.run_review(clean_pr)
    clean_false_alarms = len(clean_result.findings)

    total_false_alarms = false_alarms + clean_false_alarms

    recall = (caught_defects / total_seeded) * 100
    precision = (caught_defects / (caught_defects + total_false_alarms)) * 100 if (caught_defects + total_false_alarms) > 0 else 0

    return {
        "total_seeded_defects": total_seeded,
        "caught_defects": caught_defects,
        "matched_defect_ids": matched_ids,
        "false_alarms": total_false_alarms,
        "recall_percent": recall,
        "precision_percent": precision,
        "review_summary": review_result.summary,
        "triage_status": review_result.status,
        "triage_labels": review_result.triage_labels
    }

if __name__ == "__main__":
    metrics = run_benchmark_evaluation()
    print("=" * 60)
    print("[BENCHMARK] SEEDED DEFECT BENCHMARK EVALUATION RESULTS")
    print("=" * 60)
    print(f"Seeded Defects Caught : {metrics['caught_defects']} / {metrics['total_seeded_defects']} ({metrics['recall_percent']:.1f}%)")
    print(f"False Alarms / Noise  : {metrics['false_alarms']}")
    print(f"Precision             : {metrics['precision_percent']:.1f}%")
    print(f"PR Triage Status      : {metrics['triage_status']}")
    print(f"Triage Labels         : {', '.join(metrics['triage_labels'])}")
    print("=" * 60)
