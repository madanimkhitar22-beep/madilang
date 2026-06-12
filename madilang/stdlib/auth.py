# ════════════════════════════════════════════════════════════════════════════
# 🧠 MadiLang — Standard Library: Authentication & Security (Refined)
# ════════════════════════════════════════════════════════════════════════════
# Sovereign authentication utilities for JWT, password hashing, and validation.
# Status: v0.4.0 • Sovereign-by-Design • Production-Ready
# ════════════════════════════════════════════════════════════════════════════

"""
MadiLang Authentication Standard Library

This module provides secure, sovereign authentication utilities used by
generated backends and CLI tools. All functions follow security best practices.
"""

import os
import jwt
import bcrypt
import warnings
import hashlib
import base64
import secrets
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from enum import Enum, auto


# ────────────────────────────────────────────────────────────────────────────
# Enums and Constants
# ────────────────────────────────────────────────────────────────────────────

class TokenAlgorithm(Enum):
    """Supported JWT algorithms."""
    HS256 = "HS256"
    HS384 = "HS384"
    HS512 = "HS512"


class PasswordStrength(Enum):
    """Password strength levels."""
    WEAK = auto()
    MEDIUM = auto()
    STRONG = auto()
    VERY_STRONG = auto()


# Default configuration
DEFAULT_BCRYPT_ROUNDS = 10
DEFAULT_TOKEN_EXPIRY_HOURS = 24
DEFAULT_TOKEN_ALGORITHM = TokenAlgorithm.HS256
MIN_PASSWORD_LENGTH = 8


# ────────────────────────────────────────────────────────────────────────────
# Configuration
# ────────────────────────────────────────────────────────────────────────────

@dataclass
class AuthConfig:
    """Authentication configuration loading securely from global environment descriptors."""
    jwt_secret: str = field(default_factory=lambda: os.getenv("JWT_SECRET", ""))
    jwt_algorithm: TokenAlgorithm = DEFAULT_TOKEN_ALGORITHM
    jwt_expiry_hours: int = DEFAULT_TOKEN_EXPIRY_HOURS
    
    # Password Configuration
    bcrypt_rounds: int = DEFAULT_BCRYPT_ROUNDS
    min_password_length: int = MIN_PASSWORD_LENGTH
    require_special_chars: bool = True
    require_numbers: bool = True
    require_uppercase: bool = True
    
    # Audit Configuration
    enable_audit: bool = True
    audit_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    
    def __post_init__(self):
        if not self.jwt_secret:
            warnings.warn(
                "⚠️ JWT_SECRET not configured. Using development fallback. "
                "Set JWT_SECRET environment variable for production.",
                UserWarning
            )
            self.jwt_secret = "MADI_DEV_SECRET_CHANGE_IN_PRODUCTION"
        
        if self.bcrypt_rounds < 4:
            warnings.warn("⚠️ Bcrypt rounds too low. Minimum recommended is 10.", UserWarning)
            self.bcrypt_rounds = 4


# ────────────────────────────────────────────────────────────────────────────
# Data Transfer Objects (DTOs)
# ────────────────────────────────────────────────────────────────────────────

@dataclass
class TokenResult:
    """Result of token operations."""
    success: bool = True
    token: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    error_code: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {"success": self.success}
        if self.token:
            result["token"] = self.token
        if self.payload:
            result["payload"] = self.payload
        if self.error:
            result["error"] = self.error
        if self.error_code:
            result["error_code"] = self.error_code
        return result


@dataclass
class PasswordResult:
    """Result of password operations."""
    success: bool = True
    hashed: Optional[str] = None
    matches: bool = False
    strength: Optional[PasswordStrength] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "success": self.success,
            "matches": self.matches,
            "errors": self.errors,
            "warnings": self.warnings
        }
        if self.hashed:
            result["hashed"] = self.hashed
        if self.strength:
            result["strength"] = self.strength.name
        return result


# ────────────────────────────────────────────────────────────────────────────
# JWT Engine
# ────────────────────────────────────────────────────────────────────────────

