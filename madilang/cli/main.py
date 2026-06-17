# ════════════════════════════════════════════════════════════════════════════
# 🧠 MadiLang — Command Line Interface (CLI) (Refined v0.4.0)
# ════════════════════════════════════════════════════════════════════════════
# Sovereign CLI for compiling, running, and managing MadiLang projects.
# Status: ACTIVATED • Sovereign-by-Design • Mobile-First • Robust Parsers
# ════════════════════════════════════════════════════════════════════════════

"""
MadiLang CLI

This module provides the command-line interface for MadiLang.
It enables developers to compile, run, verify, and manage MadiLang projects.
"""

import sys
import os
import argparse
import json
import subprocess
import re
from pathlib import Path
from typing import Optional, List, Dict, Any

# Import MadiLang core
import madilang
from madilang.compiler.parser import parse_madi
from madilang.compiler.analyzer import analyze_madi, AnalysisException
from madilang.ir.step_compiler import compile_to_ir
from madilang.ir.intent_signature import (
    create_signature_engine,
    SignatureTransformer,
    verify_madi_signature,
)
from madilang.generators.base import get_generator, GeneratorConfig, GenerationResult
from madilang.cli.logger import CLILogger, LogLevel


# ────────────────────────────────────────────────────────────────────────────
# CLI Application
# ────────────────────────────────────────────────────────────────────────────

