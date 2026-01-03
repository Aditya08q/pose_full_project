# gemini_summarizer.py
# Small wrapper to ask Gemini for a polished session summary
from gemini_client import GeminiClient
import json

def ask_gemini_for_session(gemini: GeminiClient, logger_aggregate: dict):
    prompt = "You are a friendly fitness coach. Given this session aggregate, produce a short human-friendly coaching summary and bullet corrections.\n\n"
    prompt += json.dumps(logger_aggregate)
    return gemini.predict(prompt, concise=False)
