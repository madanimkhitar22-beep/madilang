# ════════════════════════════════════════════════════════════════════════════
# 🩺 MadiLang CLI — Doctor Command (Sovereign Diagnostics)
# ════════════════════════════════════════════════════════════════════════════
# Comprehensive environment, secrets, and network health check.
# Status: v0.5.0 • Mobile-First • Zero-Config
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
                has_critical_failure = True
    
    # ── 3. Network Check ──────────────────────────────────────────────────
    logger.info("\n🌐 NETWORK CONNECTIVITY")
    logger.info("-" * 40)
    net = NetworkChecker().check_all()
    
    for name, check in net["endpoints"].items():
        status = check["status"]
        url = check["url"]
        logger.info(f"  {status} {name:<18} {url}")
    
    if not net["online"]:
        logger.warning("  ⚠️ No network connectivity detected. Auto-install will fail.")
    
    # ── Summary ───────────────────────────────────────────────────────────
    logger.info("\n" + "=" * 60)
    if has_critical_failure:
        logger.error("❌ DIAGNOSTICS FAILED — Fix critical issues above before proceeding.")
        return 1
    elif not net["all_reachable"]:
        logger.warning("⚠️ DIAGNOSTICS PASSED WITH WARNINGS — Network issues detected.")
        return 0
    else:
        logger.success("✅ ALL CHECKS PASSED — Environment is sovereign-ready!")
        return 0
