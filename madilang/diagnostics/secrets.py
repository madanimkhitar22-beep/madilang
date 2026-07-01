# ════════════════════════════════════════════════════════════════════════════
# 🩺 MadiLang Diagnostics — Secrets & Configuration Checker
# ════════════════════════════════════════════════════════════════════════════

import os
from typing import Dict, Any


class SecretsChecker:
    """Verifies sovereign secrets and environment configuration."""
    
    REQUIRED_SECRETS = {
        "MADI_SIGNATURE_SECRET": {
            "description": "Cryptographic key for intent signing",
            "min_length": 16,
            "fallback_warning": "Using DEV fallback. NOT SAFE FOR PRODUCTION.",
        },
        "MADI_DEVELOPER_ID": {
            "description": "Sovereign identity of the developer",
            "min_length": 3,
            "fallback_warning": "Anonymous mode active.",
        },
    }
    
    def check_all(self) -> Dict[str, Any]:
        """Check all required secrets and return status report."""
        results = {}
        
        for name, config in self.REQUIRED_SECRETS.items():
            value = os.environ.get(name)
            
            if value is None:
                results[name] = {
                    "status": "⚠️ MISSING",
                    "set": False,
                    "valid": False,
                    "warning": config["fallback_warning"],
                    "description": config["description"],
                }
            elif len(value) < config["min_length"]:
                results[name] = {
                    "status": "❌ WEAK",
                    "set": True,
                    "valid": False,
                    "length": len(value),
                    "required_min": config["min_length"],
                    "warning": f"Value too short ({len(value)} < {config['min_length']})",
                    "description": config["description"],
                }
            else:
                results[name] = {
                    "status": "✅ SET",
                    "set": True,
                    "valid": True,
                    "length": len(value),
                    "masked": value[:4] + "*" * (len(value) - 4),
                    "description": config["description"],
                }
        
        # Check optional but recommended vars
        optional_vars = ["DATABASE_URL", "JWT_SECRET", "PORT"]
        for var in optional_vars:
            val = os.environ.get(var)
            results[var] = {
                "status": "✅ SET" if val else "ℹ️ NOT SET",
                "set": bool(val),
                "optional": True,
            }
        
        return {
            "secrets": results,
            "all_critical_valid": all(
                r.get("valid", False) 
                for k, r in results.items() 
                if not r.get("optional", False)
            ),
                }
