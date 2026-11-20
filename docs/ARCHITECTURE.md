# Architecture

```mermaid
flowchart TD
  A["CLI: goal in Arabic or English"] --> P["Planner: Claude or offline replay"]
  P --> C["Load source catalog"]
  C --> R["Select licensing and financing routes"]
  R --> K["Build bilingual checklist"]
  K --> J["Prioritize and render validated JSON"]
  C -. tool result .-> P
  R -. tool result .-> P
  K -. tool result .-> P
```

The planner executes four bounded tool calls. Local code controls the sources, translated text and SDG tags. Claude receives the selected goal, locale, and curated tool results and can select a first item from the checklist. The offline replay sends canned tool calls through the same dispatcher and preserves catalog order. The output is validated by Pydantic. Neither mode needs applicant records.
