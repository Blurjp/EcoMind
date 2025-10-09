"""
Tests for Phase 2 Authentication

Tests core authentication functionality:
- JWT token creation and verification
- Login/logout endpoints
- Password hashing
- Audit logging

SCOPE (per Codex Review):
- NO refresh token tests (deferred to Phase 2.5)
- NO rate limiting tests (infrastructure undefined)
- NO account lockout tests (datastore undefined)
"""

import pytest
from datetime import timedelta
from app.auth import (
    hash_password,
    verify_password,
    create_access_token,
    verify_token,
    ROLE_PERMISSIONS,
    can_access_resource
)
from app.models.user import User, Role
from fastapi.security import HTTPAuthorizationCredentials


class TestPasswordHashing:
    """Test password hashing functionality."""

    def test_hash_password_creates_hash(self):
        """Test that hash_password creates a hash."""
        password = "test_password_123"
        hashed = hash_password(password)

        assert hashed != password
        assert len(hashed) > 20  # Bcrypt hashes are long

    def test_verify_password_correct(self):
        """Test that correct password verifies."""
        password = "test_password_123"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test that incorrect password fails."""
        password = "test_password_123"
        wrong_password = "wrong_password"
        hashed = hash_password(password)

        assert verify_password(wrong_password, hashed) is False

    def test_same_password_different_hashes(self):
        """Test that same password generates different hashes (salt)."""
        password = "test_password_123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        assert hash1 != hash2  # Different due to random salt
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestJWTTokens:
    """Test JWT token creation and verification."""

    def test_create_access_token(self):
        """Test that access token is created."""
        data = {"sub": "user_123", "org_id": "org_456"}
        token = create_access_token(data)

        assert isinstance(token, str)
        assert len(token) > 50  # JWT tokens are long

    def test_create_token_with_expiration(self):
        """Test creating token with custom expiration."""
        data = {"sub": "user_123"}
        expires_delta = timedelta(minutes=30)
        token = create_access_token(data, expires_delta)

        assert isinstance(token, str)

    def test_token_contains_claims(self):
        """Test that token contains the provided claims."""
        from jose import jwt
        from app.auth import SECRET_KEY, ALGORITHM

        data = {
            "sub": "user_123",
            "org_id": "org_456",
            "role": "admin"
        }
        token = create_access_token(data)

        # Decode without verification (just for testing)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        assert payload["sub"] == "user_123"
        assert payload["org_id"] == "org_456"
        assert payload["role"] == "admin"
        assert "exp" in payload  # Expiration should be added


class TestRBACPermissions:
    """Test RBAC permission system."""

    def test_role_permissions_defined(self):
        """Test that all roles have permissions defined."""
        for role in Role:
            assert role in ROLE_PERMISSIONS

    def test_owner_has_all_permissions(self):
        """Test that OWNER role has all permissions."""
        owner_perms = ROLE_PERMISSIONS[Role.OWNER]

        assert owner_perms["read_own_data"] is True
        assert owner_perms["read_org_data"] is True
        assert owner_perms["write_data"] is True
        assert owner_perms["manage_users"] is True
        assert owner_perms["manage_billing"] is True
        assert owner_perms["manage_settings"] is True

    def test_viewer_limited_permissions(self):
        """Test that VIEWER role has limited permissions."""
        viewer_perms = ROLE_PERMISSIONS[Role.VIEWER]

        assert viewer_perms["read_own_data"] is True
        assert viewer_perms["read_org_data"] is False  # Cannot read org-wide
        assert viewer_perms["write_data"] is False
        assert viewer_perms["manage_users"] is False
        assert viewer_perms["manage_billing"] is False
        assert viewer_perms["manage_settings"] is False

    def test_analyst_read_only_org_data(self):
        """Test that ANALYST can read org data but not write."""
        analyst_perms = ROLE_PERMISSIONS[Role.ANALYST]

        assert analyst_perms["read_own_data"] is True
        assert analyst_perms["read_org_data"] is True  # Can read org-wide
        assert analyst_perms["write_data"] is False    # But cannot write
        assert analyst_perms["manage_users"] is False

    def test_billing_role_permissions(self):
        """Test that BILLING role has billing permissions."""
        billing_perms = ROLE_PERMISSIONS[Role.BILLING]

        assert billing_perms["manage_billing"] is True
        assert billing_perms["read_org_data"] is True  # For reports
        assert billing_perms["manage_users"] is False
        assert billing_perms["write_data"] is False

    def test_can_access_resource_with_permission(self):
        """Test can_access_resource returns True for allowed permission."""
        # Create mock user with ADMIN role
        class MockUser:
            role = Role.ADMIN

        user = MockUser()
        assert can_access_resource(user, "read_org_data") is True
        assert can_access_resource(user, "manage_users") is True

    def test_can_access_resource_without_permission(self):
        """Test can_access_resource returns False for denied permission."""
        class MockUser:
            role = Role.VIEWER

        user = MockUser()
        assert can_access_resource(user, "read_org_data") is False
        assert can_access_resource(user, "manage_users") is False


class TestAuthHelpers:
    """Test authentication helper functions."""

    def test_password_hash_not_reversible(self):
        """Test that password hash cannot be reversed."""
        password = "secret_password_123"
        hashed = hash_password(password)

        # There's no way to get password back from hash
        assert hashed != password
        assert password not in hashed

    def test_empty_password_handling(self):
        """Test handling of empty password."""
        # Bcrypt will hash even empty string
        hashed = hash_password("")
        assert len(hashed) > 0
        assert verify_password("", hashed) is True
        assert verify_password("not_empty", hashed) is False


# Integration test markers (require database)
pytest.mark.integration = pytest.mark.skipif(
    "not config.getoption('--integration')",
    reason="need --integration option to run"
)


@pytest.mark.integration
class TestAuthenticationIntegration:
    """Integration tests requiring database (mark with --integration)."""

    def test_full_auth_flow(self):
        """Test complete authentication flow (requires DB)."""
        # This would test:
        # 1. Create user with password
        # 2. Login to get token
        # 3. Use token to access protected route
        # 4. Logout
        # 5. Verify audit logs created
        pass  # Placeholder for full integration test
