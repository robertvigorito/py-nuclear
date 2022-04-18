"""Tests for `nuclear` package."""
import os
import pytest
import requests
import subprocess
import unittest

# Wgid Imports
from wgid import nuclear


def latest_from_github():
    """Find the latest release version from github

    Notes:
        For unauthenticated requests, the rate limit allows for up to 60
        requests per hour. Unauthenticated requests are associated with the
        originating IP address, and not the user making requests.

    Returns:
        (str) Latest version from github repo
    """
    response = requests.get("https://api.github.com/repos/robertvigorito/py-nuclear/releases/latest")
    try:
        latest_release = response.json()["tag_name"].replace("v", "")
    except KeyError:
        latest_release = ""
    return latest_release


def test_version():
    """
    Version test, check pyproject.toml and python package version matches, then
    compare version is greater than latest release.
    """
    import toml
    pyproject = os.path.join(os.path.dirname(os.path.dirname(__file__)), "pyproject.toml")
    latest_release = latest_from_github()

    with open(pyproject, "r") as pyproject_file:
        pyproject_data = toml.load(pyproject_file)
        toml_version = pyproject_data["project"]["version"]

    # Compare the pyproject and python module version, than current compare with the release version
    assert toml_version == nuclear.__version__, "pyproject.toml and nuclear.__version__ don't match"
    assert latest_release < toml_version, "Please increment the package version, v{latest_release} release exists!".format(**locals())


def test_response():
    """Simple response test.
    """
    url = "https://github.com/robertvigorito/alfred"
    response = requests.get(url)
    assert response.status_code == 200, "{url} doesnt exist return code {status}".format(url=url, status=response.status_code)