class JWTEngine:
    """JWT token generation and verification engine."""
    
    def __init__(self, config: Optional[AuthConfig] = None):
        self.config = config or AuthConfig()
    
    def generate_token(
        self,
        payload: Dict[str, Any],
        expiry_hours: Optional[int] = None,
        include_issued_at: bool = True
    ) -> TokenResult:
        try:
            token_payload = payload.copy()
            now = datetime.now(timezone.utc)
            expiry = expiry_hours if expiry_hours is not None else self.config.jwt_expiry_hours
            
            # ✅ Fixed: Converted datetime structures to Unix epoch integer timestamps to avoid serializability errors
            token_payload["exp"] = int((now + timedelta(hours=expiry)).timestamp())
            
            if include_issued_at:
                token_payload["iat"] = int(now.timestamp())
            
            token_payload["madi"] = {
                "version": "0.4.0",
                "generated_at": now.isoformat()
            }
            
            token = jwt.encode(
                token_payload,
                self.config.jwt_secret,
                algorithm=self.config.jwt_algorithm.value
            )
            
            self._audit("token_generated", {
                "payload_keys": list(payload.keys()),
                "expiry_hours": expiry,
                "algorithm": self.config.jwt_algorithm.value
            })
            return TokenResult(success=True, token=token, payload=token_payload)
            
        except Exception as e:
            self._audit("token_generation_failed", {"error": str(e)})
            return TokenResult(
                success=False,
                error=f"Token generation failed: {str(e)}",
                error_code="TOKEN_GENERATION_ERROR"
            )
    
    def verify_token(self, token: str, require_exp: bool = True) -> TokenResult:
        try:
            options = {"require": ["exp"]} if require_exp else {}
            payload = jwt.decode(
                token,
                self.config.jwt_secret,
                algorithms=[self.config.jwt_algorithm.value],
                options=options
            )
            
            self._audit("token_verified", {"payload_keys": list(payload.keys()), "has_madi": "madi" in payload})
            return TokenResult(success=True, payload=payload)
            
        except jwt.ExpiredSignatureError:
            self._audit("token_expired", {})
            return TokenResult(success=False, error="Token has expired", error_code="TOKEN_EXPIRED")
        except jwt.InvalidSignatureError:
            self._audit("token_invalid_signature", {})
            return TokenResult(success=False, error="Invalid token signature", error_code="INVALID_SIGNATURE")
        except jwt.InvalidTokenError as e:
            self._audit("token_invalid", {"error": str(e)})
            return TokenResult(success=False, error=f"Invalid token: {str(e)}", error_code="INVALID_TOKEN")
        except Exception as e:
            self._audit("token_verification_failed", {"error": str(e)})
            return TokenResult(success=False, error=f"Token verification failed: {str(e)}", error_code="VERIFICATION_ERROR")
    
    def refresh_token(self, token: str, new_expiry_hours: Optional[int] = None) -> TokenResult:
        result = self.verify_token(token, require_exp=False)
        if not result.success and result.error_code not in ["TOKEN_EXPIRED"]:
            return result
        if not result.payload:
            return TokenResult(success=False, error="Cannot refresh: no payload", error_code="REFRESH_FAILED")
        
        payload = result.payload.copy()
        payload.pop("exp", None)
        payload.pop("iat", None)
        payload.pop("madi", None)
        return self.generate_token(payload, expiry_hours=new_expiry_hours)
    
    def _audit(self, action: str, details: Dict[str, Any]):
        if not self.config.enable_audit:
            return
        audit_entry = {"action": action, "timestamp": datetime.now(timezone.utc).isoformat(), "details": details}
        if self.config.audit_callback:
            try:
                self.config.audit_callback(audit_entry)
            except Exception:
                pass


# ────────────────────────────────────────────────────────────────────────────
# Password Engine
# ────────────────────────────────────────────────────────────────────────────

