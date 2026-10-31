import pytest

from assessment.scoring import load, score

pytest_plugins = ["results_plugin"]


@pytest.fixture(scope="session")
def responses():
    return load("responses.json")


@pytest.fixture(scope="session")
def framework():
    return load("framework.json")


@pytest.fixture(scope="session")
def scores(responses, framework):
    return score(responses, framework)
