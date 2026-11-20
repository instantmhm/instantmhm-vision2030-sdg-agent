"""Contracts for the public-service catalog and navigation reports."""

from typing import Literal

from pydantic import BaseModel, Field, HttpUrl

Language = Literal["en", "ar"]
Goal = Literal["licensing", "financing", "both"]
Target = Literal["8.3", "9.3"]


class Translation(BaseModel):
    en: str
    ar: str

    def in_language(self, language: Language) -> str:
        return self.ar if language == "ar" else self.en


class Route(BaseModel):
    id: str
    goal: Literal["licensing", "financing"]
    action: Translation
    confidence: Translation
    source_url: HttpUrl
    sdg_target: Target


class Catalog(BaseModel):
    source: Literal["curated_official_references"]
    routes: list[Route] = Field(min_length=1)


class Recommendation(BaseModel):
    id: str
    action: str
    sdg_target: Target
    confidence: str
    source_url: HttpUrl


class Report(BaseModel):
    language: Language
    goal: Goal
    source: Literal["curated_official_references"] = "curated_official_references"
    summary: str
    recommendations: list[Recommendation]
