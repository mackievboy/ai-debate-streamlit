from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Callable, Literal
from uuid import uuid4

import requests


ProviderId = Literal["chatgpt", "claude", "gemini"]
PROVIDER_NAMES: dict[ProviderId, str] = {
    "chatgpt": "ChatGPT",
    "claude": "Claude",
    "gemini": "Gemini",
}
DEFAULT_MODELS: dict[ProviderId, str] = {
    "chatgpt": "gpt-5.6-sol",
    "claude": "claude-sonnet-5",
    "gemini": "gemini-3.8-flash",
}


@dataclass(frozen=True)
class Answer:
    provider: ProviderId
    label: str
    text: str


def _checked_json(response: requests.Response, provider: ProviderId) -> dict:
    try:
        body = response.json()
    except requests.JSONDecodeError:
        body = {}
    if response.ok:
        return body
    if response.status_code in (401, 403):
        raise RuntimeError(f"{PROVIDER_NAMES[provider]} API 키 인증에 실패했습니다.")
    if response.status_code == 429:
        raise RuntimeError(f"{PROVIDER_NAMES[provider]} API 사용량 제한에 도달했습니다.")
    detail = body.get("error", {}).get("message") or body.get("message")
    suffix = f": {detail}" if detail else ""
    raise RuntimeError(
        f"{PROVIDER_NAMES[provider]} API 요청 실패 ({response.status_code}){suffix}"
    )


def ask_provider(
    provider: ProviderId,
    api_key: str,
    model: str,
    prompt: str,
    timeout: int = 600,
) -> str:
    if provider == "chatgpt":
        response = requests.post(
            "https://api.openai.com/v1/responses",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"model": model, "input": prompt, "max_output_tokens": 5000},
            timeout=timeout,
        )
        body = _checked_json(response, provider)
        text = body.get("output_text")
        if not text:
            for item in body.get("output", []):
                for content in item.get("content", []):
                    if content.get("type") == "output_text" and content.get("text"):
                        text = content["text"]
                        break
    elif provider == "claude":
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": model,
                "max_tokens": 5000,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=timeout,
        )
        body = _checked_json(response, provider)
        text = "\n".join(
            item.get("text", "")
            for item in body.get("content", [])
            if item.get("type") == "text"
        )
    else:
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
            headers={"x-goog-api-key": api_key, "content-type": "application/json"},
            json={
                "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                "generationConfig": {"maxOutputTokens": 5000},
            },
            timeout=timeout,
        )
        body = _checked_json(response, provider)
        candidates = body.get("candidates", [])
        parts = candidates[0].get("content", {}).get("parts", []) if candidates else []
        text = "\n".join(part.get("text", "") for part in parts if part.get("text"))
    if not text or not str(text).strip():
        raise RuntimeError(f"{PROVIDER_NAMES[provider]}가 빈 응답을 반환했습니다.")
    return str(text).strip()


def validate_debate(
    question: str,
    participants: list[ProviderId],
    finalizer: ProviderId,
    keys: dict[ProviderId, str],
    models: dict[ProviderId, str],
) -> None:
    if not 3 <= len(question.strip()) <= 12_000:
        raise ValueError("질문은 3~12,000자로 입력해 주세요.")
    if not 2 <= len(participants) <= 3 or len(set(participants)) != len(participants):
        raise ValueError("서로 다른 AI를 두 개 이상 선택해 주세요.")
    if finalizer not in participants:
        raise ValueError("최종 종합 AI는 참여 AI 중에서 선택해야 합니다.")
    for provider in participants:
        if not keys.get(provider, "").strip():
            raise ValueError(f"{PROVIDER_NAMES[provider]} API 키가 필요합니다.")
        if not models.get(provider, "").strip():
            raise ValueError(f"{PROVIDER_NAMES[provider]} 모델명이 필요합니다.")


def run_debate(
    question: str,
    participants: list[ProviderId],
    finalizer: ProviderId,
    keys: dict[ProviderId, str],
    models: dict[ProviderId, str],
    progress: Callable[[str, str], None] | None = None,
) -> dict:
    validate_debate(question, participants, finalizer, keys, models)
    notify = progress or (lambda _stage, _message: None)

    notify("initial", "각 AI가 독립적으로 질문을 분석하고 있습니다.")

    def initial_task(item: tuple[int, ProviderId]) -> Answer:
        index, provider = item
        prompt = (
            f"당신은 {PROVIDER_NAMES[provider]}이며 다중 AI 토론의 독립 분석가입니다. "
            "다른 참가자의 답을 보지 않고 질문에 직접 답하세요. 정확성, 근거, 실행 "
            f"가능성을 우선하고 불확실한 내용은 명시하세요.\n\n질문:\n{question}"
        )
        return Answer(
            provider,
            f"답변 {chr(65 + index)}",
            ask_provider(provider, keys[provider], models[provider], prompt),
        )

    with ThreadPoolExecutor(max_workers=len(participants)) as executor:
        answers = list(executor.map(initial_task, enumerate(participants)))

    notify("critique", "작성자를 숨긴 채 익명 상호 비평을 진행하고 있습니다.")

    def critique_task(provider: ProviderId) -> Answer:
        anonymous = "\n\n---\n\n".join(
            f"익명 답변 {chr(65 + index)}:\n{answer.text}"
            for index, answer in enumerate(
                answer for answer in answers if answer.provider != provider
            )
        )
        prompt = (
            "당신은 다중 AI 토론의 비평가입니다. 작성자의 정체를 추측하거나 언급하지 "
            "마세요. 각 답변의 강점, 사실 오류 가능성, 빠진 관점, 논리적 약점을 검토하고 "
            f"수정안을 제시하세요.\n\n원래 질문:\n{question}\n\n{anonymous}"
        )
        return Answer(
            provider,
            f"{PROVIDER_NAMES[provider]} 비평",
            ask_provider(provider, keys[provider], models[provider], prompt),
        )

    with ThreadPoolExecutor(max_workers=len(participants)) as executor:
        critiques = list(executor.map(critique_task, participants))

    notify("final", f"{PROVIDER_NAMES[finalizer]}가 최종안을 종합하고 있습니다.")
    answer_text = "\n\n---\n\n".join(
        f"{answer.label}:\n{answer.text}" for answer in answers
    )
    critique_text = "\n\n---\n\n".join(
        f"비평 {index + 1}:\n{critique.text}"
        for index, critique in enumerate(critiques)
    )
    final_prompt = (
        "당신은 다중 AI 토론의 최종 편집자입니다. 독립 답변과 익명 상호 비평을 "
        "종합해 하나의 완결된 최종 답변을 작성하세요. 오류를 교정하고 합의점을 채택하며 "
        "남은 이견과 불확실성은 명확히 구분하세요. 자연스러운 한국어로 답하세요."
        f"\n\n원래 질문:\n{question}\n\n[독립 답변]\n{answer_text}"
        f"\n\n[상호 비평]\n{critique_text}"
    )
    final_answer = ask_provider(
        finalizer, keys[finalizer], models[finalizer], final_prompt
    )
    notify("done", "최종 합의안을 완성했습니다.")
    return {
        "id": str(uuid4()),
        "question": question.strip(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "participants": participants,
        "answers": [asdict(answer) for answer in answers],
        "critiques": [asdict(critique) for critique in critiques],
        "final_answer": final_answer,
        "finalizer": finalizer,
    }
