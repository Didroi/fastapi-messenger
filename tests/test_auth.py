from app.auth import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)

USER_ID = "b4ec85dc-47fb-4f37-bb43-bfb8c53952a7"


# --- hash_password ---


def test_hash_password_returns_string():
    result = hash_password("Password1")
    assert isinstance(result, str)


def test_hash_password_not_equal_to_original():
    password = "Password1"
    assert hash_password(password) != password


def test_hash_password_different_hashes_for_same_password():
    # bcrypt генерирует разные хеши для одного пароля (соль)
    assert hash_password("Password1") != hash_password("Password1")


# --- verify_password ---


def test_verify_password_correct():
    hashed = hash_password("Password1")
    assert verify_password("Password1", hashed) is True


def test_verify_password_wrong():
    hashed = hash_password("Password1")
    assert verify_password("WrongPassword1", hashed) is False


def test_verify_password_case_sensitive():
    hashed = hash_password("Password1")
    assert verify_password("password1", hashed) is False


# --- create_access_token ---


def test_create_access_token_returns_string():
    token = create_access_token(USER_ID)
    assert isinstance(token, str)


def test_create_access_token_has_three_parts():
    # JWT состоит из трёх частей разделённых точкой
    token = create_access_token(USER_ID)
    assert len(token.split(".")) == 3


# --- decode_access_token ---


def test_decode_access_token_returns_user_id():
    token = create_access_token(USER_ID)
    assert decode_access_token(token) == USER_ID


def test_decode_access_token_invalid_token():
    assert decode_access_token("invalid.token.here") is None


def test_decode_access_token_empty_string():
    assert decode_access_token("") is None


def test_decode_access_token_tampered_token():
    token = create_access_token(USER_ID)
    tampered = token[:-5] + "XXXXX"
    assert decode_access_token(tampered) is None
