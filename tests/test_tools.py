from pathlib import Path

from saudi_sme_agent.tools import (
    build_checklist,
    generate_report,
    load_catalog,
    select_routes,
)


def test_catalog_matches_source():
    root = Path(__file__).resolve().parents[1]
    source = root / "data/sample/catalog.json"
    packaged = root / "src/saudi_sme_agent/data/catalog.json"
    assert source.read_bytes() == packaged.read_bytes()
    assert load_catalog().source == "curated_official_references"


def test_each_goal_selects_relevant_routes():
    catalog = load_catalog()
    licensing = select_routes(catalog, "licensing")
    financing = select_routes(catalog, "financing")
    assert [route.id for route in licensing] == [
        "registration",
        "municipal-requirements",
        "municipal-license",
    ]
    assert [route.id for route in financing] == ["financing-gate", "kafalah"]
    assert select_routes(catalog, "both") == licensing + financing


def test_checklist_language_parity_and_provenance():
    routes = select_routes(load_catalog(), "both")
    en = build_checklist(routes, "en")
    ar = build_checklist(routes, "ar")
    assert [(item.id, item.source_url, item.sdg_target) for item in en] == [
        (item.id, item.source_url, item.sdg_target) for item in ar
    ]
    assert all(
        item.source_url.scheme == "https" and item.confidence for item in en + ar
    )
    assert en[0].action != ar[0].action
    assert "guarantee to the financier" in en[-1].action


def test_report_uses_validated_checklist():
    actions = build_checklist(select_routes(load_catalog(), "financing"), "ar")
    report = generate_report("financing", "ar", actions)
    assert report.goal == "financing"
    assert report.language == "ar"
    assert report.recommendations == actions
