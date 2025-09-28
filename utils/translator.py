# utils/translator.py
def get_openai_client(api_key: str):
    if not api_key:
        return None
    try:
        from openai import OpenAI
        return OpenAI(api_key=api_key)
    except Exception:
        return None

def explain_in_english(client, service_key, form_data, eligible, reasons, required_docs, degraded=False, max_tokens=220):
    status = "Eligible" if eligible else "Not eligible"
    base = f"{status}. "
    brief = "; ".join(reasons[:3]) if reasons else ""
    docs = ", ".join(required_docs[:4]) if required_docs else ""
    if degraded or client is None:
        text = f"{base}Reason(s): {brief}. Required documents: {docs}."
        return text.strip()

    try:
        content = f"""
You are a government service assistant. Write a concise explanation (<= 120 words) for a citizen about their eligibility result.
Service: {service_key}
Eligibility: {status}
Key reasons: {reasons}
Required documents: {required_docs}
Citizen inputs (for reference): {form_data}
Avoid policy jargon; keep it simple, friendly, and instructional.
"""
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": content}],
            max_tokens=max_tokens,
            temperature=0.2,
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        return f"{base}Reason(s): {brief}. Required documents: {docs}."

def translate_to_urdu(client, english_text: str, degraded=False, max_tokens=220):
    if degraded or client is None:
        return "❗ آف لائن موڈ: اردو ترجمہ فی الحال دستیاب نہیں۔\n\n" + english_text
    try:
        content = f"Translate this into Urdu. Keep it short, simple and friendly:\n\n{english_text}"
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": content}],
            max_tokens=max_tokens,
            temperature=0.2,
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        return "❗ ترجمہ دستیاب نہیں۔"
