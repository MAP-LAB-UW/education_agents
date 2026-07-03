"""Thin wrapper over litellm for LLM calls."""

from __future__ import annotations

import json
import os
import re

import litellm
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

DEFAULT_MODEL = os.getenv("EDU_AGENTS_MODEL", "anthropic/claude-sonnet-4-6")

_FENCE_RE = re.compile(r"^```[a-zA-Z]*\s*|\s*```$")


def _coerce_json(raw: str) -> str:
    """Strip markdown code fences some models (e.g. Anthropic Haiku) wrap JSON in.

    Falls back to extracting the outermost {...} block if fences alone don't
    yield clean JSON.
    """
    s = raw.strip()
    if s.startswith("```"):
        s = _FENCE_RE.sub("", s).strip()
    try:
        json.loads(s)
        return s
    except Exception:
        start, end = s.find("{"), s.rfind("}")
        if start != -1 and end > start:
            return s[start : end + 1]
        return s


def complete(
    messages: list[dict],
    model: str | None = None,
    **kwargs,
) -> str:
    model = model or DEFAULT_MODEL
    response = litellm.completion(model=model, messages=messages, **kwargs)
    return response.choices[0].message.content


def structured_complete(
    messages: list[dict],
    schema: type[BaseModel],
    model: str | None = None,
    **kwargs,
) -> BaseModel:
    model = model or DEFAULT_MODEL
    try:
        response = litellm.completion(
            model=model,
            messages=messages,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": schema.__name__,
                    "schema": schema.model_json_schema(),
                },
            },
            **kwargs,
        )
        raw = response.choices[0].message.content
        return schema.model_validate_json(_coerce_json(raw))
    except Exception:
        schema_hint = json.dumps(schema.model_json_schema(), indent=2)
        fallback_messages = list(messages)
        fallback_messages.append({
            "role": "user",
            "content": (
                f"Respond as JSON matching this exact schema "
                f"(use these exact field names):\n```json\n{schema_hint}\n```"
            ),
        })
        response = litellm.completion(
            model=model,
            messages=fallback_messages,
            response_format={"type": "json_object"},
            **kwargs,
        )
        raw = response.choices[0].message.content
        return schema.model_validate_json(_coerce_json(raw))
