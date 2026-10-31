# IT Maturity Assessment

[![Tests and dashboard](https://github.com/artysficial/it-maturity-assessment/actions/workflows/tests.yml/badge.svg)](https://github.com/artysficial/it-maturity-assessment/actions/workflows/tests.yml)
[![Dashboard](https://img.shields.io/badge/dashboard-live-0071e3)](https://artysficial.github.io/it-maturity-assessment/)

The Senior IT Consultant lens on the fictional **Arunika Bank**: a COBIT 2019-aligned maturity assessment that
explains *why* the payment-security programme exists and what else must change around it.

**[View the assessment report →](https://artysficial.github.io/it-maturity-assessment/)**

## Method

1. **Eight domains**, each mapped to COBIT 2019 objectives: governance, risk & compliance, security operations,
   key management, identity & access, architecture & integration, delivery & quality, vendor management.
2. **Five stakeholders** (CIO, CISO, Head of Payments Technology, Head of IT Operations, Head of Internal Audit)
   score three statements per domain on a 0-5 CMMI-style scale (`data/responses.json`).
3. **Scoring** (`assessment/scoring.py`): domain maturity = mean of all answers; gap = target − current;
   **priority = gap × business impact**; consensus from the spread of answers; overall maturity impact-weighted.
4. **Roadmap** (`data/framework.json`): initiatives over 0-3, 3-12 and 12-24 months, each tied to the domains
   it improves. Linked initiatives are delivered by the other projects in this case study.

## Findings in one line

Overall maturity **2.8 of a 3.9 target**. Key management (2.0) is the largest impact-weighted gap, which is why
INIT-01 became the **Payment Security Modernisation** programme; business leaders consistently score higher than
Internal Audit, so the roadmap insists on evidence-based re-assessment.

## Tests

Scoring logic (mean, gap floor at zero, impact weighting, consensus bands, level names), completeness (every
stakeholder answered every question, valid scale, three questions per domain) and roadmap rules (every gap ≥ 0.5
has an initiative; the top-priority domain gets a quick win).

```bash
pip install -r requirements.txt
python -m pytest && python tools/build_dashboard.py
```

Built by [Rahmadani Tyas Ningrum](https://artysficial.github.io/) · MIT licence
