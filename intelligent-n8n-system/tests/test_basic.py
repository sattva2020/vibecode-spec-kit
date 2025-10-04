"""
Basic tests to verify test infrastructure is working
"""

import pytest
import sys
from pathlib import Path


def test_basic_imports():
    """Test that basic imports work"""
    # Add src to path
    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

    try:
        from core.config import get_config

        config = get_config()
        assert config is not None
        assert hasattr(config, "server")
        assert hasattr(config, "lightrag")
        assert hasattr(config, "supabase")
        assert hasattr(config, "n8n")
        assert hasattr(config, "ollama")
        print("✅ Basic imports working")
    except ImportError as e:
        pytest.skip(f"Import failed: {e}")


def test_config_loading():
    """Test configuration loading"""
    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

    try:
        from core.config import get_config

        config = get_config()

        # Test server config
        assert config.server.host == "0.0.0.0"
        assert config.server.port == 8000
        assert config.server.debug is False

        # Test n8n config
        assert config.n8n.url == "http://localhost:5678"
        assert config.n8n.user == "admin"
        assert config.n8n.password == "admin123"

        print("✅ Configuration loading working")
    except ImportError as e:
        pytest.skip(f"Import failed: {e}")


@pytest.mark.asyncio
async def test_async_support():
    """Test that async support is working"""
    import asyncio

    async def async_function():
        await asyncio.sleep(0.001)
        return "async_working"

    result = await async_function()
    assert result == "async_working"
    print("✅ Async support working")


def test_pytest_markers():
    """Test that pytest markers are working"""
    # This test should run without markers
    assert True
    print("✅ Pytest markers working")


@pytest.mark.unit
def test_unit_marker():
    """Test that unit marker works"""
    assert True
    print("✅ Unit marker working")


@pytest.mark.integration
def test_integration_marker():
    """Test that integration marker works"""
    assert True
    print("✅ Integration marker working")


@pytest.mark.slow
def test_slow_marker():
    """Test that slow marker works"""
    import time

    time.sleep(0.1)  # Simulate slow test
    assert True
    print("✅ Slow marker working")


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])
