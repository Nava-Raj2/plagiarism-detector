import argparse
import json
import sys
from detector import overall_score

def format_report(result, label1="Text 1", label2="Text 2"):
    lines = []
    lines.append("=" * 60)
    lines.append("         PLAGIARISM DETECTION REPORT")
    lines.append("=" * 60)
    lines.append(f"  Comparing: {label1}  →  {label2}")
    lines.append("")
    lines.append(f"  Overall Score : {result['overall_score_pct']}%")
    lines.append(f"  Verdict       : {result['verdict']}")
    lines.append("")
    m = result["metrics"]
    lines.append("-" * 60)
    lines.append("  Metric Breakdown")
    lines.append("-" * 60)
    lines.append(f"  {'3-gram Jaccard':<30} {m['jaccard_3gram']:>6}%")
    lines.append(f"  {'2-gram Jaccard':<30} {m['jaccard_2gram']:>6}%")
    lines.append(f"  {'Cosine Similarity':<30} {m['cosine_similarity']:>6}%")
    lines.append(f"  {'Fingerprint Similarity':<30} {m['fingerprint_similarity']:>6}%")
    lines.append(f"  {'LCS Ratio':<30} {m['lcs_ratio']:>6}%")
    lines.append("")
    phrases = result.get("matching_phrases", [])
    if phrases:
        lines.append("-" * 60)
        lines.append("  Matching Phrases")
        lines.append("-" * 60)
        for i, p in enumerate(phrases[:5], 1):
            lines.append(f"\n  [{i}] Similarity: {round(p['similarity']*100,1)}%")
            lines.append(f"      Source  : {p['source'][:90]}")
            lines.append(f"      Suspect : {p['suspect'][:90]}")
    lines.append("\n" + "=" * 60)
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="Plagiarism Detector CLI")
    group1 = parser.add_mutually_exclusive_group(required=True)
    group2 = parser.add_mutually_exclusive_group(required=True)
    group1.add_argument("--text1", type=str)
    group1.add_argument("--file1", type=str)
    group2.add_argument("--text2", type=str)
    group2.add_argument("--file2", type=str)
    parser.add_argument("--report", type=str)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        text1 = args.text1 if args.text1 else open(args.file1).read()
        text2 = args.text2 if args.text2 else open(args.file2).read()
        label1 = "Text 1" if args.text1 else args.file1
        label2 = "Text 2" if args.text2 else args.file2
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    result = overall_score(text1, text2)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        report = format_report(result, label1, label2)
        print(report)
        if args.report:
            open(args.report, "w").write(report)
            print(f"Report saved to: {args.report}")

if __name__ == "__main__":
    main()
