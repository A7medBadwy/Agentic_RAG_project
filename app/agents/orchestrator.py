from app.agents.retriever_agent import RetrieverAgent
from app.agents.analyst_agent import AnalystAgent
from app.agents.answer_agent import AnswerAgent
from app.core.config import settings

class Orchestrator:
    def __init__(self):
        self.retriever = RetrieverAgent()
        self.analyst = AnalystAgent()
        self.answerer = AnswerAgent()

    async def run(self, question: str):
        rewritten = self.retriever.rewrite_query(question)
        evidence = self.retriever.retrieve(rewritten)
        analysis = self.analyst.analyze(question, evidence)
        rounds = 0

        # Bounded feedback loop. The second search broadens the query with key terms.
        while not analysis["sufficient_evidence"] and rounds < settings.max_feedback_rounds:
            rounds += 1
            broader_query = f"{rewritten} relevant details definitions explanation"
            extra = self.retriever.retrieve(broader_query, limit=settings.top_k + 4)
            known = {x.get("chunk_id") for x in evidence}
            evidence.extend(x for x in extra if x.get("chunk_id") not in known)
            analysis = self.analyst.analyze(question, evidence)

        answer = await self.answerer.answer(question, evidence, analysis)
        citations = []
        seen = set()
        for item in evidence:
            key = (item.get("document_name"), item.get("page_number"), item.get("chunk_id"))
            if key not in seen:
                seen.add(key)
                citations.append({
                    "document_name": key[0] or "Unknown",
                    "page_number": key[1] or 1,
                    "chunk_id": key[2] or "unknown"
                })
        return {
            "answer": answer,
            "citations": citations,
            "evidence_count": len(evidence),
            "feedback_rounds": rounds,
            "analysis": analysis
        }
