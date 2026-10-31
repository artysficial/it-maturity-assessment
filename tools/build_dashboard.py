"""Builds the IT maturity assessment report (site/index.html)."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import report_kit as rk  # noqa: E402
from assessment.scoring import level_name, load, overall, score  # noqa: E402


def main() -> None:
    responses, framework = load("responses.json"), load("framework.json")
    domains = score(responses, framework)
    levels = framework["levels"]
    current, target = overall(domains)
    ranked = sorted(domains, key=lambda d: -d.priority)
    initiatives = framework["initiatives"]
    quick_wins = [i for i in initiatives if i["horizon"] == "0-3 months"]

    body = rk.kpis([
        ("Overall maturity", f"{current:.1f} / 5", f"{level_name(current, levels)} · impact-weighted", "warn"),
        ("Target", f"{target:.1f} / 5", level_name(target, levels)),
        ("Largest priority gap", f"{ranked[0].current:.1f} → {ranked[0].target:.1f}", ranked[0].name, "bad"),
        ("Roadmap initiatives", len(initiatives), f"{len(quick_wins)} quick wins in 0-3 months"),
        ("Stakeholders", len(responses["stakeholders"]), f"{len(responses['questions'])} questions each"),
    ])
    body += rk.grid(
        rk.section("Current vs target maturity", rk.radar([d.name for d in domains], [
            ("Target", [d.target for d in domains], "var(--line)"),
            ("Current", [d.current for d in domains], "var(--blue)"),
        ])),
        rk.section("Priority = gap × business impact", rk.bars([(d.name, d.priority) for d in ranked if d.priority > 0]),
                   "Where improvement buys the most risk reduction."),
    )
    rows = [[d.name, framework["domains"][d.name]["cobit"], f"{d.current:.2f}", level_name(d.current, levels), f"{d.target:.1f}", f"{d.gap:.2f}",
             d.impact, f"{d.priority:.1f}", rk.pill(d.consensus)]
            for d in ranked]
    body += rk.section("Domain results", rk.table(["Domain", "COBIT 2019", "Current", "Level", "Target", "Gap", "Impact (1-5)", "Priority", "Consensus"], rows, {8}),
                       "Consensus shows how far stakeholders agree: weak consensus is a finding in itself and needs a workshop.")
    people = responses["stakeholders"]
    view_rows = [[d.name] + [f"{d.by_stakeholder[p]:.1f}" for p in people] for d in ranked]
    body += rk.section("How each stakeholder sees it", rk.table(["Domain"] + people, view_rows),
                       "Business leaders score higher than Internal Audit on almost every domain: the classic optimism gap the roadmap must close with evidence.")
    roadmap = ""
    for horizon in ("0-3 months", "3-12 months", "12-24 months"):
        items = [i for i in initiatives if i["horizon"] == horizon]
        rows = [[i["id"], f'<a href="{i["link"]}">{rk.esc(i["name"])}</a>' if i["link"] else rk.esc(i["name"]), rk.esc(", ".join(i["domains"])), rk.esc(i["effort"]), rk.esc(i["value"]), rk.esc(i["outcome"])] for i in items]
        roadmap += f"<h3 style='margin:18px 0 8px'>{rk.esc(horizon)}</h3>" + rk.table(["ID", "Initiative", "Domains", "Effort", "Value", "Outcome"], rows, {1, 2, 3, 4, 5})
    body += rk.section("Transformation roadmap", roadmap,
                       "Linked initiatives are delivered in the other projects of this case study; INIT-01 became the Payment Security Modernisation programme.")
    recommendations = [
        f"Start with {ranked[0].name.lower()}: it has the largest impact-weighted gap ({ranked[0].current:.1f} vs {ranked[0].target:.1f}). Enforce key-ceremony dual control now and fund the HSM Services API programme.",
        f"Automate access lifecycle and segregation-of-duties reviews; identity & access sits at {next(d for d in domains if d.name == 'Identity & access').current:.1f} with strong agreement that it is weak.",
        "Make security testing and requirement traceability release gates, so maturity claims are backed by evidence rather than self-assessment.",
        "Re-assess in twelve months with evidence-based scoring (control test results, audit findings) alongside interviews.",
    ]
    body += rk.section("Key recommendations", "<ol>" + "".join(f"<li style='margin-bottom:8px'>{rk.esc(r)}</li>" for r in recommendations) + "</ol>")
    checks = json.loads((ROOT / "reports" / "results.json").read_text(encoding="utf-8"))
    body += rk.section("Method checks", rk.table(["Check", "Area", "Result"], [[c["title"], c["category"], rk.pill(c["status"])] for c in checks["tests"]], {2}))

    weak = [d.name for d in domains if d.consensus == "Weak"]
    takeaways = [
        f"Arunika Bank's IT scores {current:.1f} out of 5 ({level_name(current, levels).lower()}) against a target of {target:.1f} ({level_name(target, levels).lower()}).",
        f"The biggest priority is {ranked[0].name.lower()}: it scores {ranked[0].current:.1f} against a target of {ranked[0].target:.1f} and carries high business impact.",
        f"The roadmap has {len(initiatives)} initiatives over 24 months, including {len(quick_wins)} quick wins that can start within three months.",
        (f"Stakeholders disagree most on {', '.join(n.lower() for n in weak)}; a short workshop should settle those scores before funding decisions."
         if weak else "Business leaders consistently score IT higher than Internal Audit does; the roadmap closes that gap with evidence."),
    ]
    rk.write(str(ROOT / "site" / "index.html"), rk.page(
        title="IT Maturity Assessment",
        eyebrow="Senior IT Consultant · Assessment & roadmap",
        summary="A COBIT-aligned maturity assessment of Arunika Bank's IT across eight domains, with stakeholder views, impact-weighted gaps and a 24-month transformation roadmap.",
        body=body, repo="it-maturity-assessment", verdict=(f"Maturity {current:.1f} of target {target:.1f}: start with {ranked[0].name.lower()}", "warn"), takeaways=takeaways,
    ))
    print(f"dashboard built: overall {current} vs {target}")


if __name__ == "__main__":
    main()
