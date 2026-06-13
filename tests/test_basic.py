# tests/test_basic.py
"""
Basic tests for MadiLang core functionality.
These tests ensure the package is importable and core components initialize correctly.
"""

import pytest


def test_package_import():
    """Test that madilang package can be imported."""
    import madilang
    assert madilang is not None


def test_version_defined():
    """Test that version is defined and valid."""
    import madilang
    assert hasattr(madilang, "__version__")
    assert isinstance(madilang.__version__, str)
    assert len(madilang.__version__) > 0


def test_author_defined():
    """Test that author metadata is defined."""
    import madilang
    assert hasattr(madilang, "__author__")
    assert "El Madani" in madilang.__author__


def test_cli_entry_point():
    """Test that CLI main function is accessible."""
    from madilang.cli.main import main
    assert callable(main)


def test_parser_initialization():
    """Test that parser can be initialized."""
    from madilang.compiler.parser import MadiParser
    parser = MadiParser("")
    assert parser is not None


def test_ir_program_creation():
    """Test that IR program can be created."""
    from madilang.ir.models import IRProgram
    ir = IRProgram()
    assert ir is not None
    assert ir.entities == {}
    assert ir.intents == {}


def test_signature_engine_creation():
    """Test that signature engine can be initialized."""
    from madilang.ir.intent_signature import IntentSignatureEngine
    engine = IntentSignatureEngine()
    assert engine is not None


def test_generator_registry():
    """Test that generator registry works."""
    from madilang.generators.base import GeneratorRegistry
    registry = GeneratorRegistry.list_generators()
    assert isinstance(registry, list)
    # NodeJS generator should be registered
    assert "nodejs" in registry
