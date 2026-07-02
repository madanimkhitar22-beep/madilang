"""MadiLang CLI — run & build commands."""

import os
import subprocess
from pathlib import Path
from madilang.cli.logger import CLILogger
from madilang.compiler.parser import parse_madi
from madilang.compiler.analyzer import analyze_madi, AnalysisException
from madilang.ir.step_compiler import compile_to_ir
from madilang.ir.intent_signature import create_signature_engine, SignatureTransformer
from madilang.generators.base import get_generator, GeneratorConfig, GenerationResult


def cmd_run(args, logger: CLILogger) -> int:
    file_path = Path(args.file)
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return 1

    logger.info(f"📖 Reading {file_path}")
    try:
        source = file_path.read_text(encoding="utf-8")
    except Exception as e:
        logger.error(f"Failed to read file: {e}")
        return 1

    result = _compile(source, args, logger)
    if not result.success:
        for error in result.errors:
            logger.error(error)
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
        logger.success(f"✅ Generated {output_path}")

        if hasattr(result, 'files') and result.files:
            for name, content in result.files.items():
                if name in ["index.js", "output.js"]:
                    continue
                fp = output_path.parent / name
                fp.parent.mkdir(parents=True, exist_ok=True)
                fp.write_text(content, encoding="utf-8")
                logger.info(f"📄 Generated {name}")
    except Exception as e:
        logger.error(f"Failed to write output: {e}")
        return 1

    if not getattr(args, "no_run", False):
        return _run_output(output_path, args, logger)
    return 0


def cmd_build(args, logger: CLILogger) -> int:
    args.no_run = True
    return cmd_run(args, logger)


def _compile(source: str, args, logger: CLILogger) -> GenerationResult:
    logger.info("🔍 Parsing...")
    try:
        ast = parse_madi(source)
    except Exception as e:
        return GenerationResult(success=False, errors=[f"Parse error: {e}"])

    logger.info("📋 Analyzing...")
    try:
        ast = analyze_madi(ast)
    except AnalysisException as e:
        return GenerationResult(success=False, errors=[str(err) for err in e.errors])

    logger.info("⚙️ Compiling to IR...")
    ir = compile_to_ir(ast)

    if not getattr(args, "no_signature", False):
        logger.info("🔐 Signing intent...")
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
            logger.warning(f"Signature injection failed: {e}")

    target_lang = str(args.target).lower().strip()
    logger.info(f"🏗️ Generating {target_lang} code...")
    try:
        config = GeneratorConfig(
            include_signature=not getattr(args, "no_signature", False),
            add_runtime_verification=True
        )
        generator = get_generator(target=target_lang, config=config)
        return generator.generate_program(ir)
    except Exception as e:
        return GenerationResult(success=False, errors=[f"Generation error: {e}"])


def _run_output(output_path: Path, args, logger: CLILogger) -> int:
    target = str(getattr(args, "target", "nodejs")).lower().strip()
    
    if target == "python":
        # ── Python/FastAPI Runner ──
        req_file = output_path.parent / "requirements.txt"
        venv_path = output_path.parent / ".venv"
        
        if req_file.exists() and not venv_path.exists():
            logger.info("📦 Installing Python dependencies...")
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", "-r", str(req_file)],
                    cwd=str(output_path.parent),
                    check=True, capture_output=True, text=True
                )
                logger.success("✅ Python dependencies installed")
            except subprocess.CalledProcessError as e:
                logger.error(f"pip install failed: {e.stderr}")
                return 1
        
        logger.info("🚀 Starting FastAPI server...")
        env = {**os.environ, "PORT": str(getattr(args, "port", 8000))}
        try:
            process = subprocess.Popen(
                [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", str(env["PORT"])],
                cwd=str(output_path.parent), env=env
            )
            return process.wait()
        except KeyboardInterrupt:
            logger.warning("\nStopping FastAPI server safely...")
            if 'process' in locals():
                process.terminate()
                process.wait()
            return 130
        except Exception as e:
            logger.error(f"FastAPI runtime failure: {e}")
            return 1
    
    else:
        # ── Node.js/Express Runner (Original) ──
        package_json = output_path.parent / "package.json"
        node_modules = output_path.parent / "node_modules"
        
        if package_json.exists() and not node_modules.exists():
            logger.info("📦 Installing dependencies (npm install)...")
            try:
                subprocess.run(["npm", "install"], cwd=str(output_path.parent), check=True, capture_output=True, text=True)
                logger.success("✅ Dependencies installed successfully")
            except subprocess.CalledProcessError as e:
                logger.error(f"npm install failed: {e.stderr}")
                return 1
            except FileNotFoundError:
                logger.error("npm command not found. Please install Node.js.")
                return 1
        
        logger.info("🚀 Starting server...")
        env = {**os.environ, "PORT": str(getattr(args, "port", 3000))}
        try:
            process = subprocess.Popen(["node", str(output_path)], env=env)
            return process.wait()
        except KeyboardInterrupt:
            logger.warning("\nStopping sovereign background server node safely...")
            if 'process' in locals():
                process.terminate()
                process.wait()
            return 130
        except FileNotFoundError:
            logger.error("Node.js not found. Install Node.js to run the output.")
            return 1
        except Exception as e:
            logger.error(f"Server runtime failure: {e}")
            return 1
