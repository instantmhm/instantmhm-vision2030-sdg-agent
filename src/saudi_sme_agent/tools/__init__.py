"""Catalog loading, route analysis, checklist creation and report generation."""

from importlib.resources import files

from saudi_sme_agent.models import (
    Catalog,
    Goal,
    Language,
    Recommendation,
    Report,
    Route,
)


def load_catalog() -> Catalog:
    """Read validated project-authored summaries from the installed package."""
    path = files("saudi_sme_agent").joinpath("data", "catalog.json")
    catalog = Catalog.model_validate_json(path.read_text(encoding="utf-8"))
    if len({route.id for route in catalog.routes}) != len(catalog.routes):
        raise ValueError("Catalog route IDs must be unique.")
    for route in catalog.routes:
        expected_target = "8.3" if route.goal == "licensing" else "9.3"
        if route.source_url.scheme != "https" or route.sdg_target != expected_target:
            raise ValueError(f"Invalid source or target for route {route.id}.")
    return catalog


def select_routes(catalog: Catalog, goal: Goal) -> list[Route]:
    """Return relevant routes in checklist order."""
    return [route for route in catalog.routes if goal == "both" or route.goal == goal]


def build_checklist(routes: list[Route], language: Language) -> list[Recommendation]:
    """Translate curated action and confidence text while retaining source links."""
    return [
        Recommendation(
            id=route.id,
            action=route.action.in_language(language),
            sdg_target=route.sdg_target,
            confidence=route.confidence.in_language(language),
            source_url=route.source_url,
        )
        for route in routes
    ]


def generate_report(
    goal: Goal, language: Language, checklist: list[Recommendation]
) -> Report:
    """Assemble a validated bilingual navigation report."""
    summary = (
        "دليل إرشادي. تحقّق من المتطلبات الحالية لدى الجهة المختصة."
        if language == "ar"
        else "Navigation checklist. Verify current requirements with the relevant authority."
    )
    return Report(
        language=language, goal=goal, summary=summary, recommendations=checklist
    )
