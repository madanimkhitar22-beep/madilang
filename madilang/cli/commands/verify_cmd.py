"""MadiLang CLI — verify command."""

import json
import re
from pathlib import Path
from madilang.cli.logger import CLILogger


def cmd_verify(args, logger: CLILogger) -> int:
    file_path = Path(args.file)
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return 1

    logger.info(f"🔍 Verifying {file_path}")
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
                logger.error("No sovereign signature found in file")
                return 1
        else:
            signature = json.loads(sig_match.group(1))

        logger.info(f"👤 Developer: {signature.get('developer', {}).get('id')}")
        logger.info(f"📅 Generated: {signature.get('timestamp', {}).get('iso')}")
        logger.info(f"🔖 Intent Hash: {signature.get('intent', {}).get('hash', '')[:32]}...")

        if signature.get('ethics'):
            score = signature['ethics'].get('score')
            if score is not None:
                logger.info(f"🛡️ Ethics Score: {score:.2f}")

        logger.success("✅ Signature structure valid")
        return 0
    except Exception as e:
        logger.error(f"Verification failed: {e}")
        return 1
