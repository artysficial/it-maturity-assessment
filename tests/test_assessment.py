"""Scoring logic and the completeness of the assessment and roadmap."""

import pytest

from assessment.scoring import DomainScore, level_name, overall, score


@pytest.mark.category("Scoring logic")
@pytest.mark.severity("critical")
def test_domain_score_is_the_mean_of_all_answers():
    """A domain's maturity is the mean of every stakeholder's answer to its questions"""
    responses = {"stakeholders": ["A", "B"], "questions": [
        {"domain": "D", "scores": {"A": 2, "B": 4}}, {"domain": "D", "scores": {"A": 3, "B": 3}}]}
    [d] = score(responses, {"domains": {"D": {"target": 4.0, "impact": 2}}})
    assert d.current == 3.0 and d.by_stakeholder == {"A": 2.5, "B": 3.5}


@pytest.mark.category("Scoring logic")
@pytest.mark.severity("high")
@pytest.mark.parametrize("current, target, impact, gap, priority", [(2.0, 4.0, 5, 2.0, 10.0), (3.5, 3.5, 3, 0.0, 0.0), (4.2, 4.0, 4, 0.0, 0.0)])
def test_gap_and_priority(current, target, impact, gap, priority):
    """Gap is target minus current (never negative); priority weights the gap by business impact"""
    d = DomainScore("D", current, target, impact, 0.5, {})
    assert d.gap == gap and d.priority == priority


@pytest.mark.category("Scoring logic")
@pytest.mark.severity("medium")
@pytest.mark.parametrize("spread, consensus", [(0.3, "Strong"), (0.8, "Moderate"), (1.2, "Weak")])
def test_consensus_from_spread(spread, consensus):
    """Stakeholder disagreement (standard deviation) is reported as consensus"""
    assert DomainScore("D", 3, 4, 1, spread, {}).consensus == consensus


@pytest.mark.category("Scoring logic")
@pytest.mark.severity("medium")
def test_overall_maturity_is_impact_weighted():
    """Overall maturity weights each domain by its business impact"""
    domains = [DomainScore("A", 2.0, 4.0, 3, 0, {}), DomainScore("B", 4.0, 4.0, 1, 0, {})]
    assert overall(domains) == (2.5, 4.0)


@pytest.mark.category("Scoring logic")
@pytest.mark.severity("low")
@pytest.mark.parametrize("value, name", [(0.2, "Non-existent"), (1.6, "Managed"), (3.49, "Defined"), (5, "Optimising")])
def test_level_names(framework, value, name):
    """Scores map to the CMMI-style level names"""
    assert level_name(value, framework["levels"]) == name


@pytest.mark.category("Assessment completeness")
@pytest.mark.severity("critical")
def test_every_stakeholder_answered_every_question(responses):
    """No missing answers: every stakeholder scored every question"""
    for q in responses["questions"]:
        assert set(q["scores"]) == set(responses["stakeholders"]), q["id"]


@pytest.mark.category("Assessment completeness")
@pytest.mark.severity("high")
def test_scores_are_on_the_zero_to_five_scale(responses):
    """All answers are whole numbers from 0 to 5"""
    assert all(isinstance(s, int) and 0 <= s <= 5 for q in responses["questions"] for s in q["scores"].values())


@pytest.mark.category("Assessment completeness")
@pytest.mark.severity("high")
def test_every_domain_has_at_least_three_questions(responses, framework):
    """Each domain is measured by three or more questions"""
    for domain in framework["domains"]:
        assert sum(1 for q in responses["questions"] if q["domain"] == domain) >= 3


@pytest.mark.category("Roadmap")
@pytest.mark.severity("critical")
def test_every_significant_gap_has_an_initiative(scores, framework):
    """Every domain with a gap of 0.5 or more is addressed by at least one roadmap initiative"""
    addressed = {d for i in framework["initiatives"] for d in i["domains"]}
    for d in scores:
        if d.gap >= 0.5:
            assert d.name in addressed, d.name


@pytest.mark.category("Roadmap")
@pytest.mark.severity("medium")
def test_initiatives_reference_known_domains_and_horizons(framework):
    """Initiatives use known domains and one of the three horizons"""
    for i in framework["initiatives"]:
        assert set(i["domains"]) <= set(framework["domains"])
        assert i["horizon"] in ("0-3 months", "3-12 months", "12-24 months")


@pytest.mark.category("Roadmap")
@pytest.mark.severity("medium")
def test_highest_priority_domain_gets_a_quick_win(scores, framework):
    """The top-priority domain has at least one initiative in the first three months"""
    top = max(scores, key=lambda d: d.priority).name
    assert any(top in i["domains"] and i["horizon"] == "0-3 months" for i in framework["initiatives"])
