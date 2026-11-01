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

        try:
            from madilang.plugins.ethics_hook import evaluate_ethics
            ethics_report = evaluate_ethics(ast)
        except Exception as e:  # the ethics layer must never break a build
            ethics_report = {"error": str(e)}

        report = {
            "ethics": ethics_report,
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
            eth = report.get("ethics") or {}
            if "overall" in eth:
                verdict = "PASS" if eth["passed"] else "FAIL"
                logger.info(f"   Ethics: [{eth['bar']}] {eth['overall']:.2f} {verdict}")
                for f in eth.get("findings", [])[:5]:
                    logger.info(f"   - {f['severity']:<8} {f['message']}")
        ethics = report.get("ethics") or {}
        if ethics.get("overall") is not None and not ethics.get("passed", True):
            logger.error("\u274c Ethics gate failed \u2014 refusing to pass")
            return 1
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