class PasswordEngine:
    """Password hashing and validation engine."""
    
    def __init__(self, config: Optional[AuthConfig] = None):
        self.config = config or AuthConfig()
    
    def hash_password(self, password: str) -> PasswordResult:
        try:
            validation = self.validate_password(password)
            if validation.errors:
                return PasswordResult(success=False, errors=validation.errors, warnings=validation.warnings)
            
            salt = bcrypt.gensalt(rounds=self.config.bcrypt_rounds)
            hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
            return PasswordResult(success=True, hashed=hashed.decode("utf-8"), strength=validation.strength)
        except Exception as e:
            return PasswordResult(success=False, errors=[f"Password hashing failed: {str(e)}"])
    
    def verify_password(self, password: str, hashed: str) -> PasswordResult:
        try:
            # ✅ Fixed: Wrapped and formatted hash variables to defend against raw byte encoding mismatches
            passwd_bytes = password.encode("utf-8")
            hash_bytes = hashed.encode("utf-8") if isinstance(hashed, str) else hashed
            
            matches = bcrypt.checkpw(passwd_bytes, hash_bytes)
            return PasswordResult(success=True, matches=matches)
        except Exception as e:
            return PasswordResult(success=False, errors=[f"Password verification failed: {str(e)}"])
    
    def validate_password(self, password: str) -> PasswordResult:
        errors = []
        warnings = []
        
        if len(password) < self.config.min_password_length:
            errors.append(f"Password must be at least {self.config.min_password_length} characters")
        if self.config.require_uppercase and not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")
        if self.config.require_numbers and not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one number")
        if self.config.require_special_chars:
            special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?/"
            if not any(c in special_chars for c in password):
                errors.append("Password must contain at least one special character")
                
        strength = self._calculate_strength(password)
        if strength == PasswordStrength.MEDIUM:
            warnings.append("Password strength is medium. Consider using a stronger password.")
        elif strength == PasswordStrength.WEAK:
            warnings.append("Password strength is weak. Please use a stronger password.")
            
        return PasswordResult(success=len(errors) == 0, errors=errors, warnings=warnings, strength=strength)
    
    def _calculate_strength(self, password: str) -> PasswordStrength:
        score = 0
        score += min(len(password) // 4, 4)
        if any(c.isupper() for c in password): score += 1
        if any(c.islower() for c in password): score += 1
        if any(c.isdigit() for c in password): score += 1
        if any(not c.isalnum() for c in password): score += 2
        
        if score >= 8: return PasswordStrength.VERY_STRONG
        elif score >= 6: return PasswordStrength.STRONG
        elif score >= 4: return PasswordStrength.MEDIUM
        return PasswordStrength.WEAK
    
    def generate_secure_password(self, length: int = 16, include_special: bool = True) -> str:
        alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        if include_special:
            alphabet += "!@#$%^&*()_+-=[]{}|;:,.<>?/"
        return "".join(secrets.choice(alphabet) for _ in range(length))


# ────────────────────────────────────────────────────────────────────────────
# API Key Engine
# ────────────────────────────────────────────────────────────────────────────

class APIKeyEngine:
    """API key generation and validation engine."""
    
    def __init__(self, config: Optional[AuthConfig] = None):
        self.config = config or AuthConfig()
    
    def generate_api_key(self, prefix: str = "madi", length: int = 32) -> str:
        random_part = secrets.token_urlsafe(length)
        return f"{prefix}_{random_part}"
    
    def hash_api_key(self, api_key: str) -> str:
        return hashlib.sha256(api_key.encode("utf-8")).hexdigest()
    
    def verify_api_key(self, api_key: str, hashed_key: str) -> bool:
        # ✅ Fixed: Substituted native '==' operator with strict static 'secrets.compare_digest' to prevent timing attacks
        current_hash = self.hash_api_key(api_key)
        return secrets.compare_digest(current_hash, hashed_key)


# ────────────────────────────────────────────────────────────────────────────
# Convenience Functions
# ────────────────────────────────────────────────────────────────────────────

_jwt_engine: Optional[JWTEngine] = None
_password_engine: Optional[PasswordEngine] = None
_api_key_engine: Optional[APIKeyEngine] = None


def get_jwt_engine(config: Optional[AuthConfig] = None) -> JWTEngine:
    global _jwt_engine
    if _jwt_engine is None:
        _jwt_engine = JWTEngine(config)
    return _jwt_engine


def get_password_engine(config: Optional[AuthConfig] = None) -> PasswordEngine:
    global _password_engine
    if _password_engine is None:
        _password_engine = PasswordEngine(config)
    return _password_engine


def get_api_key_engine(config: Optional[AuthConfig] = None) -> APIKeyEngine:
    global _api_key_engine
    if _api_key_engine is None:
        _api_key_engine = APIKeyEngine(config)
    return _api_key_engine


def generate_token(payload: Dict[str, Any], expiry_hours: Optional[int] = None) -> TokenResult:
    return get_jwt_engine().generate_token(payload, expiry_hours)


def verify_token(token: str) -> TokenResult:
    return get_jwt_engine().verify_token(token)


def hash_password(password: str) -> PasswordResult:
    return get_password_engine().hash_password(password)


def verify_password(password: str, hashed: str) -> PasswordResult:
    return get_password_engine().verify_password(password, hashed)


def generate_api_key(prefix: str = "madi") -> str:
    return get_api_key_engine().generate_api_key(prefix)
