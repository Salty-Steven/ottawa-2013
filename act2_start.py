#!/usr/bin/env python3
"""
OTTAWA 2013: AN INADVERTENT ADVENTURE // ACT II LAUNCHER
Checks for `act1_checkpoint.json` and unlocks the first scene of Act II.
"""

import hashlib
import hmac
import json
import os
import sys
import time

from crypto_utils import compute_verification_hash, decrypt_payload


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ACT1_CHECKPOINT_FILE = os.path.join(BASE_DIR, "act1_checkpoint.json")
ACT2_PAYLOAD_FILE = os.path.join(BASE_DIR, "act2_payload.bin")

# Salted PBKDF2-SHA256 verification digest for `act1_checkpoint.json` unlock token
ACT1_UNLOCK_SALT_HEX = "6798d00b70a42ab3cecf4b9f7394340e"
ACT1_UNLOCK_HASH_HEX = "a8a51f1ccd3b5c5fb51f302473343a05b5a918d44b95d2dc7d0f33b0d6ea5a71"
ACT1_UNLOCK_CONTEXT = "ACT2_GATEWAY_CHECKPOINT_VERIFY"
ACT2_STAGE_2_1_CONTEXT = b"ACT2_STAGE_2_1_ROUTE_TO_MARIO_DROP"


def print_banner() -> None:
    print("=" * 74)
    print(" OTTAWA 2013 // ACT II: MEANWHILE, ON THE OC TRANSPO BUS...")
    print(" Character : Brandon")
    print(" Location  : OC Transpo Bus Heading Downtown // ~7:05 PM")
    print("=" * 74)
    print()


def main() -> int:
    print_banner()

    if not os.path.exists(ACT1_CHECKPOINT_FILE):
        print("[LOCKED] `act1_checkpoint.json` not found in this folder.")
        print("Finish Act I (`python3 enter_building.py`) first to unlock Act II!")
        return 1

    if not os.path.exists(ACT2_PAYLOAD_FILE):
        print(f"[ERROR] Game data file missing: {ACT2_PAYLOAD_FILE}", file=sys.stderr)
        return 1

    try:
        with open(ACT1_CHECKPOINT_FILE, "r", encoding="utf-8") as f:
            checkpoint = json.load(f)
    except Exception as err:
        print(f"[ERROR] Could not read `act1_checkpoint.json`: {err}")
        return 1

    unlock_token = str(checkpoint.get("act2_unlock_token", "")).strip()
    active_session = str(checkpoint.get("telemetry", {}).get("active_session", ""))
    expected_sig = hashlib.sha256(
        f"ACT1_CLEARED:{active_session}:{unlock_token}".encode("utf-8")
    ).hexdigest()

    if not unlock_token or checkpoint.get("verification_signature") != expected_sig:
        print("[LOCKED] `act1_checkpoint.json` signature doesn't match.")
        return 1

    candidate_hash = compute_verification_hash(
        unlock_token, ACT1_UNLOCK_SALT_HEX, context=ACT1_UNLOCK_CONTEXT
    )
    if not hmac.compare_digest(candidate_hash, ACT1_UNLOCK_HASH_HEX):
        print("[LOCKED] Checkpoint token does not match this game build.")
        return 1

    print("Loading Act I save state... Rewinding the clock 20 minutes...\n")
    time.sleep(0.4)

    print("While Steve is settling in upstairs with his new stoner friends,")
    print("let's rewind a few minutes to see what happened on the other side")
    print("of that text message.")
    print()
    time.sleep(0.4)
    print("You are now playing as BRANDON.")
    print("You're riding an OC Transpo bus heading downtown to shoot some pool.")
    print("Your phone buzzes in your pocket. You pull it out at 1% battery")
    print("just as the screen lights up:")
    print()
    print('  From Steve: "Heyo, locked out of Mario\'s apt. Can\'t get back in. Going on an adventure!"')
    print()
    time.sleep(0.5)
    print("Before you can even type a single letter to reply, your phone screen")
    print("flashes black and dies completely.")
    print()
    print("From your perspective, Steve is locked out of Mario's apartment in an")
    print("unfamiliar city, Mario is dead asleep, and your phone is a brick.")
    print("You reach up, yank the yellow stop-request cord, and hop off the bus.")
    print()

    with open(ACT2_PAYLOAD_FILE, "rb") as f:
        envelope = json.load(f)

    stage_2_1_blob = bytes.fromhex(envelope["stage_2_1_hex"])
    try:
        route_script_bytes = decrypt_payload(
            stage_2_1_blob,
            unlock_token,
            context=ACT2_STAGE_2_1_CONTEXT,
        )
    except ValueError as err:
        print(f"[ERROR] Failed to unlock next scene: {err}")
        return 1

    route_script_path = os.path.join(BASE_DIR, "route_to_mario.py")
    with open(route_script_path, "wb") as f:
        f.write(route_script_bytes)
    try:
        os.chmod(route_script_path, 0o755)
    except OSError:
        pass

    print("-" * 74)
    print(" [NEW SCENE UNLOCKED: `route_to_mario.py`]")
    print("   Forget pool—you need to head straight to Mario's building to see if")
    print("   Steve is waiting outside on the sidewalk.")
    print("   >> Type: `python3 route_to_mario.py`")
    print("=" * 74)
    return 0


if __name__ == "__main__":
    sys.exit(main())
