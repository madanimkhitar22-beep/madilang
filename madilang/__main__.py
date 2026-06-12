# ════════════════════════════════════════════════════════════════════════════
# 🧠 MadiLang — Module Entry Point
# ════════════════════════════════════════════════════════════════════════════
# Enables: python -m madilang [args]
# Status: v0.4.0 • Mobile-First • Sovereign-by-Design
# ════════════════════════════════════════════════════════════════════════════

"""
MadiLang Module Entry Point

This file enables running MadiLang as a Python module:
    $ python -m madilang [command] [args]

It delegates all CLI logic to madilang.cli.main for clean separation.
"""

import sys


def main() -> int:
    """
    Entry point for `python -m madilang`.
    
    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    try:
        from madilang.cli.main import main as cli_main
        return cli_main()
    except ImportError as e:
        print(f"❌ Failed to import CLI module: {e}", file=sys.stderr)
        print("💡 Ensure madilang is installed: pip install madilang", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"❌ Unexpected error: {type(e).__name__}: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
