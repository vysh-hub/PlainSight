import argparse
import json
from dotenv import load_dotenv

from src.pipeline.run_pipeline import run_policy_pipeline
from src.pipeline.types import PolicyInput

def main():
    load_dotenv()

    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True, help="Input JSON file")
    ap.add_argument("--out", dest="out", required=True, help="Output JSON file")
    args = ap.parse_args()

    with open(args.inp, "r", encoding="utf-8") as f:
        raw = json.load(f)

    policy_in = PolicyInput(
        url=raw.get("url", ""),
        title=raw.get("title", ""),
        raw_text=raw.get("raw_text", ""),
        captured_at=raw.get("captured_at")
    )

    result = run_policy_pipeline(policy_in)

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f" Wrote output to {args.out}")

if __name__ == "__main__":
    main()
