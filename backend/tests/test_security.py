"""Tests of password hashing and JWT token helpers."""

from datetime import datetime, timedelta, timezone

import jwt as pyjwt
import pytest

from app.core.config import settings
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


class TestHashPassword:
    def test_hash_is_not_plaintext(self):
        hashed = hash_password("1234")

        assert hashed != "1234"
        assert "1234" not in hashed

    def test_verify_matches_correct_password(self):
        hashed = hash_password("1234")

        assert verify_password("1234", hashed) is True

    def test_verify_rejects_wrong_password(self):
        hashed = hash_password("1234")

        assert verify_password("9999", hashed) is False

    def test_same_password_hashes_to_different_salts(self):
        first = hash_password("1234")
        second = hash_password("1234")

        assert first != second

    def test_verify_rejects_malformed_hash(self):
        assert verify_password("1234", "not-a-valid-hash") is False


class TestCreateAccessToken:
    def test_token_decodes_back_with_subject_and_role(self):
        token = create_access_token(
            subject="admin@demo.com",
            role="ADMIN",
        )

        payload = decode_access_token(token)

        assert payload["sub"] == "admin@demo.com"
        assert payload["role"] == "ADMIN"

    def test_token_has_expiration(self):
        token = create_access_token(
            subject="operario@demo.com",
            role="VIEWER",
        )

        payload = decode_access_token(token)

        assert "exp" in payload
        assert payload["exp"] > datetime.now(
            timezone.utc
        ).timestamp()

    def test_token_contains_viewer_role(self):
        token = create_access_token(
            subject="operario@demo.com",
            role="VIEWER",
        )

        assert decode_access_token(token)["role"] == "VIEWER"


class TestDecodeAccessToken:
    def test_rejects_expired_token(self):
        expired = pyjwt.encode(
            {
                "sub": "admin@demo.com",
                "role": "ADMIN",
                "exp": datetime.now(timezone.utc)
                - timedelta(days=1),
            },
            settings.jwt_secret,
            algorithm=settings.jwt_algorithm,
        )

        with pytest.raises(pyjwt.ExpiredSignatureError):
            decode_access_token(expired)

    def test_rejects_invalid_token(self):
        with pytest.raises(pyjwt.PyJWTError):
            decode_access_token("este-no-es-un-jwt")

    def test_rejects_tampered_token(self):
        token = create_access_token(
            subject="admin@demo.com",
            role="ADMIN",
        )
        tampered = token[:-4] + ("abcd" if token[-4:] != "abcd" else "wxyz")

        with pytest.raises(pyjwt.PyJWTError):
            decode_access_token(tampered)