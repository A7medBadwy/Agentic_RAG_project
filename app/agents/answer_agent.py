from app.services.llm import chat_completion

class AnswerAgent:
    async def answer(self, question: str, evidence: list[dict], analysis: dict) -> str:
        if not evidence:
            return "I couldn't find supporting information in the uploaded documents. Please upload relevant documents or rephrase your question."
        context_parts = []
        for i, item in enumerate(evidence, 1):
            context_parts.append(
                f"[{i}] File: {item.get('document_name')} | Page: {item.get('page_number')}\n{item.get('text', '')}"
            )
        context = "\n\n".join(context_parts)
        system = (
            "You are a document-grounded assistant. Use only the supplied evidence. "
            "Answer directly in 1–3 short sentences by default. "
            "Do not include a preamble, evidence list, headings, setup instructions, or discussion of your process. "
            "Use brief bullets only when the question asks for multiple items or a comparison. "
            "If the evidence does not support an answer, say so briefly. "
            "Do not include inline citations; sources are displayed separately. Never invent facts."
        )
        prompt = (
            f"Question: {question}\n\nEvidence:\n{context}\n\n"
            f"Analyst findings (internal guidance; do not mention): {analysis}\n\n"
            "Return only the answer."
        )
        generated = await chat_completion(system, prompt)
        if generated:
            return generated
        return "Answer generation is unavailable. Set OPENROUTER_API_KEY in .env to enable concise answers from your documents."
