# ════════════════════════════════════════════════════════════════════
# 🧠 MadiLang — Build Command (P1-4)
# ════════════════════════════════════════════════════════════════════
# Compile .madi source to target code WITHOUT execution.
# This is the foundation for reproducibility and CI/CD integration.
# ════════════════════════════════════════════════════════════════════

from pathlib import Path
from typing import Any
from madilang.compiler.parser import parse_madi
from madilang.compiler.analyzer import analyze_madi
from madilang.ir.step_compiler import compile_to_ir
from madilang.ir.intent_signature import sign_madi_program
from madilang.generators.base import get_generator, GeneratorConfig


def cmd_build(args: Any, logger) -> int:
    """
    Build command: compile .madi source to target code.
    
    Unlike `run`, this command does NOT execute the generated code.
    It only writes the output files to disk.
    
    Args:
        args: Parsed command-line arguments (uses args.file, not args.source)
        logger: CLILogger instance for output
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    source_path = Path(args.file)
    target = str(getattr(args, "target", "nodejs")).lower().strip()
    output_path = getattr(args, "output", None)
    
    # Validate source file
    if not source_path.exists():
        logger.error(f"Source file not found: {source_path}")
        return 1
    
    if not source_path.suffix == ".madi":
        logger.error(f"Source file must have .madi extension: {source_path}")
        return 1
    
    logger.info(f"📖 Reading {source_path}")
    
    try:
        # Read source (utf-8-sig strips BOM if present)
        source_code = source_path.read_text(encoding="utf-8-sig")
        
        # Parse
        logger.info("🔍 Parsing...")
        ast = parse_madi(source_code)
        
        # Analyze
        logger.info("📋 Analyzing...")
        analyzed = analyze_madi(ast)
        
        # Compile to IR
        logger.info("⚙️ Compiling to IR...")
        ir_program = compile_to_ir(analyzed)
        
        # Sign intent
        logger.info("🔐 Signing intent...")
        # ✅ Fixed: sign_madi_program expects (source, program, developer_id)
        signature = sign_madi_program(source_code, analyzed)
        ir_program.signature = signature.to_dict() if hasattr(signature, 'to_dict') else signature
        
        # Generate code
        logger.info(f"🏗️ Generating {target} code...")
        
        # Determine output directory
        if output_path:
            output_dir = Path(output_path)
            # If output_path is a file (has extension), use its parent
            if output_dir.suffix:
                output_dir = output_dir.parent
        else:
            output_dir = Path(".")
        
        config = GeneratorConfig(output_dir=str(output_dir))
        generator = get_generator(target, config)
        
        if generator is None:
            logger.error(f"Unknown target: {target}")
            return 1
        
        result = generator.generate_program(ir_program)
        
        if not result.success:
            logger.error(f"Generation failed: {result.errors}")
            return 1
        
        # Write output files
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for filename, content in result.files.items():
            file_path = output_dir / filename
            file_path.write_text(content, encoding="utf-8")
            logger.info(f"📄 Generated {file_path}")
        
        logger.success(f"✅ Build complete: {len(result.files)} file(s) generated in {output_dir}")
        return 0
        
    except Exception as e:
        logger.error(f"❌ Build error: {e}")
        return 1