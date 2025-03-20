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
