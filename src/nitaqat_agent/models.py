"""Validated catalog and report contracts."""

from typing import Literal

from pydantic import BaseModel, Field

Language = Literal["en", "ar"]


class Translation(BaseModel):
    en: str
    ar: str

    def in_language(self, language: Language) -> str:
        return self.ar if language == "ar" else self.en


class Role(BaseModel):
    id: str
    title: Translation
    required: list[str] = Field(min_length=1)


class Catalog(BaseModel):
    source: Literal["synthetic"]
    skills: dict[str, Translation]
    roles: list[Role] = Field(min_length=1)
    practice: dict[str, Translation]


class Match(BaseModel):
    role: str
    matched: list[str]
    missing: list[str]
    coverage: float = Field(ge=0, le=1)


class Recommendation(BaseModel):
    action: str
    sdg_target: Literal["8.5", "8.6", "4.4"]
    confidence: str


class Report(BaseModel):
    language: Language
    data_source: Literal["synthetic"] = "synthetic"
    summary: str
    unrecognized_count: int = Field(ge=0)
    matches: list[Match]
    recommendations: list[Recommendation]
