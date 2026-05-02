"""Configuration loader for DroneRL project."""

import warnings
from pathlib import Path

import yaml

from dronerl import __version__ as _project_version


class Config:
    """Recursive dot-access wrapper around the parsed YAML config (the project's most-reused building block).

    Input:  ``data: dict`` — the parsed `config/config.yaml` shape, with any
            nesting depth. Numeric lists (e.g. ``start_position: [1, 1]``) are
            coerced to tuples so they're hashable and immutable; mixed-type
            lists are preserved as ``list``.
    Output: instance attributes for every top-level key, with nested dicts
            wrapped recursively into more ``Config`` instances. ``to_dict()``
            round-trips back to a plain dict (tuples → lists).
    Setup:  no constructor parameters beyond ``data``. Schema and version
            validation live in :func:`load_config` (the ingest path that
            calls ``_validate_schema`` and ``_validate_version``); a Config
            built directly from a literal dict bypasses both — this is
            intentional so tests can construct minimal configs without the
            full YAML schema.
    """

    def __init__(self, data: dict):
        for key, value in data.items():
            if isinstance(value, dict):
                setattr(self, key, Config(value))
            elif isinstance(value, list):
                setattr(self, key, tuple(value) if all(isinstance(i, (int, float)) for i in value) else value)
            else:
                setattr(self, key, value)

    def __repr__(self):
        attrs = ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items())
        return f"Config({attrs})"

    def to_dict(self) -> dict:
        """Convert back to a plain dictionary (tuples restored to lists)."""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, Config):
                result[key] = value.to_dict()
            elif isinstance(value, tuple):
                result[key] = list(value)
            else:
                result[key] = value
        return result


def _major_minor(version: str) -> tuple[int, int]:
    """Return ``(major, minor)`` from a ``"major.minor.patch"`` string."""
    major, minor, *_ = version.split(".") + ["0", "0"]
    return int(major), int(minor)


def _validate_version(config_version: str) -> None:
    """Validate that the config file's version is compatible with the project.

    Per the course-wide submission guidelines (§8.1), the application
    must validate config-version compatibility at startup. Mismatch on
    *patch* level is tolerated silently (config files don't need to bump
    on every patch release); mismatch on *major* or *minor* triggers a
    ``UserWarning`` so a stale config doesn't silently produce wrong
    results.
    """
    if not config_version:
        warnings.warn(
            f"config has no 'version' key; expected {_project_version}",
            UserWarning,
            stacklevel=3,
        )
        return
    cfg_mm = _major_minor(config_version)
    proj_mm = _major_minor(_project_version)
    if cfg_mm != proj_mm:
        warnings.warn(
            f"config version {config_version!r} differs from project "
            f"version {_project_version!r} on major/minor level — config "
            "may be stale",
            UserWarning,
            stacklevel=3,
        )


_REQUIRED_TOP_LEVEL = (
    "version", "environment", "rewards", "agent", "training",
    "wind", "algorithm", "q_learning", "double_q",
    "dynamic_board", "gui", "colors", "logging", "comparison", "paths",
)


def _validate_schema(data: dict, path: str) -> None:
    """Warn clearly if a required top-level block is absent.

    Mirrors :func:`_validate_version` — a soft warning rather than a hard
    raise so synthetic test configs (and partial / WIP configs) still load,
    but the user sees an actionable message at startup rather than an
    opaque ``AttributeError`` later when the SDK reaches into a missing
    sub-block.
    """
    missing = [k for k in _REQUIRED_TOP_LEVEL if k not in data]
    if missing:
        warnings.warn(
            f"config at {path!r} is missing required top-level keys: {missing}. "
            "The SDK will raise AttributeError when it reaches into any of "
            "these. Restore from config/config.yaml in the repo if unsure.",
            UserWarning,
            stacklevel=3,
        )


_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_CONFIG_PATH = str(_PROJECT_ROOT / "config" / "config.yaml")  # §14.3 — anchor to the package, not CWD


def package_relative(path: str) -> str:
    """Resolve ``path`` against the project root if it's relative; pass-through if absolute (§14.3 / Pass-5 F14.5)."""
    p = Path(path)
    return str(p if p.is_absolute() else _PROJECT_ROOT / p)


def load_config(path: str = _DEFAULT_CONFIG_PATH) -> dict:
    """Load YAML config, validate version + schema, return as a dict.

    Fault tolerance (§13 Reliability): malformed YAML and empty files raise
    ``RuntimeError`` with a clear actionable message instead of bubbling
    ``yaml.YAMLError`` or ``AttributeError`` from a downstream caller.
    """
    try:
        with open(path) as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as exc:
        raise RuntimeError(
            f"config at {path!r} is not valid YAML: {exc}. "
            "Restore from config/config.yaml in the repo if unsure."
        ) from exc
    if not isinstance(data, dict):
        raise RuntimeError(
            f"config at {path!r} parsed to {type(data).__name__}, expected dict. "
            "File may be empty or malformed."
        )
    _validate_schema(data, path)
    _validate_version(data.get("version", ""))
    return data
