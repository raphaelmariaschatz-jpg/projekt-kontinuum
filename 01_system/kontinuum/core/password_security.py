# © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations

from argon2 import PasswordHasher, Type
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError


class PasswordSecurity:
    """Argon2id password hashing policy for local Kontinuum credentials."""

    def __init__(self):
        self.hasher = PasswordHasher(
            time_cost=3,
            memory_cost=65536,
            parallelism=2,
            hash_len=32,
            salt_len=16,
            type=Type.ID,
        )

    def hash(self, password: str) -> str:
        return self.hasher.hash(password or "")

    def verify(self, encoded_hash: str, password: str) -> bool:
        if not self.is_argon2id(encoded_hash):
            return False
        try:
            return bool(self.hasher.verify(encoded_hash, password or ""))
        except (InvalidHashError, VerificationError, VerifyMismatchError):
            return False

    def needs_rehash(self, encoded_hash: str) -> bool:
        try:
            return self.hasher.check_needs_rehash(encoded_hash)
        except (InvalidHashError, VerificationError):
            return True

    @staticmethod
    def is_argon2id(encoded_hash: str) -> bool:
        return str(encoded_hash or "").startswith("$argon2id$")
