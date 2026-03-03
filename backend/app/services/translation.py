from __future__ import annotations

import asyncio

import httpx

from app.models.schemas import JobSettings, Segment

SYSTEM_PROMPT = (
    "あなたは字幕翻訳の専門家です。"
    "与えられた外国語の字幕テキストを自然な日本語に翻訳してください。"
    "翻訳文のみを出力し、説明や注釈は一切加えないでください。"
    "字幕の簡潔さを保ち、原文の意味とニュアンスを忠実に伝えてください。"
)


def _build_prompt(segments: list[Segment], index: int, context_window: int) -> str:
    """Build translation prompt with surrounding context segments."""
    start = max(0, index - context_window)
    end = min(len(segments), index + context_window + 1)

    context_before = [segments[i].text for i in range(start, index)]
    context_after = [segments[i].text for i in range(index + 1, end)]
    target = segments[index].text

    parts: list[str] = []
    if context_before:
        parts.append("【前の字幕】\n" + "\n".join(context_before))
    parts.append("【翻訳対象】\n" + target)
    if context_after:
        parts.append("【後の字幕】\n" + "\n".join(context_after))

    return "\n\n".join(parts)


async def _translate_one(
    client: httpx.AsyncClient,
    sem: asyncio.Semaphore,
    segments: list[Segment],
    index: int,
    job_settings: JobSettings,
) -> Segment:
    """Translate a single segment, respecting concurrency limit."""
    async with sem:
        prompt = _build_prompt(segments, index, job_settings.translation_context_window)
        payload = {
            "model": job_settings.translation_model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "stream": False,
        }
        response = await client.post(
            f"{job_settings.ollama_base_url}/api/chat",
            json=payload,
            timeout=120.0,
        )
        response.raise_for_status()
        ja_text = response.json()["message"]["content"].strip()
        return segments[index].model_copy(update={"ja_text": ja_text})


async def translate_segments(
    segments: list[Segment],
    job_settings: JobSettings,
) -> list[Segment]:
    """Translate all segments in parallel, limited by translation_parallel."""
    if not segments:
        return segments

    sem = asyncio.Semaphore(job_settings.translation_parallel)
    async with httpx.AsyncClient() as client:
        tasks = [
            _translate_one(client, sem, segments, i, job_settings)
            for i in range(len(segments))
        ]
        return list(await asyncio.gather(*tasks))
