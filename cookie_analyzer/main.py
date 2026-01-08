import argparse
import json
from cookie_analyzer.analyzer import analyze_cookie_usage
from cookie_analyzer.schemas import CookieAnalyzerInput

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", dest="out", required=True)
    args = ap.parse_args()

    with open(args.inp, "r") as f:
        raw = json.load(f)

    inp = CookieAnalyzerInput(**raw)
    result = analyze_cookie_usage(inp)

    with open(args.out, "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
