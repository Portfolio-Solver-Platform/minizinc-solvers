#!/usr/bin/env bash
pip-compile --upgrade pyproject.toml -o requirements.txt --strip-extras
pip-compile --upgrade pyproject.toml --extra dev -o requirements-dev.txt --strip-extras
