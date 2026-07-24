import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


def _get_groq_client():
    from groq import Groq
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not set in environment")
    return Groq(api_key=api_key)


def generate_response(user_query, rag_context="", system_prompt=""):
    """Generate a response using Groq Llama 3.1 8B with RAG context."""
    client = _get_groq_client()

    if not system_prompt:
        system_prompt = (
            "You are a medical AI assistant. Given the user's query and relevant medical context, "
            "provide a clear, accurate, and helpful response. Be concise and to-the-point. "
            "Do not fabricate information. If the context doesn't contain enough information, say so. "
            "Always recommend consulting a healthcare professional for medical decisions."
        )

    messages = [{"role": "system", "content": system_prompt}]

    if rag_context:
        messages.append({
            "role": "system",
            "content": f"Relevant medical knowledge from database:\n{rag_context}"
        })

    messages.append({"role": "user", "content": user_query})

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.3,
            max_completion_tokens=1024,
            top_p=0.9,
            stream=False,
        )
        return completion.choices[0].message.content
    except Exception as e:
        logger.error(f"Groq API error: {e}")
        return f"Error generating response: {str(e)}"


def analyze_medical_report(report_text, language="english"):
    """Analyze a medical report using Groq with RAG context."""
    from rag import build_rag_context

    rag_context = build_rag_context(report_text, n_results=3)

    lang_map = {
        "english": "English",
        "hindi": "Hindi",
        "hinglish": "Romanized Hindi (Hinglish)",
    }
    target_lang = lang_map.get(language.lower(), "English")

    system_prompt = f"""You are a medical report analyzer. Respond in {target_lang}.
Break down the entire document thoroughly:
- Summary: bullet list covering all major sections
- Findings: detailed bullets for every notable item
- Terms: medical terms with brief layman explanations
- Recommendations: actionable, clear, concise

Return JSON in this exact format:
{{
    "summary": ["bullet 1", "bullet 2"],
    "findings": [{{"emoji": "emoji", "text": "finding"}}],
    "terms": [{{"term": "medical term", "explanation": "brief explanation"}}],
    "recommendations": [{{"emoji": "emoji", "title": "title", "description": "description"}}]
}}
Output pure text/Markdown, no HTML."""

    query = f"Analyze this medical report:\n\n{report_text[:3000]}"
    return generate_response(query, rag_context, system_prompt)