class MadiCLI:
    """MadiLang Command Line Interface managing compiler states."""
    
    def __init__(self):
        self.logger = CLILogger()
        self.parser = self._create_parser()
        self._audit_log: List[Dict[str, Any]] = []
    
    def _create_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            prog="madi",
            description="🧠 MadiLang: Sovereign Intent-Driven Programming Language",
            epilog="Code is no longer written; it is described.",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        parser.add_argument("--version", "-v", action="version", version=f"MadiLang v{madilang.__version__}")
        parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
        parser.add_argument("--silent", action="store_true", help="Suppress all output except errors")
        
        subparsers = parser.add_subparsers(dest="command", help="Available commands")
        
        # ── init command ──
        init_parser = subparsers.add_parser("init", help="Initialize a new MadiLang project")
        init_parser.add_argument("name", nargs="?", default="madi-project", help="Project name (default: madi-project)")
        init_parser.add_argument("--template", choices=["basic", "auth", "full"], default="basic", help="Project template (default: basic)")
        
        # ── run command ──
        run_parser = subparsers.add_parser("run", help="Compile and run a .madi file")
        run_parser.add_argument("file", help="Path to .madi file")
        run_parser.add_argument("--target", choices=["nodejs", "python", "go"], default="nodejs", help="Target language (default: nodejs)")
        run_parser.add_argument("--output", "-o", help="Output file path")
        run_parser.add_argument("--no-run", action="store_true", help="Compile only, do not run")
        run_parser.add_argument("--port", "-p", type=int, default=3000, help="Server port (default: 3000)")
        run_parser.add_argument("--no-signature", action="store_true", help="Disable sovereign signature embedding")
        
        # ── build command ──
        build_parser = subparsers.add_parser("build", help="Compile .madi file to target language")
        build_parser.add_argument("file", help="Path to .madi file")
        build_parser.add_argument("--target", choices=["nodejs", "python", "go"], default="nodejs", help="Target language (default: nodejs)")
        build_parser.add_argument("--output", "-o", help="Output directory or file path")
        build_parser.add_argument("--no-signature", action="store_true", help="Disable sovereign signature embedding")
        
        # ── verify command ──
        verify_parser = subparsers.add_parser("verify", help="Verify sovereign signature of generated code")
        verify_parser.add_argument("file", help="Path to generated code file")
        verify_parser.add_argument("--source", help="Path to original .madi source for verification")
        
        # ── check command ──
        check_parser = subparsers.add_parser("check", help="Analyze and validate .madi source")
        check_parser.add_argument("file", help="Path to .madi file")
        check_parser.add_argument("--json", action="store_true", help="Output analysis as JSON")
        
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
            
            if parsed.command == "init": return self.cmd_init(parsed)
            elif parsed.command == "run": return self.cmd_run(parsed)
            elif parsed.command == "build": return self.cmd_build(parsed)
            elif parsed.command == "verify": return self.cmd_verify(parsed)
            elif parsed.command == "check": return self.cmd_check(parsed)
            else:
                self.logger.error(f"Unknown command: {parsed.command}")
                return 1
                
        except KeyboardInterrupt:
            self.logger.warning("\nInterrupted by user")
            return 130
        except Exception as e:
            self.logger.error(f"Unexpected error: {type(e).__name__}: {e}")
            if os.getenv("MADI_DEBUG"):
                import traceback
                traceback.print_exc()
            return 1
    
    # ────────────────────────────────────────────────────────────────────────
    # Command: init
    # ────────────────────────────────────────────────────────────────────────
    
    def cmd_init(self, args) -> int:
        project_name = args.name
        project_path = Path(project_name)
        self.logger.info(f"🚀 Initializing MadiLang project: {project_name}")
        
        try:
            project_path.mkdir(parents=True, exist_ok=True)
            (project_path / "src").mkdir(exist_ok=True)
            (project_path / "examples").mkdir(exist_ok=True)
            
            main_madi = self._get_template_madi(args.template)
            (project_path / "src" / "main.madi").write_text(main_madi, encoding="utf-8")
            (project_path / ".env.example").write_text(self._get_env_template(), encoding="utf-8")
            (project_path / ".gitignore").write_text(self._get_gitignore(), encoding="utf-8")
            (project_path / "README.md").write_text(self._get_readme_template(project_name), encoding="utf-8")
            
            self.logger.success(f"✅ Project initialized at {project_path}")
            self.logger.info("\n📋 Next steps:")
            self.logger.info(f"   cd {project_name}")
            self.logger.info("   madi run src/main.madi")
            return 0
        except Exception as e:
            self.logger.error(f"Failed to initialize project: {e}")
            return 1
            
    def _get_template_madi(self, template: str) -> str:
        """Get template .madi content."""
        if template == "auth":
            return '''entity: User
fields:
    - name: string
    - email: string (unique)
    - password: string (secure)
    - createdAt: datetime (auto)

intent: register_user
route: "/api/signup"
method: POST
inputs: (name, email, password)

steps:
    find User by email as existing_user
    
    if existing_user:
        show error "Email already exists"
        stop process
    
    create User
    generate token
    return success with token

intent: login_user
route: "/api/login"
method: POST
inputs: (email, password)

steps:
    find User by email as user
    
    if user not found:
        show error "User not found"
        stop process
    
    if password does not match user.password:
        show error "Invalid credentials"
        stop process
    
    generate token
    return success with token
'''
        else:
            return '''entity: Item
fields:
    - title: string
    - description: string
    - completed: boolean
    - createdAt: datetime (auto)

intent: create_item
route: "/api/items"
method: POST
inputs: (title, description)

steps:
    create Item
    return success

intent: get_items
route: "/api/items"
method: GET

steps:
    return success
'''

    def _get_env_template(self) -> str:
        return "PORT=3000\nNODE_ENV=development\nDATABASE_URL=postgresql://user:pass@localhost:5432/madidb\nJWT_SECRET=devsecret\n"

    def _get_gitignore(self) -> str:
        return "node_modules/\n.venv/\noutput.js\ndist/\n.env\n*.log\n"

    def _get_readme_template(self, name: str) -> str:
        return f"# {name}\nSovereign backend powered by MadiLang.\n"

    # ────────────────────────────────────────────────────────────────────────
    # Command: run & build
    # ────────────────────────────────────────────────────────────────────────
    
    def cmd_run(self, args) -> int:
        file_path = Path(args.file)
        if not file_path.exists():
            self.logger.error(f"File not found: {file_path}")
            return 1
        
        self.logger.info(f"📖 Reading {file_path}")
        try:
            source = file_path.read_text(encoding="utf-8")
        except Exception as e:
            self.logger.error(f"Failed to read file: {e}")
            return 1
        
        result = self._compile(source, args)
        if not result.success:
            for error in result.errors:
                self.logger.error(error)
            return 1
        
        raw_output = getattr(args, "output", None)
        if raw_output:
            output_path = Path(raw_output)
            if output_path.is_dir():
                output_path = output_path / ("index.js" if args.target == "nodejs" else "main.py")
        else:
            output_path = Path("output.js")
            
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(result.code, encoding="utf-8")
            self.logger.success(f"✅ Generated {output_path}")
        except Exception as e:
            self.logger.error(f"Failed to write output: {e}")
            return 1
        
        if not getattr(args, "no_run", False):
            return self._run_output(output_path, args)
        return 0
    
    def _compile(self, source: str, args) -> GenerationResult:
        self.logger.info("🔍 Parsing...")
        try:
            ast = parse_madi(source)
        except Exception as e:
            return GenerationResult(success=False, errors=[f"Parse error: {e}"])
        
        self.logger.info("📋 Analyzing...")
        try:
            ast = analyze_madi(ast)
        except AnalysisException as e:
            return GenerationResult(success=False, errors=[str(err) for err in e.errors])
        
        self.logger.info("⚙️ Compiling to IR...")
        ir = compile_to_ir(ast)
        
        if not getattr(args, "no_signature", False):
            self.logger.info("🔐 Signing intent...")
            try:
                dev_id = os.getenv("MADI_DEVELOPER_ID", "anonymous")
                engine = create_signature_engine(developer_id=dev_id)
                transformer = SignatureTransformer(engine)
                ast = transformer.transform(source, ast)
                ir = compile_to_ir(ast)
                
                sig_obj = getattr(ast, "signature", getattr(getattr(ast, "program", None), "signature", None))
                if sig_obj:
                    engine.sign_ir(ir, sig_obj)
            except Exception as e:
                self.logger.warning(f"Signature injection failed: {e}")
        
        target_lang = str(args.target).lower().strip()
        self.logger.info(f"🏗️ Generating {target_lang} code...")
        try:
            config = GeneratorConfig(
                include_signature=not getattr(args, "no_signature", False),
                add_runtime_verification=True
            )
            generator = get_generator(target_lang, config=config)
            return generator.generate_program(ir)
        except Exception as e:
            return GenerationResult(success=False, errors=[f"Generation error: {e}"])
    
    def _run_output(self, output_path: Path, args) -> int:
        self.logger.info("🚀 Starting server...")
        env = {**os.environ, "PORT": str(getattr(args, "port", 3000))}
        
        try:
            process = subprocess.Popen(["node", str(output_path)], env=env)
            return process.wait()
        except KeyboardInterrupt:
            self.logger.warning("\nStopping sovereign background server node safely...")
            if 'process' in locals():
                process.terminate()
                process.wait()
            return 130
        except FileNotFoundError:
            self.logger.error("Node.js not found. Install Node.js to run the output.")
            return 1
        except Exception as e:
            self.logger.error(f"Server runtime failure: {e}")
            return 1
            
    def cmd_build(self, args) -> int:
        args.no_run = True
        return self.cmd_run(args)
    
    # ────────────────────────────────────────────────────────────────────────
    # Command: verify
    # ────────────────────────────────────────────────────────────────────────
    
    def cmd_verify(self, args) -> int:
        file_path = Path(args.file)
        if not file_path.exists():
            self.logger.error(f"File not found: {file_path}")
            return 1
        
        self.logger.info(f"🔍 Verifying {file_path}")
        try:
            content = file_path.read_text(encoding="utf-8")
            
            sig_match = re.search(r'__MADI_SIGNATURE__\s*=\s*(\{.*?\n\s*\});?', content, re.DOTALL) or \
                        re.search(r'__MADI_SIGNATURE__\s*=\s*(\{.*?\});?', content, re.DOTALL)
            
            if not sig_match:
                lines = [line for line in content.splitlines() if "__MADI_SIGNATURE__" in line]
                if lines:
                    json_str = lines[0].split("=", 1)[1].strip().rstrip(";").strip("'\"")
                    signature = json.loads(json_str)
                else:
                    self.logger.error("No sovereign signature found in file")
                    return 1
            else:
                signature = json.loads(sig_match.group(1))
            
            self.logger.info(f"👤 Developer: {signature.get('developer', {}).get('id')}")
            self.logger.info(f"📅 Generated: {signature.get('timestamp', {}).get('iso')}")
            self.logger.info(f"🔖 Intent Hash: {signature.get('intent', {}).get('hash', '')[:32]}...")
            
            if signature.get('ethics'):
                score = signature['ethics'].get('score')
                if score is not None:
                    self.logger.info(f"🛡️ Ethics Score: {score:.2f}")
            
            self.logger.success("✅ Signature structure valid")
            return 0
        except Exception as e:
            self.logger.error(f"Verification failed: {e}")
            return 1
    
    # ────────────────────────────────────────────────────────────────────────
    # Command: check
    # ────────────────────────────────────────────────────────────────────────
    
    def cmd_check(self, args) -> int:
        file_path = Path(args.file)
        if not file_path.exists():
            self.logger.error(f"File not found: {file_path}")
            return 1
        
        try:
            source = file_path.read_text(encoding="utf-8")
        except Exception as e:
            self.logger.error(f"Failed to read file: {e}")
            return 1
        
        self.logger.info("🔍 Analyzing...")
        try:
            ast = parse_madi(source)
            ast = analyze_madi(ast)
            
            report = {
                "success": True,
                "entities": len(ast.entities) if hasattr(ast, "entities") else 0,
                "intents": len(ast.intents) if hasattr(ast, "intents") else 0,
                "errors": [],
                "warnings": []
            }
            
            if args.json:
                print(json.dumps(report, indent=2))
            else:
                self.logger.success("✅ Analysis passed")
                self.logger.info(f"   Entities: {report['entities']}")
                self.logger.info(f"   Intents: {report['intents']}")
            return 0
        except AnalysisException as e:
            report = {"success": False, "errors": [str(err) for err in e.errors], "warnings": []}
            if args.json:
                print(json.dumps(report, indent=2))
            else:
                self.logger.error("❌ Analysis failed")
                for err in e.errors: self.logger.error(f"   {err}")
            return 1
        except Exception as e:
            self.logger.error(f"Analysis error: {e}")
            return 1


# ────────────────────────────────────────────────────────────────────────────
# Entry Point
# ────────────────────────────────────────────────────────────────────────────

def main() -> int:
    cli = MadiCLI()
    return cli.run()


if __name__ == "__main__":
    sys.exit(main())

