"""
Automated regression tests for src/groundhog.py.

Run with:
    py -3.12 -m pip install pytest      # once, if not already installed
    py -3.12 -m pytest tests/ -v

These are black-box tests: they invoke groundhog.py as a subprocess, feed it
stdin (piped from the sample data under utils/, or ad-hoc strings for edge
cases), and assert on stdout, exit code, and specific computed values. The
expected numeric values below were captured from an actual run of the
current script against utils/temperatures and utils/temp0 and hand-checked
against the formulas documented in README.md (g = average of last `period`
positive day-over-day gains, r = % change vs `period` steps back, s = stdev
of the last `period` values, switches = sign flips of r, weirdest values =
furthest outside the +-2s Bollinger band). They serve as a regression net:
if a future change to groundhog.py alters these values, these tests fail.
"""
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = PROJECT_ROOT / "src" / "groundhog.py"
UTILS = PROJECT_ROOT / "utils"


def run_groundhog(args, stdin_text=""):
    """Run groundhog.py with the given argv and stdin, return CompletedProcess."""
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        input=stdin_text,
        capture_output=True,
        text=True,
        timeout=10,
    )


def read_utils(name):
    return (UTILS / name).read_text()


# ---------------------------------------------------------------------------
# Argument handling
# ---------------------------------------------------------------------------

def test_help_flag_prints_usage_and_exits_zero():
    result = run_groundhog(["-h"])
    assert result.returncode == 0
    assert "SYNOPSIS" in result.stdout
    assert "./groundhog period" in result.stdout
    assert "DESCRIPTION" in result.stdout


def test_missing_argument_exits_84():
    result = run_groundhog([])
    assert result.returncode == 84


def test_too_many_arguments_exits_84():
    result = run_groundhog(["5", "extra"])
    assert result.returncode == 84


def test_non_numeric_period_exits_84():
    result = run_groundhog(["abc"])
    assert result.returncode == 84


# ---------------------------------------------------------------------------
# Full runs against the sample data (utils/temperatures), period=5
# ---------------------------------------------------------------------------

def test_period5_temperatures_exits_zero():
    result = run_groundhog(["5"], stdin_text=read_utils("temperatures"))
    assert result.returncode == 0


def test_period5_temperatures_first_lines_are_nan_until_period_reached():
    result = run_groundhog(["5"], stdin_text=read_utils("temperatures"))
    lines = result.stdout.splitlines()
    # With period=5, g and r need `index >= period` values of history, so
    # the first 4 lines (index 0..3) must show g=nan and r=nan.
    for line in lines[:4]:
        assert "g=nan" in line
        assert "r=nan%" in line


def test_period5_temperatures_s_appears_before_g_and_r():
    result = run_groundhog(["5"], stdin_text=read_utils("temperatures"))
    lines = result.stdout.splitlines()
    # s only needs `index >= period - 1` = 4 values of history, one fewer
    # than g/r, so the 5th line (index 4) should have a real s but still
    # nan g/r.
    fifth_line = lines[4]
    assert "g=nan" in fifth_line
    assert "r=nan%" in fifth_line
    assert "s=nan" not in fifth_line


def test_period5_temperatures_switch_count():
    result = run_groundhog(["5"], stdin_text=read_utils("temperatures"))
    assert "Global tendency switched 4 times" in result.stdout


def test_period5_temperatures_weirdest_values():
    result = run_groundhog(["5"], stdin_text=read_utils("temperatures"))
    assert "5 weirdest values are [21.6, 29.4, 24.0, 27.2, 26.7]" in result.stdout


def test_period5_temperatures_line_count():
    result = run_groundhog(["5"], stdin_text=read_utils("temperatures"))
    lines = result.stdout.splitlines()
    # 74 data lines (one per temperature reading before STOP) + 2 summary
    # lines ("Global tendency switched..." and "5 weirdest values...").
    assert len(lines) == 76


def test_period5_temperatures_a_switch_occurs_marker():
    result = run_groundhog(["5"], stdin_text=read_utils("temperatures"))
    switch_lines = [l for l in result.stdout.splitlines() if "a switch occurs" in l]
    # Marker line count must agree with the printed summary count.
    assert len(switch_lines) == 4


# ---------------------------------------------------------------------------
# Full run against the sample data, a different period (period=3)
# ---------------------------------------------------------------------------

def test_period3_temperatures_exits_zero():
    result = run_groundhog(["3"], stdin_text=read_utils("temperatures"))
    assert result.returncode == 0


def test_period3_temperatures_switch_count_differs_from_period5():
    """A different period is expected to produce a different switch count
    and weirdest-value set than period=5 -- this guards against the period
    argument being silently ignored."""
    result5 = run_groundhog(["5"], stdin_text=read_utils("temperatures"))
    result3 = run_groundhog(["3"], stdin_text=read_utils("temperatures"))
    assert result3.returncode == 0
    assert "Global tendency switched 7 times" in result3.stdout
    assert result3.stdout != result5.stdout


def test_period3_temperatures_weirdest_values():
    result = run_groundhog(["3"], stdin_text=read_utils("temperatures"))
    assert "5 weirdest values are [26.4, 23.6, 26.7, 24.0, 27.2]" in result.stdout


# ---------------------------------------------------------------------------
# Edge cases: degenerate / insufficient data
# ---------------------------------------------------------------------------

def test_all_zero_readings_exits_84_on_zero_division():
    """utils/temp0 is 30 identical '0' readings then STOP. The Bollinger
    band (mobileAverage +- 2*s) collapses to a single point once s == 0,
    so checkValues' diff = (value - lowBand) / (highBand - lowBand) divides
    by zero; the script's own except ZeroDivisionError -> exit(84) should
    fire deterministically."""
    result = run_groundhog(["5"], stdin_text=read_utils("temp0"))
    assert result.returncode == 84


def test_fewer_values_than_period_exits_84():
    result = run_groundhog(["100"], stdin_text="1\n2\n3\nSTOP\n")
    assert result.returncode == 84


def test_period_1_exits_84_because_fewer_than_5_weirdest_values_collected():
    """Only 3 samples are fed in, so even though the run completes the main
    loop, fewer than 5 'weirdest value' candidates get collected and the
    script's own len(weirdestValues) >= 5 guard exits 84."""
    result = run_groundhog(["1"], stdin_text="1\n2\n3\nSTOP\n")
    assert result.returncode == 84


def test_non_numeric_reading_exits_84():
    result = run_groundhog(["2"], stdin_text="1\nnotanumber\n3\nSTOP\n")
    assert result.returncode == 84


def test_eof_without_stop_exits_84():
    """The script only breaks its read loop on a literal 'STOP' line; if
    stdin closes first (EOFError from input()), it must exit 84 rather than
    hang or crash with a traceback."""
    result = run_groundhog(["2"], stdin_text="1\n2\n3\n4\n")
    assert result.returncode == 84


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
