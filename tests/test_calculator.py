import pytest
from app.agents.analyst_agent import safe_calculate

def test_safe_calculate():
    assert safe_calculate("(92 + 95 + 89) / 3") == 92

def test_rejects_python_execution():
    with pytest.raises(ValueError):
        safe_calculate("__import__('os').system('whoami')")
