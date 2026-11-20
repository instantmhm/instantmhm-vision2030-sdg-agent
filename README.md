# Bilingual job–skill matching under Nitaqat

[![Saudi Vision 2030](https://img.shields.io/badge/Saudi_Vision-2030-087b51)](https://www.vision2030.gov.sa/en/overview/pillars/a-thriving-economy)
[![SDG 8](https://img.shields.io/badge/SDG_8-Decent_Work-a21942)](https://sdgs.un.org/goals/goal8)
[![SDG 4](https://img.shields.io/badge/SDG_4-Quality_Education-c5192d)](https://sdgs.un.org/goals/goal4)

Saudi youth and women exploring private-sector employment need to understand which skills transfer to a role and which gaps to address first. This career-exploration agent compares user-entered skills with an illustrative role catalog and generates a structured Arabic or English report. Nitaqat Mutawar supplies the policy context for private-sector localization. [Problem selection and sources](docs/PROBLEM_SELECTION.md)

| Framework | Objective or target | Indicator or prototype measurement |
|---|---|---|
| Vision 2030, Thriving Economy / HCDP | Align education with labor-market needs | National KPI is Saudi unemployment. The agent measures coverage of listed skills. |
| SDG 8 | 8.5 Decent work and employment | 8.5.2 unemployment by sex, age and disability status |
| SDG 8 | 8.6 Youth employment, education and training | 8.6.1 youth outside employment, education or training |
| SDG 4 | 4.4 Employment-relevant skills | 4.4.1 ICT skills by type |

See the [SDG alignment and ethics notes](docs/SDG_ALIGNMENT.md) for prototype metrics and their relationship to national indicators.

## Architecture

```mermaid
flowchart LR
  A["Typer CLI"] --> B["Claude planner or offline replay"]
  B --> C["Load catalog"]
  C --> D["Analyze coverage"]
  D --> E["Recommend actions"]
  E --> F["Prioritize and generate report"]
  F --> G["Validated bilingual JSON"]
```

See [architecture details](docs/ARCHITECTURE.md).

## Quickstart

Use Python 3.11 or later.

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install '.[dev]'
nitaqat-agent match --mock --skills 'Excel,SQL'
nitaqat-agent match --mock --lang ar --skills 'إكسل، إس كيو إل'
```

For live mode, copy `.env.example` to `.env` in the working directory and set `ANTHROPIC_API_KEY` locally. Set `ANTHROPIC_MODEL` if your account requires a different compatible model that supports forced tool use. Then run:

```sh
nitaqat-agent match --skills 'Excel,SQL'
```

Use comma-separated skill labels. The [sample catalog](data/sample/catalog.json) lists supported labels in both languages. Raw skills are processed locally. Live mode sends derived catalog evidence to Anthropic.

## Example

```sh
nitaqat-agent match --mock --skills 'Excel,SQL'
```

```json
{
  "language": "en",
  "data_source": "synthetic",
  "summary": "Career exploration using a synthetic catalog. Results do not represent vacancies.",
  "unrecognized_count": 0,
  "matches": [
    {
      "role": "Junior data analyst",
      "matched": [
        "Excel",
        "SQL"
      ],
      "missing": [
        "data visualization"
      ],
      "coverage": 0.6666666666666666
    },
    {
      "role": "Operations assistant",
      "matched": [
        "Excel"
      ],
      "missing": [
        "report writing"
      ],
      "coverage": 0.5
    }
  ],
  "recommendations": [
    {
      "action": "Review the Junior data analyst role and its requirements with a career counselor.",
      "sdg_target": "8.5",
      "confidence": "Illustrative match based on self-reported skills and a synthetic catalog."
    },
    {
      "action": "Create a chart and explain the trend it shows.",
      "sdg_target": "4.4",
      "confidence": "Illustrative practice for a skill gap in the synthetic catalog."
    }
  ]
}
```

## Verification

```sh
ruff check .
pytest
```

## Limitations and future work

The [synthetic catalog](data/README.md) contains illustrative roles and exercises. Skill coverage describes catalog overlap and has no predictive interpretation. Human reviewers verify placement, eligibility and localization requirements. A follow-on pilot could evaluate counselor-rated relevance, expand aliases and role coverage, and integrate a vacancy feed with documented reuse rights. Changes in unemployment or youth education and training outcomes require a separate evaluation.

## Author and citation

Dr. Muhammad Zulkifl Hasan, University of Central Punjab (UCP), Lahore. [ORCID 0000-0002-2733-5527](https://orcid.org/0000-0002-2733-5527)

```bibtex
@software{hasan2026nitaqat,
  author = {Hasan, Muhammad Zulkifl},
  title = {Vision 2030 SDG Agent: Bilingual Career Exploration under Nitaqat},
  year = {2026},
  version = {0.1.0}
}
```
