"""Tests for config_loader module."""

import os
import tempfile
import warnings

import pytest
import yaml

from dronerl import __version__ as _project_version
from dronerl.config_loader import Config, _major_minor, _validate_version, load_config

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


class TestVersionValidation:
    """§8.1 — application validates config-version compatibility at startup."""

    def test_major_minor_extracts_first_two_components(self):
        assert _major_minor("1.1.1") == (1, 1)
        assert _major_minor("2.0") == (2, 0)
        assert _major_minor("3") == (3, 0)

    def test_load_with_matching_version_no_warning(self):
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            data = load_config(CONFIG_PATH)
            assert data["version"] == _project_version

    def test_validate_version_warns_on_major_minor_mismatch(self):
        # Project is 1.1.x; "2.0.0" differs on major/minor → warn.
        with pytest.warns(UserWarning, match="differs from project"):
            _validate_version("2.0.0")

    def test_validate_version_no_warn_on_patch_only_mismatch(self):
        # Project is 1.1.1; "1.1.0" differs on patch only → tolerated.
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            _validate_version(f"{_major_minor(_project_version)[0]}."
                              f"{_major_minor(_project_version)[1]}.999")

    def test_validate_version_warns_when_missing(self):
        with pytest.warns(UserWarning, match="no 'version' key"):
            _validate_version("")

    def test_load_config_without_version_warns(self):
        # Build a temporary config file with no 'version' key.
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            yaml.dump({"environment": {"grid_rows": 3, "grid_cols": 3}}, f)
            path = f.name
        try:
            with pytest.warns(UserWarning, match="no 'version' key"):
                load_config(path)
        finally:
            os.unlink(path)
