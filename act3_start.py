#!/usr/bin/env python3
"""
OTTAWA 2013: AN INADVERTENT ADVENTURE // ACT III LAUNCHER
Checks for `act2_checkpoint.json` and unlocks Act III: Mario's Perspective.
"""

import hashlib
import hmac
import json
import os
import sys
import time

from crypto_utils import compute_verification_hash, decrypt_payload


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ACT2_CHECKPOINT_FILE = os.path.join(BASE_DIR, "act2_checkpoint.json")
ACT3_PAYLOAD_FILE = os.path.join(BASE_DIR, "act3_payload.bin")

# Salted PBKDF2-SHA256 verification digest for `act2_checkpoint.json` unlock token
ACT2_UNLOCK_SALT_HEX = "2e14293d0b7907a8ffa4b9aa6a1c7b45"
ACT2_UNLOCK_HASH_HEX = "7323eb84e8337bc5833cfdc775c52f6a351ad68d447408a97635c76aab21dc3f"
ACT2_UNLOCK_CONTEXT = "ACT3_GATEWAY_CHECKPOINT_VERIFY"
ACT3_STAGE_3_1_CONTEXT = b"ACT3_STAGE_3_1_MARIO_SLEEPING_DROP"


def print_banner() -> None:
    print("=" * 74)
    print(" OTTAWA 2013 // ACT III: MEANWHILE, INSIDE MARIO'S BEDROOM...")
    print(" Character : Mario")
    print(" Location  : Dead Asleep in Bed // 7:00 PM onwards")
    print("=" * 74)
    print()


def main() -> int:
    print_banner()

    if not os.path.exists(ACT2_CHECKPOINT_FILE):
        print("[LOCKED] `act2_checkpoint.json` not found in this folder.")
        print("Finish Act II (`python3 act2_start.py`) first to unlock Act III!")
        return 1

    if not os.path.exists(ACT3_PAYLOAD_FILE):
        print(f"[ERROR] Game data file missing: {ACT3_PAYLOAD_FILE}", file=sys.stderr)
        return 1

    try:
        with open(ACT2_CHECKPOINT_FILE, "r", encoding="utf-8") as f:
            checkpoint = json.load(f)
    except Exception as err:
        print(f"[ERROR] Could not read `act2_checkpoint.json`: {err}")
        return 1

    unlock_token = str(checkpoint.get("act3_unlock_token", "")).strip()
    if not unlock_token:
        print("[LOCKED] `act2_checkpoint.json` is missing its unlock token.")
        return 1

    candidate_hash = compute_verification_hash(
        unlock_token, ACT2_UNLOCK_SALT_HEX, context=ACT2_UNLOCK_CONTEXT
    )
    if not hmac.compare_digest(candidate_hash, ACT2_UNLOCK_HASH_HEX):
        print("[LOCKED] Checkpoint token does not match this game build.")
        return 1

    print("Loading Act II save state... Cutting to the inside of Mario's apartment...\n")
    time.sleep(0.4)

    with open(ACT3_PAYLOAD_FILE, "rb") as f:
        envelope = json.load(f)

    stage_3_1_blob = bytes.fromhex(envelope["stage_3_1_hex"])
    try:
        mario_script_bytes = decrypt_payload(
            stage_3_1_blob,
            unlock_token,
            context=ACT3_STAGE_3_1_CONTEXT,
        )
    except ValueError as err:
        print(f"[ERROR] Failed to unlock Act III scene: {err}")
        return 1

    mario_script_path = os.path.join(BASE_DIR, "mario_sleeping.py")
    with open(mario_script_path, "wb") as f:
        f.write(mario_script_bytes)
    try:
        os.chmod(mario_script_path, 0o755)
    except OSError:
        pass

    print("While Steve was locked out in the hallway, smoking with strangers,")
    print("and Brandon was running around downtown Ottawa with a")
    print("dead phone...")
    print()
    print("...it is now time to experience the harrowing, high-stakes perspective")
    print("of MARIO.")
    print()
    print("-" * 74)
    print(" [NEW SCENE UNLOCKED: `mario_sleeping.py`]")
    print("   >> Type: `python3 mario_sleeping.py`")
    print("=" * 74)
    return 0


if __name__ == "__main__":
    sys.exit(main())
