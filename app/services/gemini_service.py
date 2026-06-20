import json
import time

import google.generativeai as genai

from app.core.config import GEMINI_API_KEY


genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.0-flash")


def classify_missing_categories(transactions):

    prompt = f"""
Return ONLY valid JSON.

Transactions:
{json.dumps(transactions)}
"""

    for attempt in range(3):

        try:

            response = model.generate_content(prompt)

            print("CATEGORY RESPONSE:")
            print(response.text)

            return json.loads(response.text)

        except Exception as e:

            print("CATEGORY ERROR:")
            print(str(e))

            if attempt == 2:
                return None

            time.sleep(2 ** attempt)

    return None


def generate_summary(summary_data):

    prompt = f"""
Return ONLY valid JSON.

Input:
{json.dumps(summary_data)}

Format:

{{
  "narrative": "...",
  "risk_level": "low"
}}
"""

    for attempt in range(3):

        try:

            response = model.generate_content(prompt)

            print("SUMMARY RESPONSE:")
            print(response.text)

            return json.loads(response.text)

        except Exception as e:

            print("SUMMARY ERROR:")
            print(str(e))

            if attempt == 2:
                return None

            time.sleep(2 ** attempt)

    return None