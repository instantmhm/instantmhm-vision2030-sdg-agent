# Saudi SME licensing and financing guide

[![Saudi Vision 2030](https://img.shields.io/badge/Saudi_Vision-2030-087b51)](https://www.vision2030.gov.sa/en/overview/pillars/a-thriving-economy)
[![SDG 8](https://img.shields.io/badge/SDG_8-Decent_Work-a21942)](https://sdgs.un.org/goals/goal8)
[![SDG 9](https://img.shields.io/badge/SDG_9-Industry_and_Innovation-f36d25)](https://sdgs.un.org/goals/goal9)

A bilingual agent that helps prospective founders and SME owners find the official starting points for registration, municipal licensing, and financing in Saudi Arabia. It produces a checklist with a source, an SDG tag, and a confidence note for each action. [Problem selection](docs/PROBLEM_SELECTION.md) · [SDG alignment and ethics](docs/SDG_ALIGNMENT.md)

| Framework | Alignment | Measure |
|---|---|---|
| Vision 2030 | Thriving Economy and Financial Sector Development | SME contribution to GDP is a national KPI |
| SDG 8.3 | Formalization and growth of MSMEs | 8.3.1 informal employment by sector and sex |
| SDG 9.3 | Small-scale enterprises' access to finance | 9.3.2 small-scale industries with a loan or line of credit |

## Architecture

```mermaid
flowchart LR
  CLI --> Planner["Claude or offline replay"]
  Planner --> Catalog["Load catalog"]
  Catalog --> Routes["Select routes"]
  Routes --> Actions["Build checklist"]
  Actions --> JSON["Generate validated JSON"]
```

See [architecture and tool contracts](docs/ARCHITECTURE.md).

## Run locally

Use Python 3.11 or later.

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install '.[dev]'
sme-agent guide --mock --goal both
sme-agent guide --mock --goal التمويل --lang ar
```

For live mode, copy `.env.example` to `.env` and set `ANTHROPIC_API_KEY` locally. Then run `sme-agent guide --goal financing`. Set `ANTHROPIC_MODEL` if your account requires a different model that supports forced tool use.

## Example

```sh
sme-agent guide --mock --goal financing
```

```json
{
  "language": "en",
  "goal": "financing",
  "source": "curated_official_references",
  "summary": "Navigation checklist. Verify current requirements with the relevant authority.",
  "recommendations": [
    {
      "id": "financing-gate",
      "action": "Review Tamweel Gate to learn how SMEs submit requests to participating financiers.",
      "sdg_target": "9.3",
      "confidence": "Official channel description. Confirm available offers and terms with the financier.",
      "source_url": "https://www.kafalah.gov.sa/en/Help/Pages/TamweelGate.aspx"
    },
    {
      "id": "kafalah",
      "action": "Ask a participating financier about Kafalah. The program can provide a guarantee to the financier, which handles the financing request.",
      "sdg_target": "9.3",
      "confidence": "Official guarantee-program description. The financier and program assess requests independently.",
      "source_url": "https://www.kafalah.gov.sa/en/Help/FAQ/Pages/Does-the-program-grant-financing-to-SMEs.aspx"
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

The curated catalog covers a small number of public entry points. The licensing authority confirms current activity, location, and documentation requirements. Financiers and Kafalah make financing and guarantee decisions. Future work includes review with SME advisers, broader sector-specific coverage, and periodic checks for source changes. The prototype measures source coverage and routing accuracy. Population-level indicators require separate evidence. [Catalog provenance](data/README.md)

## Author and citation

Dr. Muhammad Zulkifl Hasan, University of Central Punjab (UCP), Lahore. [ORCID 0000-0002-2733-5527](https://orcid.org/0000-0002-2733-5527)

```bibtex
@software{hasan2026saudisme,
  author = {Hasan, Muhammad Zulkifl},
  title = {Vision 2030 SDG Agent: Saudi SME Licensing and Financing Navigation},
  year = {2026},
  version = {0.1.0}
}
```
