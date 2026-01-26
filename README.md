# netcalc-toolkit

Small, dependency-free Python calculators for network engineers: Layer 1
link budgets and FEC, latency/jitter/loss, CCNA/CCNP subnetting and routing
metrics, protocol overhead, and AI/ML fabric sizing (multipath transport,
Ultra Ethernet-style spraying, RoCE/PFC/DCQCN, buffers, collectives).

* **Standard library only.** Python 3.9+, nothing to `pip install` to run it.
* **Every module is both a library and a CLI.** Import the functions, or run
  `python -m netcalc <tool> --help`.
* **Formulas are documented.** Each module's docstring shows the equation it
  implements, and [TECHNOLOGY.md](TECHNOLOGY.md) explains the concepts.
* **Tested.** 140+ unit tests under `tests/`.
