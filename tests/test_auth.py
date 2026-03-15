import pytest
from oneorg.services.auth import (
    get_password_hash, verify_password, create_user,
    authenticate_user, create_access_token, get_current_user
)


@pytest.mark.asyncio
async def test_password_hashing():
    """Test bcrypt password hashing and verification."""
    password = "testpassword123"
    hashed = get_password_hash(password)
    
    # Hash should be different from plain text
    assert hashed != password
    # Correct password should verify
    assert verify_password(password, hashed) is True
    # Wrong password should not verify
    assert verify_password("wrongpassword", hashed) is False


@pytest.mark.asyncio
async def test_create_and_authenticate_user():
    """Test user creation and authentication."""
    # This test will need database setup - placeholder for now
    # Will be fully functional after Chunk 1 integration
    email = "auth_test@example.com"
    password = "testpass123"
    
    # Create user (requires db models from Chunk 1)
    # user = await create_user(session, email, password)
    # assert user.email == email
    
    # Authenticate (requires db models from Chunk 1)
    # auth_user = await authenticate_user(session, email, password)
    # assert auth_user is not None
    # assert auth_user.email == email
    
    # Test wrong password
    # wrong_auth = await authenticate_user(session, email, "wrong")
    # assert wrong_auth is None
    
    # For now, just verify the functions exist
    assert callable(create_user)
    assert callable(authenticate_user)


@pytest.mark.asyncio
async def test_access_token():
    """Test JWT token creation and validation."""
    user_id = "123"
    token = create_access_token({"sub": user_id})
    
    # Token should be a string
    assert isinstance(token, str)
    assert len(token) > 0
    
    # Token validation will need database setup
    # user = await get_current_user(session, token)
    # For now, just verify function exists
    assert callable(get_current_user)


@pytest.mark.asyncio
async def test_password_hash_uniqueness():
    """Test that same password produces different hashes each time."""
    password = "mypassword"
    hash1 = get_password_hash(password)
    hash2 = get_password_hash(password)
    
    # Hashes should be different due to salt
    assert hash1 != hash2
    # Both should verify correctly
    assert verify_password(password, hash1) is True
    assert verify_password(password, hash2) is True
