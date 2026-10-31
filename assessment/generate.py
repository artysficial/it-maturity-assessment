"""Generates data/responses.json: five stakeholders answer 24 maturity questions (0-5).
Seeded around each domain's observed level, so the result is reproducible."""

from __future__ import annotations

import json
import random
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data"
STAKEHOLDERS = ["CIO", "CISO", "Head of Payments Technology", "Head of IT Operations", "Head of Internal Audit"]

# domain -> (observed level, questions)
DOMAINS = {
    "Governance": (3.2, ["IT strategy is aligned to the business plan and reviewed yearly",
                         "An IT steering committee prioritises investment with clear criteria",
                         "IT performance is reported to the board with agreed KPIs"]),
    "Risk & compliance": (2.8, ["IT risks are recorded, owned and reviewed quarterly",
                                "Regulatory requirements (PCI, OJK) are mapped to controls",
                                "Control testing results feed back into the risk register"]),
    "Security operations": (2.6, ["Security events are monitored 24x7 with defined response times",
                                  "Vulnerabilities are remediated within policy timelines",
                                  "Security testing is part of every release"]),
    "Key management": (1.8, ["Cryptographic keys are inventoried with owners and usage",
                             "Key ceremonies follow dual control and split knowledge",
                             "Applications reach HSMs through a controlled, audited interface"]),
    "Identity & access": (2.4, ["Joiners, movers and leavers are automated from HR data",
                                "Access is reviewed periodically with segregation-of-duties rules",
                                "Privileged access is vaulted and session-recorded"]),
    "Architecture & integration": (2.9, ["Integration follows API standards with versioning and security",
                                         "Architecture decisions are recorded and reviewed",
                                         "Technical debt is tracked and funded"]),
    "Delivery & quality": (3.3, ["Requirements are traceable to tests and evidence",
                                 "Test automation covers regression for critical systems",
                                 "Releases have defined quality gates and readiness reports"]),
    "Vendor management": (3.0, ["Purchases follow procure-to-pay controls with approval limits",
                                "Critical vendors are assessed for risk and performance",
                                "Contracts define service levels and exit plans"]),
}


def main() -> None:
    rng = random.Random(2019)
    questions = []
    for domain, (level, items) in DOMAINS.items():
        for n, text in enumerate(items, 1):
            scores = {}
            for person in STAKEHOLDERS:
                bias = 0.5 if person in ("CIO", "Head of Payments Technology") else -0.4 if person == "Head of Internal Audit" else 0.0
                scores[person] = max(0, min(5, round(rng.gauss(level + bias, 0.6))))
            questions.append({"id": f"{domain[:3].upper()}-{n}", "domain": domain, "question": text, "scores": scores})
    DATA.mkdir(exist_ok=True)
    (DATA / "responses.json").write_text(json.dumps({"stakeholders": STAKEHOLDERS, "questions": questions}, indent=2), encoding="utf-8")
    print(f"wrote {len(questions)} questions x {len(STAKEHOLDERS)} stakeholders")


if __name__ == "__main__":
    main()
