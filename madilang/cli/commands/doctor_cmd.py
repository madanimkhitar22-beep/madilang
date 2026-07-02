# ════════════════════════════════════════════════════════════════════════════
# 🩺 MadiLang CLI — Doctor Command (Purified v0.5.1)
# ════════════════════════════════════════════════════════════════════════════
# Comprehensive environment, secrets, and network health check.
# Status: CERTIFIED • Mobile-First • Smart Fallback Validation • Bug-Free
# ════════════════════════════════════════════════════════════════════════════

from madilang.cli.logger import CLILogger
from madilang.diagnostics import EnvironmentChecker, SecretsChecker, NetworkChecker


def run_doctor(logger: CLILogger) -> int:
    """
    Execute full system diagnostics.
    
    Returns:
        0 if all critical checks pass, 1 otherwise.
    """
    logger.info("🩺 Running MadiLang Sovereign Diagnostics...")
    logger.info("=" * 60)
    
    has_critical_failure = False
    has_warnings = False
    
    # ── 1. Environment Check ──────────────────────────────────────────────
    logger.info("\n🖥️  SYSTEM ENVIRONMENT")
    logger.info("-" * 40)
    env = EnvironmentChecker().check_all()
    
    for key in ["python", "nodejs", "npm"]:
        check = env[key]
        status = check["status"]
        version = check.get("version", "N/A")
        path = check.get("path", "Not found")
        logger.info(f"  {status} {key.capitalize():<8} v{version:<12} ({path})")
        if not check["ok"]:
            has_critical_failure = True
    
    perm = env["permissions"]
    logger.info(f"  {perm['status']} Write Access   {perm['cwd']}")
    if not perm["ok"]:
        has_critical_failure = True
    
    plat = env["platform"]
    mobile_tag = "📱 Mobile" if plat["is_mobile"] else "💻 Desktop"
    termux_tag = " (Termux)" if plat["is_termux"] else ""
    logger.info(f"  ℹ️ Platform      {plat['system']} {plat['machine']} {mobile_tag}{termux_tag}")
    
    # ── 2. Secrets Check ──────────────────────────────────────────────────
    logger.info("\n🔐 SOVEREIGN SECRETS")
    logger.info("-" * 40)
    secrets = SecretsChecker().check_all()
    
    for name, check in secrets["secrets"].items():
        status = check["status"]
        desc = check.get("description", "")
        
        if status == "⚠️" or check.get("warning"):
            has_warnings = True
            
        if check.get("optional"):
            logger.info(f"  {status} {name:<28} (optional)")
        else:
            detail = ""
            if check.get("masked"):
                detail = f" [{check['masked']}]"
            elif check.get("warning"):
                detail = f" ⚠️ {check['warning']}"
            logger.info(f"  {status} {name:<28}{detail}")
            
            if not check.get("valid", True) and not check.get("optional"):
                if check.get("critical", False) or status == "❌":
                    has_critical_failure = True
    
    # ── 3. Network Check ──────────────────────────────────────────────────
    logger.info("\n🌐 NETWORK CONNECTIVITY")
    logger.info("-" * 40)
    net = NetworkChecker().check_all()
    
    for name, check in net["endpoints"].items():
        status = check["status"]
        url = check["url"]
        logger.info(f"  {status} {name:<18} {url}")
        if status == "❌":
            has_warnings = True
    
    if not net["online"]:
        logger.warning("  ⚠️ No network connectivity detected. Auto-install will fail.")
        has_warnings = True
        
    if not net["all_reachable"]:
        has_warnings = True
    
    # ── Summary ───────────────────────────────────────────────────────────
    logger.info("\n" + "=" * 60)
    if has_critical_failure:
        logger.error("❌ DIAGNOSTICS FAILED — Fix critical issues above before proceeding.")
        return 1
    elif has_warnings:
        logger.success("✅ DIAGNOSTICS PASSED (with development warnings). Ready for local compilation! 🚀")
        return 0
    else:
        logger.success("✅ ALL CHECKS PASSED — Environment is 100% sovereign-ready! 🛡️")
        return 0
