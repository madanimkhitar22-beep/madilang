# ════════════════════════════════════════════════════════════════════════════
# 🧠 MadiLang — CLI Entry Point (Purified v0.5.1)
# ════════════════════════════════════════════════════════════════════════════
# Lightweight entry point with lazy command loading.
# All command logic lives in cli/commands/*.py for modularity.
# Status: CERTIFIED • Clean Architecture • Type-Safe
# ════════════════════════════════════════════════════════════════════════════

import sys
import os
import argparse
from typing import Optional, List, Any

import madilang
from madilang.cli.logger import CLILogger, LogLevel


class MadiCLI:
    """MadiLang Command Line Interface — Modular Architecture."""

    def __init__(self):
        self.logger = CLILogger()
        self.parser = self._create_parser()

    def _create_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            prog="madi",
            description="🧠 MadiLang: Sovereign Intent-Driven Programming Language",
            epilog="Code is no longer written; it is described.",
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )

        parser.add_argument("--version", "-v", action="version", version=f"MadiLang v{madilang.__version__}")
        parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
        parser.add_argument("--silent", action="store_true", help="Suppress all output except errors")

        subparsers = parser.add_subparsers(dest="command", help="Available commands")

        # ── init ──
        init_p = subparsers.add_parser("init", help="Initialize a new MadiLang project")
        init_p.add_argument("name", nargs="?", default="madi-project", help="Project name")
        init_p.add_argument("--template", choices=["basic", "auth", "full"], default="basic")

        # ── run ──
        run_p = subparsers.add_parser("run", help="Compile and run a .madi file")
        run_p.add_argument("file", help="Path to .madi file")
        run_p.add_argument("--target", choices=["nodejs", "python", "go"], default="nodejs")
        run_p.add_argument("--output", "-o", help="Output file path")
        run_p.add_argument("--no-run", action="store_true", help="Compile only")
        run_p.add_argument("--port", "-p", type=int, default=3000)
        run_p.add_argument("--no-signature", action="store_true")

        # ── build ──
        build_p = subparsers.add_parser("build", help="Compile .madi to target language")
        build_p.add_argument("file", help="Path to .madi file")
        build_p.add_argument("--target", choices=["nodejs", "python", "go"], default="nodejs")
        build_p.add_argument("--output", "-o", help="Output path")
        build_p.add_argument("--no-signature", action="store_true")

        # ── verify ──
        verify_p = subparsers.add_parser("verify", help="Verify sovereign signature")
        verify_p.add_argument("file", help="Path to generated code")
        verify_p.add_argument("--source", help="Original .madi source")

        # ── check ──
        check_p = subparsers.add_parser("check", help="Analyze and validate .madi source")
        check_p.add_argument("file", help="Path to .madi file")
        check_p.add_argument("--json", action="store_true")

        # ── doctor ──
        subparsers.add_parser("doctor", help="Diagnose environment and configuration")

        return parser

    def run(self, args: Optional[List[str]] = None) -> int:
        try:
            parsed = self.parser.parse_args(args)

            if parsed.silent:
                self.logger.set_level(LogLevel.ERROR)
            elif parsed.verbose:
                self.logger.set_level(LogLevel.DEBUG)

            if not parsed.command:
                self.parser.print_help()
                return 0

            result: Any = 0

            # 🔌 Lazy command dispatch — imports dynamically only when invoked
            if parsed.command == "init":
                from madilang.cli.commands.init_cmd import cmd_init
                result = cmd_init(parsed, self.logger)

            elif parsed.command == "run":
                from madilang.cli.commands.run_cmd import cmd_run
                result = cmd_run(parsed, self.logger)

            elif parsed.command == "build":
                # 🛡️ تم تصحيح المرجع هنا ليستدعي ملف البناء المستقل بدقة
                from madilang.cli.commands.build_cmd import cmd_build
                result = cmd_build(parsed, self.logger)

            elif parsed.command == "verify":
                from madilang.cli.commands.verify_cmd import cmd_verify
                result = cmd_verify(parsed, self.logger)

            elif parsed.command == "check":
                from madilang.cli.commands.check_cmd import cmd_check
                result = cmd_check(parsed, self.logger)

            elif parsed.command == "doctor":
                from madilang.cli.commands.doctor_cmd import run_doctor
                result = run_doctor(self.logger)

            else:
                self.logger.error(f"Unknown command: {parsed.command}")
                return 1

            # ضمان إرجاع القيمة كـ Integer دائماً لإرضاء الـ Type Checkers ونظام التشغيل
            return int(result) if result is not None else 0

        except KeyboardInterrupt:
            self.logger.warning("\nInterrupted by user")
            return 130
        except Exception as e:
            self.logger.error(f"Unexpected error: {type(e).__name__}: {e}")
            if os.getenv("MADI_DEBUG"):
                import traceback
                traceback.print_exc()
            return 1


def main() -> int:
    cli = MadiCLI()
    return cli.run()


if __name__ == "__main__":
    sys.exit(main())
