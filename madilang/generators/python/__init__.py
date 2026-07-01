# ════════════════════════════════════════════════════════════════════════════
# 🧠 MadiLang — Python/FastAPI Generator Module
# ════════════════════════════════════════════════════════════════════════════
# This module registers the PythonFastAPIGenerator with the core registry.
# Importing this package triggers the @register_generator decorator.
# ════════════════════════════════════════════════════════════════════════════

from madilang.generators.python.generator import PythonFastAPIGenerator

__all__ = ["PythonFastAPIGenerator"]
