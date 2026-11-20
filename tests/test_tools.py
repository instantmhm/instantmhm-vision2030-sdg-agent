from pathlib import Path

from nitaqat_agent.tools import (
    analyze_matches,
    generate_report,
    load_catalog,
    recommend,
)


def test_catalog_matches_source():
    root = Path(__file__).resolve().parents[1]
    source = root / "data/sample/catalog.json"
    packaged = root / "src/nitaqat_agent/data/catalog.json"
    assert source.read_bytes() == packaged.read_bytes()
    assert load_catalog().source == "synthetic"


def test_match_ranking_and_arabic_parity():
    catalog = load_catalog()
    en, en_gaps, en_unknown = analyze_matches(catalog, ["Excel", "SQL", "other"], "en")
    ar, ar_gaps, ar_unknown = analyze_matches(
        catalog, ["إِكسِل", "اس كيو ال", "آخر"], "ar"
    )
    assert [match.role for match in en] == [
        "Junior data analyst",
        "Operations assistant",
    ]
    assert ar[0].role == "محلل بيانات مبتدئ"
    assert [match.coverage for match in en] == [2 / 3, 1 / 2]
    assert [match.coverage for match in ar] == [match.coverage for match in en]
    assert en_gaps == ar_gaps == ["visualization"]
    assert en_unknown == ar_unknown == 1


def test_recommendations_have_tags_and_confidence():
    catalog = load_catalog()
    matches, gaps, _ = analyze_matches(catalog, ["Excel", "SQL"], "en")
    actions = recommend(catalog, matches, gaps, "en")
    assert [action.sdg_target for action in actions] == ["8.5", "4.4"]
    assert all(action.confidence for action in actions)
    assert recommend(catalog, [], [], "ar")[0].sdg_target == "8.6"


def test_report_keeps_catalog_provenance():
    recommendations = recommend(load_catalog(), [], [], "en")
    report = generate_report([], recommendations, 1, "en")
    assert report.data_source == "synthetic"
    assert report.recommendations == recommendations
    assert report.unrecognized_count == 1
