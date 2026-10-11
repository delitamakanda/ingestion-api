from ingestion_api.core.security.password import hash_password, verify_password


def test_hash_and_verify_password():
    password = "my_secure_password"
    hashed_password = hash_password(password)
    assert verify_password(password, hashed_password)
    assert not verify_password("wrong_password", hashed_password)


def test_hash_password_is_different_each_time():
    password = "my_secure_password"
    hashed_password1 = hash_password(password)
    hashed_password2 = hash_password(password)
    assert hashed_password1 != hashed_password2


def test_verify_password_with_invalid_password():
    hashed_password = hash_password("my_secure_password")
    assert not verify_password("wrong_password", hashed_password)
