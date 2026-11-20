# SDG alignment

**Primary — SDG 8, Decent Work and Economic Growth.** Target 8.5 covers full and productive employment and decent work, including for women and young people. Indicator 8.5.2 is unemployment by sex, age and disability status. Target 8.6 concerns youth outside employment, education or training. Indicator 8.6.1 measures that share among people aged 15–24. [UN Goal 8](https://sdgs.un.org/goals/goal8) · [UN indicator metadata](https://unstats.un.org/sdgs/metadata/?Goal=8&Target=)

**Secondary — SDG 4, Quality Education.** Target 4.4 concerns relevant skills for employment, decent jobs and entrepreneurship. Indicator 4.4.1 measures youth and adults with ICT skills, by type of skill. The ICT subset of this prototype is relevant to the target, and formal indicator measurement would require survey-compatible evidence. [UN Goal 4](https://sdgs.un.org/goals/goal4)

| Agent capability | Vision 2030 objective | SDG target | Prototype or pilot metric |
|---|---|---|---|
| Match self-reported skills to example roles | Align education with labor-market needs | 8.5 | Matched required skills divided by listed required skills |
| Give job seekers and counselors next steps to review | Strengthen pathways into employment | 8.6 | Share of pilot sessions where a counselor confirms a feasible next step |
| Suggest practice for documented skill gaps | Support lifelong learning | 4.4 | Identified gaps with an available practice suggestion divided by total identified gaps |

The official indicators require population data. The metrics above evaluate the prototype and its outputs. Indicator 8.6.1 requires a representative youth denominator and education and training status as well as employment status.

## Risks and ethics

- **Privacy and Saudi PDPL** — Work with skill labels only. The CLI maps known aliases locally and sends only catalog-derived fields to Claude. Use offline mode for local processing. Before a deployment with identifiable profiles, review lawful basis, retention, access controls and any international transfer requirements with the responsible data controller. [SDAIA PDPL guide](https://dgp.sdaia.gov.sa/wps/wcm/connect/f579bc32-fda8-47bd-bc6f-66b8cb77985c/ENG-Guide%2Bto%2Bthe%2Bsaudi%2BPDP%2Blaw%2Bfor%2Bcontrollers%2Bprocessors.pdf?MOD=AJPERES)
- **Bias** — Rankings use only explicitly entered skills and the same sorting rules for everyone. Small catalogs and uneven alias coverage can still disadvantage users. Review role coverage and counselor-rated relevance across user groups in a properly consented pilot.
- **Arabic fairness** — Normalize Arabic diacritics, common alef variants and spacing. Test equivalent Arabic and English skill sets and measure differences in recognition of regional terms before rollout.
- **Human decisions** — Counselors and users verify skills, requirements and training fit. The agent never makes hiring, rejection, pay, eligibility, placement or Nitaqat compliance decisions. It does not infer age, sex or nationality.
