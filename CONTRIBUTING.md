# Contributing

New calculators are welcome. To keep the toolkit easy to adopt:

1. **Standard library only.** No third-party imports in `netcalc/`.
2. **One topic per module**, placed in the matching package (`layer1`, `perf`,
   `ccna`, `protocols`, `aifabric`).
3. **Document the formula.** The module docstring states the equation and its
   assumptions, and starts with a one-line summary (it is shown by
   `python -m netcalc`).
4. **Pure functions first, CLI second.** Functions take SI base units (bits/s,
   bytes, seconds); `main(argv=None)` parses friendly strings with
   `netcalc.units` and prints the result.
5. **Register the tool** in `netcalc/__main__.py` and add a row to the README
   table and a section to TECHNOLOGY.md.
6. **Test it.** Add `tests/test_<module>.py` with known textbook values, and run
   `python -m unittest discover -s tests -t .` before opening a pull request.
