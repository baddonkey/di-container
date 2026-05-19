"""Tape Drive CLI — entry point.

Usage examples
--------------
Run with the simulator (default):
    python main.py status
    python main.py load TAPE-001
    python main.py write "Hello, tape!"
    python main.py rewind
    python main.py read 12
    python main.py unload

Run against real hardware (Linux only):
    python main.py --driver real status

Use a custom logging config:
    python main.py --log-config /etc/tapedrive/logging.json status
"""

import argparse
import sys
from pathlib import Path

from src.container import Container, DRIVER_REAL, DRIVER_SIMULATOR
from src.logging_setup import LoggingSetup


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tapedrive",
        description="Control a real or simulated tape drive from the command line.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--driver",
        choices=[DRIVER_REAL, DRIVER_SIMULATOR],
        default=DRIVER_SIMULATOR,
        help="Tape drive backend to use (default: %(default)s)",
    )
    parser.add_argument(
        "--log-config",
        metavar="PATH",
        type=Path,
        default=None,
        help="Path to a JSON logging configuration file",
    )

    sub = parser.add_subparsers(dest="command", metavar="COMMAND")
    sub.required = True

    # load
    p_load = sub.add_parser("load", help="Mount a tape by its ID")
    p_load.add_argument("tape_id", help="Tape identifier (e.g. TAPE-001)")

    # unload
    sub.add_parser("unload", help="Eject the currently mounted tape")

    # rewind
    sub.add_parser("rewind", help="Rewind the tape to the beginning")

    # seek
    p_seek = sub.add_parser("seek", help="Move the tape head to a byte position")
    p_seek.add_argument("position", type=int, help="Target byte position (≥ 0)")

    # read
    p_read = sub.add_parser("read", help="Read bytes from the current position")
    p_read.add_argument("num_bytes", type=int, help="Number of bytes to read")

    # write
    p_write = sub.add_parser("write", help="Write a UTF-8 string to the tape")
    p_write.add_argument("data", help="String data to write")

    # status
    sub.add_parser("status", help="Print current drive status")

    return parser


# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------

def _run(args: argparse.Namespace) -> int:
    container = Container(driver=args.driver)
    svc = container.tape_drive_service()

    if args.command == "load":
        ok = svc.load_tape(args.tape_id)
        print("OK — tape loaded." if ok else "ERROR — could not load tape.")
        return 0 if ok else 1

    if args.command == "unload":
        ok = svc.unload_tape()
        print("OK — tape ejected." if ok else "ERROR — could not unload tape.")
        return 0 if ok else 1

    if args.command == "rewind":
        ok = svc.rewind_tape()
        print("OK — tape rewound." if ok else "ERROR — rewind failed.")
        return 0 if ok else 1

    if args.command == "seek":
        ok = svc.seek_tape(args.position)
        print(
            f"OK — head at position {args.position}."
            if ok
            else f"ERROR — seek to {args.position} failed."
        )
        return 0 if ok else 1

    if args.command == "read":
        data = svc.read_data(args.num_bytes)
        if data is None:
            print("ERROR — read failed.")
            return 1
        print(f"Read {len(data)} byte(s): {data!r}")
        return 0

    if args.command == "write":
        payload = args.data.encode("utf-8")
        ok = svc.write_data(payload)
        print(
            f"OK — wrote {len(payload)} byte(s)."
            if ok
            else "ERROR — write failed."
        )
        return 0 if ok else 1

    if args.command == "status":
        status = svc.get_status()
        width = max(len(k) for k in status)
        for key, value in status.items():
            print(f"  {key:<{width}} : {value}")
        return 0

    return 0  # unreachable; argparse guards against unknown commands


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    log_config_path = args.log_config or Path("logging_config.json")
    LoggingSetup(log_config_path).configure()

    sys.exit(_run(args))


if __name__ == "__main__":
    main()
