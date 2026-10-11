from datetime import timedelta
from uuid import uuid4

import jwt
import pytest

from ingestion_api.core.security.tokens import (
    InvalidTokenError,
    create_access_token,
    decode_access_token,
)


def test_create_and_decode_access_token():
    # Create a unique user ID for testing
    user_id = str(uuid4())

    # Create an access token for the user
    token = create_access_token(sub=user_id, role="user")

    # Decode the access token to retrieve the user ID
    decoded_user_id = decode_access_token(token)

    # Assert that the decoded user ID matches the original user ID
    assert decoded_user_id["sub"] == str(user_id)
    assert decoded_user_id["role"] == "user"
    assert "iat" in decoded_user_id  # Check if issued at time is present
    assert "exp" in decoded_user_id  # Check if expiration time is present


def test_invalid_token():
    # Create an invalid token (e.g., a random string)
    invalid_token = "invalid.token.string"

    # Attempt to decode the invalid token and expect an InvalidTokenError
    with pytest.raises(InvalidTokenError):
        decode_access_token(invalid_token)


def test_token_signed_with_wrong_secret_is_rejected():
    token = jwt.encode(
        {"sub": "user_id", "role": "admin"}, "wrong_secret_key", algorithm="HS256"
    )

    # Attempt to decode the token with the wrong secret key and expect an InvalidTokenError
    with pytest.raises(InvalidTokenError):
        decode_access_token(token)


def test_expired_token_is_rejected():
    # Create a token that expires immediately
    token = create_access_token(
        sub="user_id", role="admin", expires_delta=timedelta(seconds=-1)
    )

    # Attempt to decode the expired token and expect an InvalidTokenError
    with pytest.raises(InvalidTokenError):
        decode_access_token(token)
