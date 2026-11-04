"""Rez package definition for nuclear."""

import subprocess

name = "nuclear"
version = subprocess.check_output(["rezops-get-version"]).decode().strip()
description = "A package that has a mix of nuke related tooling to general 2d pipeline."
requires = []
private_build_requires = []
build_command = f"rezops-build {name}"


def commands():
    """Expose the generated package and optional Nuke tools in Rez."""
    env.PYTHONPATH.append("{root}/python")  # noqa: F821 -- Rez injects ``env`` at runtime.
    env.NUKE_PATH.append("{root}/nuke")  # noqa: F821 -- Rez injects ``env`` at runtime.
