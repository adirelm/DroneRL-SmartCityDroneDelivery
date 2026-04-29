"""Tests for config_loader module."""

import os
import tempfile

import pytest
import yaml

from dronerl.config_loader import Config, load_config

CONFIG_PATH = "config/config.yaml"


@pytest.fixture
def raw_config():
    return load_config(CONFIG_PATH)


@pytest.fixture
def config(raw_config):
    return Config(raw_config)


class TestLoadConfig:
    def test_load_returns_dict(self):
        data = load_config(CONFIG_PATH)
        assert isinstance(data, dict)

    def test_load_has_expected_keys(self):
        data = load_config(CONFIG_PATH)
        for key in ("environment", "agent", "rewards", "training", "wind"):
            assert key in data

    def test_load_missing_file_raises(self):
        with pytest.raises(FileNotFoundError):
            load_config("nonexistent.yaml")

    def test_load_custom_yaml(self):
        content = {"x": 1, "nested": {"y": 2}}
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            yaml.dump(content, f)
            path = f.name
        try:
            data = load_config(path)
            assert data == content
        finally:
            os.unlink(path)


class TestConfig:
    def test_dot_access_scalar(self, config):
        assert config.environment.grid_rows == 12

    def test_dot_access_nested(self, config):
        assert isinstance(config.environment, Config)
        assert config.agent.learning_rate == 0.1

    def test_dot_access_list(self, config):
        assert config.environment.start_position == (0, 0)

    def test_missing_key_raises(self, config):
        with pytest.raises(AttributeError):
            _ = config.nonexistent_key

    def test_nested_missing_key_raises(self, config):
        with pytest.raises(AttributeError):
            _ = config.environment.no_such_field

    def test_repr(self, config):
        r = repr(config)
        assert r.startswith("Config(")
        assert "environment" in r

    def test_to_dict_round_trip(self, raw_config):
        cfg = Config(raw_config)
        result = cfg.to_dict()
        assert result == raw_config

    def test_config_from_simple_dict(self):
        cfg = Config({"a": 1, "b": "hello"})
        assert cfg.a == 1
        assert cfg.b == "hello"

    def test_config_nested_to_dict(self):
        cfg = Config({"outer": {"inner": 42}})
        assert cfg.to_dict() == {"outer": {"inner": 42}}
