import os
import requests

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

def openrouter_write_takeaways(
    cleaned_text: str,
    model: str = "openai/gpt-4o-mini"
):
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return None

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "PolicyPipeline"
    }

    system_prompt = (
        "You analyze website privacy policies.\n"
        "Keep it short and precise.\n"
        "Your job is to summarize policies into simple English.\n"
        "You must not invent facts or give legal advice.\n"
        "Return ONLY valid JSON."
    )

    user_prompt = f"""
    Analyze the following privacy policy text.

    Return JSON with EXACT keys:
    - summary_simple: string (3 sentences)
    - key_takeaways: array of 6 bullet strings
    - risks: array of short strings
    - red_flags: array of short strings

    Rules:
    - Use only the provided text
    - No legal advice
    - No assumptions
    - Plain English

    Policy text:
    \"\"\"{cleaned_text[:12000]}\"\"\"
    """.strip()

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.3
    }

    try:
        r = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=30)
        r.raise_for_status()
        data = r.json()

        content = data["choices"][0]["message"]["content"].strip()

        import json
        start = content.find("{")
        end = content.rfind("}")
        if start == -1 or end == -1:
            return None

        return json.loads(content[start:end+1])

    except Exception as e:
        print("OPENROUTER ERROR:", repr(e))
        return None
