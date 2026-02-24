import uuid
from datetime import UTC, datetime, timedelta

import pytest
from jose import jwt

from backend.auth.jwt import create_access_token, create_refresh_token, decode_token
from backend.config import settings


@pytest.mark.unit
class TestJWT:
    def test_create_access_token_contains_claims(self) -> None:
        user_id = uuid.uuid4()
        org_id = uuid.uuid4()
        token = create_access_token(user_id, org_id, "admin")
        payload = decode_token(token)

        assert payload["sub"] == str(user_id)
        assert payload["org_id"] == str(org_id)
        assert payload["role"] == "admin"
        assert payload["type"] == "access"

    def test_create_access_token_without_org(self) -> None:
        user_id = uuid.uuid4()
        token = create_access_token(user_id)
        payload = decode_token(token)

        assert payload["sub"] == str(user_id)
        assert "org_id" not in payload
        assert "role" not in payload
        assert payload["type"] == "access"

    def test_create_refresh_token(self) -> None:
        user_id = uuid.uuid4()
        token = create_refresh_token(user_id)
        payload = decode_token(token)

        assert payload["sub"] == str(user_id)
        assert payload["type"] == "refresh"

    def test_expired_token_raises(self) -> None:
        payload = {
            "sub": str(uuid.uuid4()),
            "exp": datetime.now(UTC) - timedelta(hours=1),
            "type": "access",
        }
        token = jwt.encode(
            payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
        )

        with pytest.raises(Exception):
            decode_token(token)

    def test_invalid_token_raises(self) -> None:
        with pytest.raises(Exception):
            decode_token("not.a.valid.token")

    def test_wrong_secret_raises(self) -> None:
        payload = {
            "sub": str(uuid.uuid4()),
            "exp": datetime.now(UTC) + timedelta(hours=1),
            "type": "access",
        }
        token = jwt.encode(payload, "wrong-secret", algorithm="HS256")

        with pytest.raises(Exception):
            decode_token(token)
