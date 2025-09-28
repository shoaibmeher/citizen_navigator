# agents/intent_agent.py

def detect_service_intent(user_query: str, openai_client=None):
    """
    Detects which public service the citizen is asking about.
    Returns: (service_key, confidence, rationale)
    """

    query = user_query.lower()

    # Rule-based fallback intent detection
    if "zakat" in query or "charity" in query:
        return "zakat", 95, "User is asking about Zakat financial support."
    elif "transport" in query or "bus" in query or "card" in query:
        return "ptc_transport", 90, "User is asking about a free senior transport card."
    elif "immunization" in query or "vaccination" in query or "child health" in query:
        return "health_immunization", 90, "User is asking about child vaccination services."
    elif "house" in query or "housing" in query or "home" in query or "lda" in query or "shelter" in query:
        return "housing_support", 88, "User is asking about government housing or LDA schemes."
    else:
        return None, 0, "Service not recognized."
