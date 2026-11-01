"""Regression tests for the ethics layer.

These exist because the ethics hook was, for three months, dead code:
it did not parse, nothing imported it, and `madi check` never called it.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from madilang.compiler.parser import parse_madi          # noqa: E402
from madilang.compiler.analyzer import analyze_madi      # noqa: E402
from madilang.plugins.ethics_hook import evaluate_ethics  # noqa: E402


def _report(source: str):
    return evaluate_ethics(analyze_madi(parse_madi(source)))


GOOD = """
entity: User
fields:
  - name: string
  - email: string (unique)
  - password: string (secure)
  - createdAt: datetime (auto)

intent: register_user
route: "/api/signup"
method: POST
inputs: (name, email, password)

steps:
  find User by email as existing_user
  if existing_user:
    show error "Email already exists"
    stop
  create User
  generate token
  return success with token
"""

BAD = """
entity: Account
fields:
  - name: string
  - password: string

intent: admin_delete_account
route: "/api/admin/delete"
method: DELETE
inputs: (name)

steps:
  create Account
  return success
"""


def test_module_imports():
    """The hook must be importable: it once held a syntax error."""
    import madilang.plugins.ethics_hook as h
    assert hasattr(h, "evaluate_ethics")


def test_good_program_passes():
    rep = _report(GOOD)
    assert rep["passed"] is True
    assert rep["overall"] >= 0.70
    assert rep["overall"] <= 1.0


def test_bad_program_fails_and_is_dominated_by_critical_finding():
    rep = _report(BAD)
    assert rep["passed"] is False
    assert rep["critical_count"] >= 1
    assert rep["overall"] <= 0.30, "a critical finding must not leave a 0.9 score"


def test_bad_program_scores_below_good_program():
    assert _report(BAD)["overall"] < _report(GOOD)["overall"]


def test_report_shape_is_stable():
    rep = _report(GOOD)
    for key in ("overall", "passed", "threshold", "dimensions", "findings", "bar"):
        assert key in rep, key
    assert set(rep["dimensions"]) == {
        "privacy", "consent", "transparency", "accountability", "fairness", "security"
    }
