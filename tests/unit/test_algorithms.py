"""Tests for the algorithm registry.

The registry in ``src/algorithms.py`` is the single source of truth for
the project's "list of algorithms." These tests guard the invariants
every consumer relies on (factory, GUI, comparison runner, charts,
analysis scripts, parametrised agent tests).
"""

from dataclasses import FrozenInstanceError

import pytest

from dronerl.algorithms import (
    AGENT_CLASSES,
    ALGORITHM_COLORS,
    ALGORITHM_LABELS,
    ALGORITHM_REGISTRY,
    ALGORITHMS,
    AlgorithmSpec,
)
from dronerl.base_agent import BaseAgent


class TestAlgorithmSpec:
    def test_is_frozen(self):
        spec = ALGORITHM_REGISTRY[0]
        with pytest.raises(FrozenInstanceError):
            spec.name = "mutated"  # type: ignore[misc]

    def test_has_expected_fields(self):
        spec = ALGORITHM_REGISTRY[0]
        assert isinstance(spec.name, str)
        assert isinstance(spec.label, str)
        assert isinstance(spec.color, str)
        assert issubclass(spec.agent_class, BaseAgent)


class TestRegistryShape:
    def test_registry_is_tuple(self):
        assert isinstance(ALGORITHM_REGISTRY, tuple)

    def test_registry_is_non_empty(self):
        assert len(ALGORITHM_REGISTRY) >= 3

    def test_every_entry_is_algorithm_spec(self):
        assert all(isinstance(spec, AlgorithmSpec) for spec in ALGORITHM_REGISTRY)


class TestDerivedStructures:
    def test_algorithms_matches_registry_names(self):
        assert tuple(spec.name for spec in ALGORITHM_REGISTRY) == ALGORITHMS

    def test_labels_match_registry(self):
        assert {s.name: s.label for s in ALGORITHM_REGISTRY} == ALGORITHM_LABELS

    def test_colors_match_registry(self):
        assert {s.name: s.color for s in ALGORITHM_REGISTRY} == ALGORITHM_COLORS

    def test_agent_classes_match_registry(self):
        assert {s.name: s.agent_class for s in ALGORITHM_REGISTRY} == AGENT_CLASSES

    def test_derived_dicts_have_same_keys(self):
        keys = set(ALGORITHM_LABELS)
        assert keys == set(ALGORITHM_COLORS)
        assert keys == set(AGENT_CLASSES)
        assert keys == set(ALGORITHMS)


class TestNameDiscipline:
    def test_names_are_unique(self):
        names = [spec.name for spec in ALGORITHM_REGISTRY]
        assert len(names) == len(set(names))

    def test_names_are_valid_identifiers(self):
        for name in ALGORITHMS:
            assert name.isidentifier(), f"{name!r} is not a valid Python identifier"

    def test_names_are_lowercase(self):
        for name in ALGORITHMS:
            assert name == name.lower(), f"{name!r} is not lowercase"


class TestAgentClassDiscipline:
    def test_all_agent_classes_subclass_base_agent(self):
        for spec in ALGORITHM_REGISTRY:
            assert issubclass(spec.agent_class, BaseAgent)

    def test_agent_classes_are_unique(self):
        classes = [spec.agent_class for spec in ALGORITHM_REGISTRY]
        assert len(classes) == len(set(classes))


class TestColorDiscipline:
    def test_colors_are_hex_strings(self):
        for color in ALGORITHM_COLORS.values():
            assert color.startswith("#") and len(color) == 7
            assert all(c in "0123456789abcdefABCDEF" for c in color[1:])

    def test_colors_are_unique(self):
        colors = list(ALGORITHM_COLORS.values())
        assert len(colors) == len(set(colors))
