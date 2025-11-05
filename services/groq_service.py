
# services/groq_service.py
import os
import json
import requests


class GroqService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.endpoint = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama-3.1-8b-instant"  # or "llama3-70b-8192"
        self.available = bool(api_key)

    def is_available(self) -> bool:
        return self.available

    def _request(self, messages):
        if not self.available:
            print("Groq service not available: No API key provided")
            return None

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.7
            }

            print("Sending request to Groq API...")
            response = requests.post(self.endpoint, headers=headers, json=payload, timeout=20)
            
            if response.status_code != 200:
                print(f"Groq API error (HTTP {response.status_code}): {response.text}")
                return None
                
            try:
                data = response.json()
                return data["choices"][0]["message"]["content"].strip()
            except KeyError as ke:
                print(f"Unexpected Groq API response format: {ke}")
                print(f"Response: {data}")
                return None
            except json.JSONDecodeError as je:
                print(f"Invalid JSON in Groq API response: {je}")
                print(f"Response text: {response.text}")
                return None

        except requests.exceptions.Timeout:
            print("Groq API request timed out after 20 seconds")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Groq API request failed: {str(e)}")
            return None
        except Exception as e:
            print(f"Unexpected error in Groq API call: {str(e)}")
            return None

    def classify_intent(self, query: str):
        """Classify user intent similar to Gemini's logic."""
        messages = [
            {"role": "system", "content": "You are an intent classifier for VIT admission queries."},
            {"role": "user", "content": f"""
Analyze this query and classify it:
- "cutoff" - Questions about admission cutoffs or closing ranks
- "rank_prediction" - Student provides rank, wants eligible branches
- "faq" - Questions about hostel, FFCS, clubs, campus life, fees,counselling,general,counselling,seat allotment

Query: "{query}"
This is an example:
Respond only in JSON:
{{
  "intent": "one of the above",
  "confidence": 0.85,
  "reasoning": "brief explanation"
}}
"""}
        ]

        result = self._request(messages)
        if not result:
            return None

        try:
            json_text = result
            if "```" in json_text:
                json_text = json_text.split("```")[1].replace("json", "").strip()
            return json.loads(json_text)
        except Exception:
            return None

    def generate_response(self, query: str, context: str, intent: str):
        """Generate a concise and helpful answer."""
        if not self.available:
            return None

        if intent == "rank_prediction":
            system_prompt = "You are a friendly VIT admission counselor helping students understand their branch eligibility."
        elif intent == "cutoff":
            system_prompt = "You are a VIT admission assistant providing cutoff-related answers."
        elif intent == "faq":
            system_prompt = "You are a friendly VIT student answering FAQ questions helpfully and concisely."
        else:
            system_prompt = "You are a helpful VIT assistant."

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Question: {query}\n\nContext:\n{context}\n\nAnswer under 100 words:"}
        ]

        return self._request(messages)