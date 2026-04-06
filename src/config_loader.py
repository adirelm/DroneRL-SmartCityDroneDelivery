"""Configuration loader for DroneRL project."""

import yaml


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


def load_config(path: str = "config/config.yaml") -> dict:
    """Load YAML config file and return as a dictionary."""
    with open(path) as f:
        data = yaml.safe_load(f)
    return data
