"""MadiLang CLI — check command."""

import json
from pathlib import Path
from madilang.cli.logger import CLILogger
from madilang.compiler.parser import parse_madi
from madilang.compiler.analyzer import analyze_madi, AnalysisException


def cmd_check(args, logger: CLILogger) -> int:
    file_path = Path(args.file)
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return 1

    try:
        source = file_path.read_text(encoding="utf-8")
    except Exception as e:
        logger.error(f"Failed to read file: {e}")
        return 1

    logger.info("🔍 Analyzing...")
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
            logger.success("✅ Analysis passed")
            logger.info(f"   Entities: {report['entities']}")
            logger.info(f"   Intents: {report['intents']}")
        return 0
    except AnalysisException as e:
        report = {"success": False, "errors": [str(err) for err in e.errors], "warnings": []}
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            logger.error("❌ Analysis failed")
            for err in e.errors:
                logger.error(f"   {err}")
        return 1
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        return 1
