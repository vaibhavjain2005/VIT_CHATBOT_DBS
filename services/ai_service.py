import json
from typing import Dict
import google.generativeai as genai
from services.groq_service import GroqService


class AIService:
    def __init__(self, gemini_api_key: str, groq_api_key: str = ""):
        self.gemini_api_key = gemini_api_key
        self.groq_api_key = groq_api_key
        self.groq = GroqService(groq_api_key)
        self.model = None
        self._initialize()

    # -------------------- Initialization -------------------- #
    def _initialize(self):
        if self.groq.is_available():
            print("Groq API available — using Groq as primary LLM.")
            return

        try:
            genai.configure(api_key=self.gemini_api_key)
            self.model = genai.GenerativeModel("gemini-2.0-flash-exp")
            print("Gemini AI initialized successfully (fallback).")
        except Exception as e:
            print(f"Gemini initialization error: {e}")
            print("Note: AI features will use fallback logic.")
            self.model = None

    def is_available(self) -> bool:
        return self.model is not None

    # -------------------- Intent Classification -------------------- #
    def classify_intent(self, query: str) -> Dict:
        """
        Classifies the user's query into one of the predefined intents using Groq first,
        then falls back to Gemini, and finally to basic keyword logic if both fail.
        """
        # ✅ Try Groq first
        if hasattr(self, "groq") and self.groq.is_available():
            try:
                result = self.groq.classify_intent(query)
                if result and "intent" in result:
                    print(f"🧠 Groq classified intent as: {result['intent']} ({result.get('confidence', 0)})")
                    return result
            except Exception as e:
                print(f"Groq intent classification error: {e}")

        # ✅ Fallback to Gemini if available
        if self.is_available():
            prompt = f"""You are an intent classifier for VIT admission queries.

Analyze this query and classify it:
- "cutoff" - Questions about admission cutoffs, closing ranks
- "rank_prediction" - Student provides rank, wants eligible branches
- "faq" - Questions about hostel, FFCS, clubs, campus life, fees

Query: "{query}"

Respond ONLY with valid JSON:
{{
    "intent": "one of the above",
    "confidence": 0.85,
    "reasoning": "brief explanation"
}}"""
            try:
                response = self.model.generate_content(prompt)
                result_text = response.text.strip()

                if "```json" in result_text:
                    result_text = result_text.split("```json")[1].split("```")[0].strip()
                elif "```" in result_text:
                    result_text = result_text.split("```")[1].split("```")[0].strip()

                result = json.loads(result_text)
                print(f"✨ Gemini classified intent as: {result['intent']} ({result.get('confidence', 0)})")
                return result
            except Exception as e:
                print(f"Error in Gemini intent classification: {e}")

        # ✅ Last resort: fallback keyword logic
        print("⚙️ Using fallback intent classification.")
        return self._fallback_classify(query)

    def _fallback_classify(self, query: str) -> Dict:
        query_lower = query.lower()

        if any(word in query_lower for word in ["rank", "got", "scored"]):
            if any(char.isdigit() for char in query):
                return {"intent": "rank_prediction", "confidence": 0.7, "reasoning": "Contains rank"}

        if any(word in query_lower for word in ["cutoff", "closing rank"]):
            return {"intent": "cutoff", "confidence": 0.7, "reasoning": "About cutoffs"}

        return {"intent": "faq", "confidence": 0.6, "reasoning": "General query"}

    # -------------------- Response Generation -------------------- #
    def generate_response(self, query: str, context: str, intent: str) -> str:
        """
        Generates a helpful answer using Groq first, then Gemini, and finally fallback text if both fail.
        """
        # ✅ Try Groq first
        if hasattr(self, "groq") and self.groq.is_available():
            try:
                result = self.groq.generate_response(query, context, intent)
                if result:
                    print("🧠 Groq generated the response successfully.")
                    return result
            except Exception as e:
                print(f"Groq response generation error: {e}")

        # ✅ Fallback to Gemini if available
        if not self.is_available():
            # Neither Groq nor Gemini available → use fallback text
            return f"Based on available information:\n\n{context[:500]}"

        # Build prompt by intent
        if intent == "rank_prediction":
            prompt = f"""You are a friendly VIT admission assistant helping a 12th-grade student.

Student asked: "{query}"

Admission data:
{context}

Provide a helpful response (under 100 words) that:
1. Answers their question about branch eligibility
2. Mentions 2–3 realistic options
3. Keeps a positive tone
4. Suggests exploring other options

Response:"""

        elif intent == "cutoff":
            prompt = f"""You are a VIT admission assistant.

Student asked: "{query}"

Cutoff information:
{context}

Provide a clear answer (under 80 words) that:
1. Addresses their cutoff question
2. Mentions specific ranks/categories
3. Keeps a helpful tone

Response:"""

        elif intent == "faq":
            prompt = f"""You are a friendly VIT admission assistant.

Student asked: "{query}"

Information:
{context}

Provide a natural answer (under 100 words) that:
1. Directly answers the question
2. Uses simple language
3. Sounds helpful

Response:"""

        else:
            prompt = f"""Student asked: "{query}"

Context: {context}

Provide a helpful response in under 80 words."""

        # Try Gemini
        try:
            response = self.model.generate_content(prompt)
            print("✨ Gemini generated the response successfully.")
            return response.text.strip()
        except Exception as e:
            print(f"Error generating response with Gemini: {e}")
            return "I'm having trouble responding. Please try again."