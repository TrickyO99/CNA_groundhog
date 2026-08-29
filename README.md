# CNA_groundhog

An Epitech project that applies simple financial-style technical-analysis
indicators (moving-average gain, rate of change, standard deviation,
Bollinger-band-like bounds) to a stream of temperature readings, to spot
trend reversals — a "Groundhog Day"-style weather-trend predictor. The
actual program is a single Python 3 script, `src/groundhog.py`; there is no
C code to compile.

## Build

The Makefile doesn't compile anything — it just copies `src/groundhog.py`
to `./groundhog` and `chmod`s it executable (a Linux/macOS convenience so
you can run `./groundhog` directly). `chmod` has no effect on Windows, so
on this machine just run the script with Python directly instead of using
`make`:

```powershell
py -3.12 src\groundhog.py <period>
```

(`make` / `mingw32-make` will still "succeed" and produce a `groundhog`
file, but that file is just a copy of the `.py` script with no extension —
it only runs if you invoke it explicitly via `py groundhog`, and even then
requires the `.py` association or `py` launcher to treat it as Python.)

## Usage

```
SYNOPSIS
    ./groundhog period

DESCRIPTION
    period      the number of days defining a period
```

- `period` (required, argv[1]) — an integer window size used by every
  indicator below. Passing `-h` instead prints the synopsis above and exits
  0. Any other invalid/missing argument exits with code `84`.
- The program then reads **whitespace-separated numeric lines from stdin**,
  one temperature value per line, until it reads the literal line `STOP`.
  Fewer than `period` values before `STOP` also exits `84`.

Example, using the sample data under `utils/`:

```powershell
py -3.12 src\groundhog.py 5 < utils\temperatures
```

For each new value once at least `period` samples exist, it prints a line
like:

```
g=1.32  r=8       s=2.14
g=0.85  r=-3      s=1.98  a switch occurs
```

- `g` — average of the recent positive day-over-day gains over the last
  `period` days ("nan" until enough history exists).
- `r` — percentage rate of change vs. the value `period` steps back.
- `s` — standard deviation of the last `period` values.
- `a switch occurs` is appended when the sign of `r` flips from the
  previous reading (an upward trend turning downward, or vice versa).

After the `STOP` line, it prints a summary:

```
Global tendency switched 3 times
5 weirdest values are [40.5, 42.1, ...]
```

`Global tendency switched N times` counts how many sign-flip "switches"
were detected. `5 weirdest values` are the five recorded values furthest
outside the Bollinger-style band (`moving average ± 2·s`); if the run
never accumulates at least 5 such candidates, the script exits `84`
instead of printing this line.

## How it works

- `calcultateG` / `sumOfLastOnes` — average of the last `period` day-over-day
  gains (negative diffs clamped to 0), i.e. a Wilder/RSI-style "average
  gain".
- `calcultateR` — `(values[i] / values[i - period]) * 100 - 100`, the
  percentage change over one `period`.
- `calcultateS` / `variance` / `deviation` — standard deviation of the last
  `period` values.
- `checkValues` — computes a simple moving average and a `± 2·s` band
  around it, then records how far the current value falls outside that
  band (values are later sorted by that distance to find the "weirdest").
- `didSwitchOccured` — compares the sign of the current `r` to the
  previous `r` to detect a trend reversal.
- The main loop (bottom of `groundhog.py`) wires these together: it reads
  one value per line from stdin, updates `g`/`r`/`s`, prints the per-line
  status, and on `STOP` prints the final switch count and the five
  weirdest values.

## Tests

`tests/test_groundhog.py` is an automated pytest suite (black-box,
subprocess-based — it runs `groundhog.py` as a child process and asserts on
its stdout/exit code, the same way a user would invoke it):

```powershell
py -3.12 -m pip install pytest   # once
py -3.12 -m pytest tests/ -v
```

19 tests, all passing as of this writing. Coverage:

- Argument handling: `-h` (usage + exit 0), missing/extra args (exit 84),
  non-numeric `period` (exit 84).
- Full runs against `utils/temperatures` at `period=5` and `period=3`:
  exit code, the `g=nan`/`r=nan` warm-up lines before enough history
  exists, the exact `Global tendency switched N times` count, the exact
  `5 weirdest values are [...]` list, total line count, and that the
  `a switch occurs` marker count agrees with the printed switch count.
  Expected values were captured from an actual run and cross-checked
  against the formulas documented above (average gain / rate of change /
  stdev / Bollinger-band distance).
- Degenerate inputs: `utils/temp0` (30 identical `0` readings) exits 84
  because the Bollinger band collapses to a single point and `checkValues`
  divides by zero — confirms the script's own `except ZeroDivisionError`
  guard fires deterministically rather than crashing with a traceback.
  Fewer readings than `period`, fewer than 5 accumulated "weirdest"
  candidates, a non-numeric reading mid-stream, and stdin closing (EOF)
  before a `STOP` line all also exit 84, as documented above.
