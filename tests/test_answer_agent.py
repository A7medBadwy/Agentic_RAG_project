import asyncio

from app.agents import answer_agent
from app.agents.answer_agent import AnswerAgent


def test_generated_answer_is_direct_and_consistent(monkeypatch):
    prompts = {}

    async def fake_chat_completion(system_prompt, user_prompt):
        prompts["system"] = system_prompt
        prompts["user"] = user_prompt
        return "A Runnable takes an input and produces an output."

    monkeypatch.setattr(answer_agent, "chat_completion", fake_chat_completion)

    result = asyncio.run(AnswerAgent().answer(
        "What is a Runnable?",
        [{"document_name": "chains.pdf", "page_number": 8, "text": "A Runnable receives input and produces output."}],
        {},
    ))

    assert result == "A Runnable takes an input and produces an output."
    assert "1–3 short sentences" in prompts["system"]
    assert "Do not include inline citations" in prompts["system"]
    assert "Return only the answer." in prompts["user"]


def test_missing_api_key_does_not_return_passage_dump(monkeypatch):
    async def fake_chat_completion(system_prompt, user_prompt):
        return None

    monkeypatch.setattr(answer_agent, "chat_completion", fake_chat_completion)

    result = asyncio.run(AnswerAgent().answer(
        "What is a Runnable?",
        [{"document_name": "chains.pdf", "page_number": 8, "text": "Raw passage text."}],
        {},
    ))

    assert result == (
        "Answer generation is unavailable. Set OPENROUTER_API_KEY in .env "
        "to enable concise answers from your documents."
    )
    assert "Raw passage text" not in result
