"""Score a candidate independently from the decision to publish it."""
import argparse
import json
import math
import unicodedata
from pathlib import Path


def normalize(text):
    return " ".join(unicodedata.normalize("NFKC", text).casefold().split())


def probability(value):
    if type(value) not in (int, float) or not math.isfinite(value) or not 0 <= value <= 1:
        raise ValueError("Expected a finite probability in [0, 1]")
    return value


def score(case, candidate, confidence, threshold=0.8):
    """Confidence means P(this candidate is correct and supported by the evidence)."""
    p, cutoff = probability(confidence), probability(threshold)
    if not isinstance(candidate, str) or not normalize(candidate) or normalize(candidate) == "[abstain]":
        raise ValueError("Expected a nonempty candidate answer, not an abstention token")
    answer = normalize(candidate)
    accepted = {normalize(x) for x in case["answers"]}
    correct = answer in accepted
    publish = p >= cutoff
    return {
        "id": case["id"],
        "correct_and_supported": correct,
        "brier": (p - int(correct)) ** 2,
        "decision": candidate if publish else "[ABSTAIN]",
        "answered": publish,
        "wrong_if_answered": publish and not correct,
    }


def verify_pairs(cases):
    """Check fixture invariants; references are curated, never inferred from prose."""
    ids, pairs = set(), {}
    for case in cases:
        if case["id"] in ids:
            raise ValueError("Duplicate case ID")
        ids.add(case["id"])
        pairs.setdefault(case["pair_id"], []).append(case)
    for pair in pairs.values():
        if len(pair) != 2 or sorted(bool(row["answers"]) for row in pair) != [False, True]:
            raise ValueError("Each pair needs one answerable and one unanswerable case")
        if pair[0]["question"] != pair[1]["question"] or pair[0]["evidence"] == pair[1]["evidence"]:
            raise ValueError("Paired cases need the same question and different evidence")
    return {case["id"]: case for case in cases}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cases", type=Path)
    parser.add_argument("predictions", type=Path)
    parser.add_argument("--threshold", type=float, default=0.8)
    args = parser.parse_args()
    cases = verify_pairs(json.loads(args.cases.read_text(encoding="utf-8")))
    predictions = json.loads(args.predictions.read_text(encoding="utf-8"))
    ids = [row["id"] for row in predictions]
    if len(ids) != len(set(ids)) or set(ids) != set(cases):
        parser.error("Predictions must cover every case exactly once")
    for row in predictions:
        print(json.dumps(score(cases[row["id"]], row["candidate"], row["confidence"], args.threshold)))


if __name__ == "__main__":
    main()
