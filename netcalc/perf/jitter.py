"""Jitter: RFC 3550 interarrival jitter, IPDV and delay statistics.

RTP (RFC 3550, section 6.4.1) defines interarrival jitter as a running
estimate of the mean deviation of the transit-time difference between
consecutive packets::

    D(i-1, i) = (R_i - R_(i-1)) - (S_i - S_(i-1))
    J = J + (|D(i-1, i)| - J) / 16

where S is the sender timestamp and R the receive time. Clock offset
between the hosts cancels out, so the two clocks need not be synchronised.

IP packet delay variation (IPDV, RFC 3393/5481) is the sequence of
consecutive one-way delay differences; PDV is each delay minus the minimum.

Usage::

    python -m netcalc.perf.jitter rfc3550 --send 0 20 40 60 --recv 5 26 44 67
    python -m netcalc.perf.jitter stats 10.1 10.4 9.8 12.0 10.2
    python -m netcalc.perf.jitter file delays.csv      # columns: send,recv
"""

import argparse
import csv
import math
import statistics


def rfc3550_series(send_times, recv_times):
    """Jitter estimate after every packet, starting from J = 0."""
    if len(send_times) != len(recv_times) or len(send_times) < 2:
        raise ValueError("need two equal-length lists with at least two packets")
    j, series = 0.0, []
    for i in range(1, len(send_times)):
        d = (recv_times[i] - recv_times[i - 1]) - (send_times[i] - send_times[i - 1])
        j += (abs(d) - j) / 16
        series.append(j)
    return series


def rfc3550_jitter(send_times, recv_times):
    """Final RFC 3550 jitter estimate (same units as the inputs)."""
    return rfc3550_series(send_times, recv_times)[-1]


def ipdv(delays):
    """Consecutive delay differences (IP packet delay variation)."""
    return [b - a for a, b in zip(delays, delays[1:])]


def pdv(delays):
    """Packet delay variation relative to the minimum delay."""
    floor = min(delays)
    return [d - floor for d in delays]


def percentile(values, pct):
    """Linear-interpolated percentile (``pct`` from 0 to 100)."""
    ordered = sorted(values)
    if not ordered:
        raise ValueError("no values")
    rank = (len(ordered) - 1) * pct / 100
    lo, hi = math.floor(rank), math.ceil(rank)
    return ordered[lo] + (ordered[hi] - ordered[lo]) * (rank - lo)


def delay_stats(delays):
    """Summary statistics for one-way delays or RTT samples."""
    diffs = [abs(x) for x in ipdv(delays)] or [0.0]
    return {
        "count": len(delays),
        "min": min(delays),
        "mean": statistics.fmean(delays),
        "max": max(delays),
        "stdev": statistics.pstdev(delays),
        "p99": percentile(delays, 99),
        "mean_abs_ipdv": statistics.fmean(diffs),
        "pdv_p99": percentile(pdv(delays), 99),
    }


def read_csv(path):
    """Read ``send,recv`` timestamp pairs from a CSV file (header optional)."""
    send, recv = [], []
    with open(path, newline="") as fh:
        for row in csv.reader(fh):
            try:
                s, r = float(row[0]), float(row[1])
            except (ValueError, IndexError):
                continue
            send.append(s)
            recv.append(r)
    return send, recv


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("rfc3550", help="jitter from send/receive timestamps")
    p.add_argument("--send", type=float, nargs="+", required=True)
    p.add_argument("--recv", type=float, nargs="+", required=True)
    p = sub.add_parser("stats", help="statistics of delay samples")
    p.add_argument("delays", type=float, nargs="+")
    p = sub.add_parser("file", help="RFC 3550 jitter and stats from a CSV of send,recv")
    p.add_argument("path")
    args = parser.parse_args(argv)

    if args.cmd == "rfc3550":
        print(f"RFC 3550 jitter: {rfc3550_jitter(args.send, args.recv):.4f}")
    elif args.cmd == "stats":
        for key, value in delay_stats(args.delays).items():
            print(f"{key:>14}: {value:.4f}" if isinstance(value, float) else f"{key:>14}: {value}")
    else:
        send, recv = read_csv(args.path)
        print(f"RFC 3550 jitter: {rfc3550_jitter(send, recv):.4f}")
        delays = [r - s for s, r in zip(send, recv)]
        for key, value in delay_stats(delays).items():
            print(f"{key:>14}: {value:.4f}" if isinstance(value, float) else f"{key:>14}: {value}")


if __name__ == "__main__":
    main()
