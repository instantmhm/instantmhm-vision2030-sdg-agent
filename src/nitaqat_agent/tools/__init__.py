"""Career exploration tools with deterministic evidence and bilingual output."""

import unicodedata
from fractions import Fraction
from importlib.resources import files

from nitaqat_agent.models import Catalog, Language, Match, Recommendation, Report

ALEF_VARIANTS = str.maketrans("أإآٱ", "اااا")


def normalize(label: str) -> str:
    """Normalize a skill label without guessing its meaning."""
    text = unicodedata.normalize("NFKC", label).translate(ALEF_VARIANTS)
    plain = "".join(
        char for char in text if unicodedata.category(char) != "Mn" and char != "ـ"
    )
    return " ".join(plain.casefold().split())


def load_catalog() -> Catalog:
    """Load and validate the packaged synthetic data."""
    path = files("nitaqat_agent").joinpath("data", "catalog.json")
    catalog = Catalog.model_validate_json(path.read_text(encoding="utf-8"))
    if len({role.id for role in catalog.roles}) != len(catalog.roles):
        raise ValueError("Catalog role IDs must be unique.")
    for role in catalog.roles:
        if len(set(role.required)) != len(role.required):
            raise ValueError(f"Duplicate skill in role {role.id}.")
        if not set(role.required) <= catalog.skills.keys():
            raise ValueError(f"Unknown skill in role {role.id}.")
    if not catalog.practice.keys() <= catalog.skills.keys():
        raise ValueError("Practice catalog contains an unknown skill.")
    return catalog


def analyze_matches(
    catalog: Catalog, labels: list[str], language: Language
) -> tuple[list[Match], list[str], int]:
    """Rank roles by the fraction of requirements covered by recognized skills."""
    aliases = {
        normalize(alias): skill_id
        for skill_id, translation in catalog.skills.items()
        for alias in (skill_id, translation.en, translation.ar)
    }
    entered = {normalize(label) for label in labels if label.strip()}
    recognized = {aliases[label] for label in entered & aliases.keys()}
    ranked = []
    for role in catalog.roles:
        matched = [skill for skill in role.required if skill in recognized]
        if not matched:
            continue
        missing = [skill for skill in role.required if skill not in recognized]
        coverage = Fraction(len(matched), len(role.required))
        match = Match(
            role=role.title.in_language(language),
            matched=[catalog.skills[skill].in_language(language) for skill in matched],
            missing=[catalog.skills[skill].in_language(language) for skill in missing],
            coverage=float(coverage),
        )
        ranked.append((coverage, len(matched), role.id, match, missing))
    ranked.sort(key=lambda item: (-item[0], -item[1], item[2]))
    top_gaps = ranked[0][4] if ranked else []
    return [item[3] for item in ranked], top_gaps, len(entered - aliases.keys())


def recommend(
    catalog: Catalog, matches: list[Match], gaps: list[str], language: Language
) -> list[Recommendation]:
    """Suggest human-reviewed actions and practice for the top role."""
    if language == "ar":
        role_action = "راجع دور «{}» ومتطلباته مع مرشد مهني."
        recovery = "أضف مسميات مهارات من القائمة التجريبية أو راجعها مع مرشد مهني."
        role_note = "تطابق استرشادي يعتمد على مهارات مصرح بها وكتالوج اصطناعي."
        recovery_note = "أدلة المطابقة غير كافية ضمن الكتالوج التجريبي."
        practice_note = "تمرين توضيحي مرتبط بفجوة مهارية في الكتالوج الاصطناعي."
    else:
        role_action = "Review the {} role and its requirements with a career counselor."
        recovery = (
            "Add skills from the sample catalog or review your skills with a counselor."
        )
        role_note = (
            "Illustrative match based on self-reported skills and a synthetic catalog."
        )
        recovery_note = "Insufficient matching evidence in the sample catalog."
        practice_note = (
            "Illustrative practice for a skill gap in the synthetic catalog."
        )
    if not matches:
        return [
            Recommendation(action=recovery, sdg_target="8.6", confidence=recovery_note)
        ]
    return [
        Recommendation(
            action=role_action.format(matches[0].role),
            sdg_target="8.5",
            confidence=role_note,
        ),
        *[
            Recommendation(
                action=catalog.practice[skill].in_language(language),
                sdg_target="4.4",
                confidence=practice_note,
            )
            for skill in gaps
            if skill in catalog.practice
        ],
    ]


def generate_report(
    matches: list[Match],
    recommendations: list[Recommendation],
    unrecognized_count: int,
    language: Language,
) -> Report:
    """Render validated findings with a catalog limitation in either language."""
    summary = (
        "استكشاف مهني باستخدام كتالوج اصطناعي. النتائج لا تمثل شواغر فعلية."
        if language == "ar"
        else "Career exploration using a synthetic catalog. Results do not represent vacancies."
    )
    return Report(
        language=language,
        summary=summary,
        unrecognized_count=unrecognized_count,
        matches=matches,
        recommendations=recommendations,
    )
