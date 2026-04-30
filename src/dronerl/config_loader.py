"""Configuration loader for DroneRL project."""

import warnings

import yaml

from dronerl import __version__ as _project_version


class Config:
    """Provides dot-access to nested config values."""

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


def load_config(path: str = "config/config.yaml") -> dict:
    """Load YAML config file, validate its version + schema, and return as a dict."""
    with open(path) as f:
        data = yaml.safe_load(f)
    _validate_schema(data, path)
    _validate_version(data.get("version", ""))
    return data
