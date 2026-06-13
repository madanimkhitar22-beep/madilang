# ════════════════════════════════════════════════════════════════════════════
# 🧠 MadiLang — Sovereign Intent-Driven Programming Language
# ════════════════════════════════════════════════════════════════════════════
# Author: El Madani El Mkhitar (madani004)
# Philosophy: Mkhitarian Ontology — Human Intent as Sovereign Layer
# Status: v0.4.0 • Active Development • Mobile-First • Ethics-by-Default
# ════════════════════════════════════════════════════════════════════════════

"""
MadiLang: Intent-Driven Programming Language

MadiLang transforms human-readable intent into production-ready backend systems.
Instead of writing code, you describe what you want, and the system generates
secure, ethical, and sovereign infrastructure automatically.

Core Principles (Mkhitarian Philosophy):
    • Clarity over complexity
    • Intent over scale
    • Sovereignty over convenience
    • Ethics by default, not as afterthought
    • Human consciousness as the sovereign layer

Quick Start:
    >>> from madilang import compile_madi
    >>> code = compile_madi("intent: create_user ...")
    >>> print(code)

CLI Usage:
    $ madi init
    $ madi run app.madi
    $ madi verify output.js

Links:
    • Repository: https://github.com/madanimkhitar22-beep/madilang
    • Philosophy: https://github.com/madanimkhitar22-beep/Mekhitarian-Philosophy
    • Sovereign Cognition: https://github.com/madanimkhitar22-beep/-Sovereign-Cognition-Engine
"""

# ────────────────────────────────────────────────────────────────────────────
# Package Metadata
# ────────────────────────────────────────────────────────────────────────────

__version__ = "0.4.0"
__author__ = "El Madani El Mkhitar"
__email__ = "madani004@proton.me"
__license__ = "MIT"
__copyright__ = "© 2026 El Madani El Mkhitar. All rights reserved."

# ────────────────────────────────────────────────────────────────────────────
# Sovereign Identity# ────────────────────────────────────────────────────────────────────────────

__philosophy__ = "Mkhitarian Ontology"
__sovereignty__ = "Human Intent as Sovereign Layer"
__ethics__ = "Ethics-by-Default • Audit-Ready • Privacy-First"

# ────────────────────────────────────────────────────────────────────────────
# Public API (Exposed for external use)
# ────────────────────────────────────────────────────────────────────────────

# Note: These will be populated as modules are implemented
# This structure enables clean imports: from madilang import compile_madi

__all__ = [
    # Core compilation API
    "compile_madi",
    "parse_madi",
    "generate_code",
    
    # Signature & Sovereignty
    "IntentSignature",
    "verify_signature",
    
    # Metadata
    "__version__",
    "__author__",
    "__license__",
    "__philosophy__",
]

# ────────────────────────────────────────────────────────────────────────────
# Lazy Imports (Deferred loading for performance on mobile)
# ────────────────────────────────────────────────────────────────────────────

def __getattr__(name):
    """
    Lazy loading of modules to minimize memory footprint.
    Critical for mobile-first development environments.
    """
    if name == "compile_madi":
        from madilang.compiler.pipeline import compile_madi
        return compile_madi
    elif name == "parse_madi":
        from madilang.compiler.parser import MadiParser
        return MadiParser
    elif name == "generate_code":
        from madilang.generators.nodejs.generator import NodeJSGenerator
        return NodeJSGenerator
    elif name == "IntentSignature":
        from madilang.ir.intent_signature import IntentSignature        
        return IntentSignature
    elif name == "verify_signature":
        from madilang.ir.intent_signature import verify_signature
        return verify_signature
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

# ────────────────────────────────────────────────────────────────────────────
# Sovereign Banner (Displayed on CLI startup)
# ────────────────────────────────────────────────────────────────────────────

def get_banner() -> str:
    """Return the sovereign banner for CLI display."""
    return f"""
╔══════════════════════════════════════════════════════════════════╗
║  🧠 MadiLang v{__version__} — Sovereign Intent Compiler                      ║
║  👤 Author: {__author__}                                                     ║
║  📜 License: {__license__}                                                   ║
║                                                                              ║
║  🏛️ Philosophy: {__philosophy__}                                             ║
║  🔐 Sovereignty: {__sovereignty__}                                           ║
║  🛡️ Ethics: {__ethics__}                                                     ║
╚══════════════════════════════════════════════════════════════════╝
"""

# ────────────────────────────────────────────────────────────────────────────
# Initialization Guard
# ────────────────────────────────────────────────────────────────────────────

def _check_environment():
    """
    Verify runtime environment meets minimum requirements.
    Provides helpful warnings for development setups.
    """
    import sys
    import warnings
    
    if sys.version_info < (3, 8):
        warnings.warn(
            f"MadiLang requires Python 3.8+. Current: {sys.version}",
            RuntimeWarning
        )
    
    # Check for JWT secret in production mode
    import os
    if os.getenv("MADI_ENV") == "production" and not os.getenv("JWT_SECRET"):
        warnings.warn(
            "⚠️ JWT_SECRET not set in production mode. "
            "Set environment variable for secure token generation.",
            UserWarning
        )
# Run environment check on import
_check_environment()
