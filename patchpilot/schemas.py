import json
import re
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

SECRET_KEYS = re.compile(
    r"^(api[_-]?key|authorization|password|secret|access[_-]?token|client[_-]?secret)$", re.I
)
SECRET_VALUE = re.compile(
    r"(?:sk_(?:live|test)_[A-Za-z0-9]{12,}|gsk_[A-Za-z0-9]{20,}|nvapi-[A-Za-z0-9]{20,})"
)


def check_secrets(value):
    if isinstance(value, dict):
        for key, item in value.items():
            if SECRET_KEYS.match(str(key)) and item:
                raise ValueError("Remove credentials from incident data before uploading")
            check_secrets(item)
    elif isinstance(value, list):
        for item in value:
            check_secrets(item)
    elif isinstance(value, str) and SECRET_VALUE.search(value):
        raise ValueError("Remove credentials from incident data before uploading")


class AcceptanceCase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    input: Any
    expected: Any


class IncidentRequest(BaseModel):
    title: str = Field(min_length=3, max_length=160)
    vendor: Literal["stripe", "github", "slack", "shopify"] = "stripe"
    target_version: str = Field(min_length=1, max_length=100)
    mode: Literal["replay", "live"] = "replay"
    source_code: str = Field(min_length=10, max_length=12000)
    entrypoint: str = Field(default="normalize_invoice", pattern=r"^[a-zA-Z][a-zA-Z0-9_]{0,59}$")
    cases: list[AcceptanceCase] = Field(min_length=1, max_length=12)
    symptom: str = Field(default="Adapter fails after an API version upgrade", max_length=2000)
    search_hint: str = Field(default="", max_length=200)
    max_attempts: int = Field(default=3, ge=1, le=3)
    replay_scenario: Literal["repair", "recovery", "no_evidence", "auth"] = "repair"

    @model_validator(mode="after")
    def protect_input(self):
        data = self.model_dump()
        if len(json.dumps(data, allow_nan=False)) > 100000:
            raise ValueError("Incident JSON exceeds the 100,000 character limit")
        check_secrets(data)
        if "__" in self.entrypoint:
            raise ValueError("Entrypoint cannot contain dunder identifiers")
        return self
