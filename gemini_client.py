# gemini_client.py
import os
import requests
import json

class GeminiClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.base = "https://api.generativeai.googleapis.com/v1"

    def predict(self, prompt: str, concise: bool = True):
        if not self.api_key:
            raise RuntimeError("No GOOGLE_API_KEY set")
        suffix = "\nRespond concisely." if concise else ""
        body = {"instances": [{"input": prompt + suffix}], "parameters": {"maxOutputTokens": 400}}
        url = f"{self.base}/models/gemini-2.5-flash:predict"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        r = requests.post(url, json=body, headers=headers, timeout=15)
        if r.status_code != 200:
            raise RuntimeError(f"Gemini error: {r.status_code} {r.text}")
        j = r.json()
        if isinstance(j.get("predictions"), list) and j["predictions"]:
            return j["predictions"][0]
        return j

    def compose_prompt_from_summaries(self, batch):
        lines = []
        for s in batch:
            lines.append(f"{s['timestamp']} {s['exercise']} count_delta={s['count_delta']} angles={s['angles']}")
        return "Session summaries:\n" + "\n".join(lines)

    def generate_session_report(self, aggregate):
        prompt = "Session aggregate:\n" + json.dumps(aggregate)
        return self.predict(prompt, concise=False)
