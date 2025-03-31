"""BFD timers: negotiated intervals, detection time, packet load and false positives.

Each BFD session negotiates the transmit interval in each direction as the
slower of what the sender wants to send and what the receiver can accept::

    tx_interval(A->B) = max(A.desired_min_tx, B.required_min_rx)

and B declares the session down after ``A.detect_mult`` intervals without
a packet::

    detection_time(at B) = A.detect_mult * tx_interval(A->B)

So 300 ms x 3 detects a failure in 900 ms and 50 ms x 3 in 150 ms. Fast
timers cost CPU or line-card capacity (packets per second per session) and
raise the chance that random loss of ``mult`` consecutive packets takes a
healthy session down.

Usage::

    python -m netcalc.routing.bfd detect --local-tx 50ms --local-rx 50ms --remote-tx 100ms --remote-rx 50ms --mult 3
    python -m netcalc.routing.bfd load --interval 50ms --sessions 400
    python -m netcalc.routing.bfd flaps --interval 10ms --mult 3 --loss 1e-3
"""

import argparse

from netcalc.units import fmt_time, parse_time


def negotiated_interval(sender_desired_tx, receiver_required_rx):
    """Transmit interval (s) actually used from sender to receiver."""
    return max(sender_desired_tx, receiver_required_rx)


def detection_time(sender_detect_mult, sender_desired_tx, receiver_required_rx):
    """Time (s) for the receiver to declare the session down.

    >>> round(detection_time(3, 0.3, 0.05), 3)
    0.9
    """
    return sender_detect_mult * negotiated_interval(sender_desired_tx, receiver_required_rx)


def session_detection_times(local_tx, local_rx, remote_tx, remote_rx, local_mult=3, remote_mult=3):
    """Detection time at the local and at the remote end: ``(local, remote)``."""
    at_local = detection_time(remote_mult, remote_tx, local_rx)
    at_remote = detection_time(local_mult, local_tx, remote_rx)
    return at_local, at_remote


def packets_per_second(interval_s, sessions=1, both_directions=True):
    """Control packets per second a router sends (and receives, if both directions)."""
    pps = sessions / interval_s
    return pps * 2 if both_directions else pps


def false_down_probability(loss, mult):
    """Probability that ``mult`` consecutive packets are lost on a healthy link."""
    return loss ** mult


def false_downs_per_day(interval_s, mult, loss):
    """Expected spurious session-downs per day from random packet loss."""
    return 86400 / interval_s * false_down_probability(loss, mult)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("detect", help="negotiated intervals and detection times")
    p.add_argument("--local-tx", required=True)
    p.add_argument("--local-rx", required=True)
    p.add_argument("--remote-tx", required=True)
    p.add_argument("--remote-rx", required=True)
    p.add_argument("--mult", type=int, default=3, help="detect multiplier on both ends")
    p = sub.add_parser("load", help="packet rate for many sessions")
    p.add_argument("--interval", required=True)
    p.add_argument("--sessions", type=int, required=True)
    p = sub.add_parser("flaps", help="false session-downs caused by random loss")
    p.add_argument("--interval", required=True)
    p.add_argument("--mult", type=int, default=3)
    p.add_argument("--loss", type=float, required=True)
    args = parser.parse_args(argv)

    if args.cmd == "detect":
        lt, lr, rt, rr = (parse_time(x) for x in (args.local_tx, args.local_rx,
                                                  args.remote_tx, args.remote_rx))
        at_local, at_remote = session_detection_times(lt, lr, rt, rr, args.mult, args.mult)
        print(f"local -> remote every {fmt_time(negotiated_interval(lt, rr))}, "
              f"remote detects in {fmt_time(at_remote)}")
        print(f"remote -> local every {fmt_time(negotiated_interval(rt, lr))}, "
              f"local detects in {fmt_time(at_local)}")
    elif args.cmd == "load":
        print(f"{packets_per_second(parse_time(args.interval), args.sessions):,.0f} packets/s "
              f"(tx + rx)")
    else:
        rate = false_downs_per_day(parse_time(args.interval), args.mult, args.loss)
        print(f"P(false down per interval) {false_down_probability(args.loss, args.mult):.1e}, "
              f"~{rate:.3g} false downs per day")


if __name__ == "__main__":
    main()
