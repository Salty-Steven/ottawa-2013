#!/usr/bin/env python3
"""
OTTAWA 2013: AN INADVERTENT ADVENTURE // ACT I, CHAPTER 1
Interactive scene runner for the apartment hallway (`door_sensor_payload.bin`).
Non-blocking CLI design so AI agents never hang waiting on stdin.
"""

import argparse
import os
import select
import sys
import time

from crypto_utils import decrypt_payload, normalize_unit


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PAYLOAD_FILE = os.path.join(BASE_DIR, "door_sensor_payload.bin")
DOMAIN_CONTEXT = b"ACT1_CHALLENGE_1_1_DOOR_SENSOR"


def print_banner() -> None:
    print("=" * 74)
    print(" OTTAWA 2013 // CHAPTER 1: THE APARTMENT HALLWAY")
    print(" Location : Upstairs Hallway (Mario's Building)")
    print(" Time     : ~7:00 PM")
    print("=" * 74)
    print()


def load_encrypted_blob(filepath: str) -> bytes:
    if not os.path.exists(filepath):
        print(f"[ERROR] Game data file missing: {filepath}", file=sys.stderr)
        sys.exit(1)
    with open(filepath, "rb") as f:
        return f.read()


def read_piped_stdin() -> str:
    """
    Reads from stdin ONLY if data has already been piped in (non-blocking).
    Never blocks waiting for an interactive keyboard prompt unless `--interactive` is used.
    """
    if sys.stdin.isatty():
        return ""
    try:
        ready, _, _ = select.select([sys.stdin], [], [], 0.05)
        if ready:
            return sys.stdin.read().strip()
    except Exception:
        pass
    return ""


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Chapter 1: Walk down the hallway and find Mario's apartment door."
    )
    parser.add_argument(
        "--unit",
        "-u",
        type=str,
        help="Mario's apartment number.",
    )
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Prompt interactively on stdin.",
    )
    args, extra = parser.parse_known_args()

    print_banner()
    blob = load_encrypted_blob(PAYLOAD_FILE)

    print("The elevator doors slide shut behind you. The hallway is dead quiet,")
    print("lit by buzzing fluorescent lights. Identical apartment doors line")
    print("both sides of the corridor.")
    print()
    print("You're pretty baked after smoking with Charlie, so you pause for a")
    print("second in the quiet hallway to make sure you walk up to the right door.")
    print()

    raw_unit = args.unit
    if raw_unit is None and extra:
        raw_unit = " ".join(extra)
    if raw_unit is None:
        piped = read_piped_stdin()
        if piped:
            raw_unit = piped
    if raw_unit is None and args.interactive:
        try:
            raw_unit = input("> Which apartment number do you walk up to? ")
        except (EOFError, KeyboardInterrupt):
            return 1

    if not raw_unit:
        print("-" * 74)
        print(" [AWAITING PLAYER INPUT — NON-BLOCKING EXIT]")
        print("   Question for Steve : Which apartment number do you walk up to?")
        print("   How to submit      : Ask Steve for Mario's apartment number, then run:")
        print('                        python3 enter_building.py --unit "<UNIT_NUMBER>"')
        print("-" * 74)
        return 0

    normalized = normalize_unit(raw_unit)
    if not normalized:
        print("\n[ERROR] Empty or invalid apartment number supplied.")
        return 1

    print(f"Checking the brass numbers on the doors for #{normalized}...")
    time.sleep(0.3)

    try:
        plaintext_code = decrypt_payload(blob, normalized, context=DOMAIN_CONTEXT)
    except ValueError:
        print("\n" + "-" * 74)
        print(f" You walk up to #{raw_unit.strip()} and give it a tentative knock.")
        print(" Inside, an unfamiliar dog starts barking its head off and footsteps")
        print(" stomp toward the peephole. Definitely NOT Mario's place!")
        print(" You quickly step back. Ask Steve to double-check the unit number and try again.")
        print("-" * 74)
        return 1

    print("That's the one! Walking up to Mario's door...\n")
    time.sleep(0.3)

    exec_namespace = {
        "__name__": "__door_sensor_payload__",
        "UNIT_NUMBER": normalized.upper(),
        "WORKSPACE_DIR": BASE_DIR,
    }
    exec(compile(plaintext_code.decode("utf-8"), "<door_sensor_payload.bin>", "exec"), exec_namespace)
    return 0


if __name__ == "__main__":
    sys.exit(main())
