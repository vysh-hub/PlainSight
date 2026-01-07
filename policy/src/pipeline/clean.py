import re

def clean_text(text: str) -> str:
    t = (text or "").replace("\r", "\n")
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n{3,}", "\n\n", t)

    lines = [ln.strip() for ln in t.split("\n")]
    out = []
    last = None
    for ln in lines:
        if len(ln) < 3:
            continue
        low = ln.lower()
        if low in {"home", "about", "contact", "login", "sign up", "privacy", "terms", "cookies"}:
            continue
        if last is not None and ln == last:
            continue
        out.append(ln)
        last = ln

    cleaned = "\n".join(out).strip()

    if len(cleaned) > 120_000:
        cleaned = cleaned[:120_000]

    return cleaned
