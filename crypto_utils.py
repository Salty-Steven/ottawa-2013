"""
Core Cryptographic & Input Sanitization Primitives.
Standard Library Only (`hashlib`, `hmac`, `re`, `struct`).

Provides authenticated stream encryption (SHA-256 Counter Mode + HMAC-SHA256)
and PBKDF2-HMAC-SHA256 key derivation for hardware telemetry blobs.
"""

import hashlib
import hmac
import re
import struct
from typing import Tuple


PBKDF2_ITERATIONS = 200_000
SALT_SIZE = 16
NONCE_SIZE = 16
TAG_SIZE = 32
HEADER_MAGIC = b"OTW13v1\x00"


def normalize_unit(raw_input: str) -> str:
    """
    Canonicalizes corridor terminal unit identifiers.
    """
    cleaned = raw_input.strip().lower()
    cleaned = re.sub(r"^(apartment|apt|unit|suite|ste|#|\s)+", "", cleaned)
    cleaned = re.sub(r"[^a-z0-9]", "", cleaned)
    return cleaned


def normalize_digits(raw_input: str) -> str:
    """
    Extracts canonical 10-digit routing address from input string.
    """
    digits = re.sub(r"\D", "", raw_input)
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    return digits


def normalize_token(raw_input: str) -> str:
    """
    Canonicalizes alphanumeric passphrases by stripping whitespace and punctuation.
    """
    return re.sub(r"[^a-z0-9]", "", raw_input.lower())


def normalize_address(raw_input: str) -> str:
    """
    Canonicalizes street addresses (case-insensitive, standardizes street suffixes
    and cardinal directions, strips unit/city suffixes and punctuation).
    Example: '123 Somerset Street West, Ottawa' -> '123somersetstw'
    """
    cleaned = raw_input.strip().lower()
    # Strip trailing city/province/country if included after a comma
    cleaned = cleaned.split(",")[0]
    cleaned = re.sub(r"\b(ottawa|ontario|on|canada)\b", "", cleaned)
    # Remove punctuation
    cleaned = re.sub(r"[^a-z0-9\s]", " ", cleaned)
    tokens = cleaned.split()

    abbreviations = {
        "street": "st",
        "st": "st",
        "avenue": "ave",
        "av": "ave",
        "ave": "ave",
        "road": "rd",
        "rd": "rd",
        "drive": "dr",
        "dr": "dr",
        "boulevard": "blvd",
        "blvd": "blvd",
        "crescent": "cres",
        "cres": "cres",
        "court": "ct",
        "ct": "ct",
        "lane": "ln",
        "ln": "ln",
        "place": "pl",
        "pl": "pl",
        "parkway": "pkwy",
        "pkwy": "pkwy",
        "highway": "hwy",
        "hwy": "hwy",
        "north": "n",
        "south": "s",
        "east": "e",
        "west": "w",
    }
    normalized_tokens = [abbreviations.get(t, t) for t in tokens]
    return "".join(normalized_tokens)


def derive_keys(passphrase: str, salt: bytes, context: bytes = b"") -> Tuple[bytes, bytes]:
    """
    Derives a 32-byte cipher key and a 32-byte MAC key via PBKDF2-HMAC-SHA256.
    """
    key_material = hashlib.pbkdf2_hmac(
        "sha256",
        passphrase.encode("utf-8") + b"|" + context,
        salt,
        PBKDF2_ITERATIONS,
        dklen=64,
    )
    return key_material[:32], key_material[32:]


def compute_verification_hash(passphrase: str, salt_hex: str, context: str = "") -> str:
    """
    Computes a salted PBKDF2-HMAC-SHA256 verification digest.
    """
    salt = bytes.fromhex(salt_hex)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        (f"VERIFY:{context}:{passphrase}").encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS,
        dklen=32,
    )
    return digest.hex()


def _keystream_xor(data: bytes, enc_key: bytes, nonce: bytes) -> bytes:
    """
    Generates a keystream via HMAC-SHA256 in counter mode and XORs with `data`.
    """
    out = bytearray(len(data))
    offset = 0
    counter = 0
    while offset < len(data):
        block = hmac.new(
            enc_key,
            nonce + struct.pack(">Q", counter),
            hashlib.sha256,
        ).digest()
        chunk_len = min(32, len(data) - offset)
        for i in range(chunk_len):
            out[offset + i] = data[offset + i] ^ block[i]
        offset += chunk_len
        counter += 1
    return bytes(out)


def encrypt_payload(plaintext: bytes, passphrase: str, salt: bytes, nonce: bytes, context: bytes = b"") -> bytes:
    """
    Encrypts `plaintext` using Encrypt-then-MAC (SHA-256-CTR + HMAC-SHA256).
    """
    if len(salt) != SALT_SIZE or len(nonce) != NONCE_SIZE:
        raise ValueError("Invalid salt or nonce length.")
    enc_key, mac_key = derive_keys(passphrase, salt, context)
    ciphertext = _keystream_xor(plaintext, enc_key, nonce)
    authenticated_data = HEADER_MAGIC + salt + nonce + ciphertext
    tag = hmac.new(mac_key, authenticated_data, hashlib.sha256).digest()
    return authenticated_data + tag


def decrypt_payload(blob: bytes, passphrase: str, context: bytes = b"") -> bytes:
    """
    Verifies the HMAC-SHA256 tag and decrypts a binary telemetry blob.
    """
    min_size = len(HEADER_MAGIC) + SALT_SIZE + NONCE_SIZE + TAG_SIZE
    if len(blob) < min_size:
        raise ValueError("Telemetry blob is truncated or corrupted.")
    if blob[: len(HEADER_MAGIC)] != HEADER_MAGIC:
        raise ValueError("Invalid telemetry magic header.")

    offset = len(HEADER_MAGIC)
    salt = blob[offset : offset + SALT_SIZE]
    offset += SALT_SIZE
    nonce = blob[offset : offset + NONCE_SIZE]
    offset += NONCE_SIZE
    ciphertext = blob[offset:-TAG_SIZE]
    expected_tag = blob[-TAG_SIZE:]

    enc_key, mac_key = derive_keys(passphrase, salt, context)
    authenticated_data = blob[:-TAG_SIZE]
    computed_tag = hmac.new(mac_key, authenticated_data, hashlib.sha256).digest()

    if not hmac.compare_digest(expected_tag, computed_tag):
        raise ValueError("Integrity check failed: invalid key material.")

    return _keystream_xor(ciphertext, enc_key, nonce)
