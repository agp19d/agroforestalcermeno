"""Scenario persistence — save, load, list, and delete named scenarios.

Scenarios are stored as a single JSON file alongside the application.
Each scenario is a flat dictionary of input values keyed exactly as
they appear in :pymod:`config.DEFAULT_INPUTS` (with the ``in_`` prefix
added by Streamlit session state).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from config import SCENARIOS_FILENAME

# Resolve the storage path relative to this file's directory.
_SCENARIOS_PATH: Path = Path(__file__).resolve().parent / SCENARIOS_FILENAME


def load_all() -> dict[str, dict[str, Any]]:
    """Load every saved scenario from disk.

    Returns:
        A mapping of *scenario name* → *input dictionary*.  Returns an
        empty dict when the file does not yet exist.
    """
    if _SCENARIOS_PATH.exists():
        return json.loads(_SCENARIOS_PATH.read_text(encoding="utf-8"))
    return {}


def save_all(scenarios: dict[str, dict[str, Any]]) -> None:
    """Overwrite the scenarios file with *scenarios*.

    Args:
        scenarios: Complete mapping of scenario names to input dicts.
    """
    _SCENARIOS_PATH.write_text(
        json.dumps(scenarios, indent=2),
        encoding="utf-8",
    )


def save_one(name: str, inputs: dict[str, Any]) -> None:
    """Create or update a single scenario by *name*.

    Args:
        name: Human-readable scenario label.
        inputs: Flat dictionary of input values to persist.
    """
    all_scenarios = load_all()
    all_scenarios[name] = inputs
    save_all(all_scenarios)


def delete_one(name: str) -> bool:
    """Delete the scenario identified by *name*.

    Args:
        name: The scenario label to remove.

    Returns:
        ``True`` if the scenario existed and was deleted; ``False``
        otherwise.
    """
    all_scenarios = load_all()
    if name in all_scenarios:
        del all_scenarios[name]
        save_all(all_scenarios)
        return True
    return False


def list_names() -> list[str]:
    """Return the names of all saved scenarios in insertion order."""
    return list(load_all().keys())
