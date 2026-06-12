# ════════════════════════════════════════════════════════════════════════════
# 🧠 MadiLang — Security Hook Plugin (Refined)
# ════════════════════════════════════════════════════════════════════════════
# Sovereign security validation plugin for MadiLang compilation pipeline.
# Detects vulnerabilities, enforces secure patterns, and integrates with scanners.
# Status: v0.4.0 • Sovereign-by-Design • Security-by-Default
# ════════════════════════════════════════════════════════════════════════════

"""
MadiLang Security Hook Plugin

This plugin integrates security validation into the MadiLang compilation pipeline.
It analyzes intents, entities, and generated code for security vulnerabilities.
"""

from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto
import warnings
import re
import json

from madilang.plugins.base_plugin import (
    BasePlugin,
    PluginMetadata,
    PluginHook,
    PluginPriority,
    PluginContext,
)

from madilang.compiler.ast_nodes import (
    ProgramNode,
    EntityNode,
    FieldNode,
    IntentNode,
    StepNode,
    StepType,
)

from madilang.ir.models import (
    IRProgram,
    IRIntent,
    IREntity,
    IRInstruction,
    IRCreateInstruction,
    IRUpdateInstruction,
    IRFindInstruction,
    IRVerifyPasswordInstruction,
    IRGenerateTokenInstruction,
)


# ────────────────────────────────────────────────────────────────────────────
# Security Enums
# ────────────────────────────────────────────────────────────────────────────

class SecurityCategory(Enum):
    """Categories of security checks."""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_PROTECTION = "data_protection"
    INPUT_VALIDATION = "input_validation"
    ERROR_HANDLING = "error_handling"
    CRYPTOGRAPHY = "cryptography"
    RATE_LIMITING = "rate_limiting"


class SecuritySeverity(Enum):
    """Severity levels for security findings."""
    CRITICAL = auto()  # Blocks compilation
    HIGH = auto()      # Strong warning, may block
    MEDIUM = auto()    # Warning
    LOW = auto()       # Info/suggestion


# ────────────────────────────────────────────────────────────────────────────
# Security Finding
# ────────────────────────────────────────────────────────────────────────────

@dataclass
class SecurityFinding:
    """Represents a security validation finding."""
    category: SecurityCategory
    severity: SecuritySeverity
    rule_id: str
    message: str
    location: str = ""
    suggestion: Optional[str] = None
    cwe_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "rule_id": self.rule_id,
            "category": self.category.value,
            "severity": self.severity.name,
            "message": self.message,
            "location": self.location,
        }
        if self.suggestion:
            result["suggestion"] = self.suggestion
        if self.cwe_id:
            result["cwe_id"] = self.cwe_id
        return result


# ────────────────────────────────────────────────────────────────────────────
# Security Report
# ────────────────────────────────────────────────────────────────────────────

@dataclass
class SecurityReport:
    """Comprehensive security analysis report."""
    passed: bool = True
    findings: List[SecurityFinding] = field(default_factory=list)
    secure_fields_verified: bool = False
    auth_coverage: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "findings_count": len(self.findings),
            "critical_count": sum(1 for f in self.findings if f.severity == SecuritySeverity.CRITICAL),
            "high_count": sum(1 for f in self.findings if f.severity == SecuritySeverity.HIGH),
            "secure_fields_verified": self.secure_fields_verified,
            "auth_coverage": round(self.auth_coverage, 2),
            "findings": [f.to_dict() for f in self.findings],
        }


# ────────────────────────────────────────────────────────────────────────────
# Security Hook Plugin
# ────────────────────────────────────────────────────────────────────────────

class SecurityHookPlugin(BasePlugin):
    """Plugin for security validation of MadiLang programs."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        
        # Configuration
        self.block_on_critical = self.get_config("block_on_critical", True)
        self.block_on_high = self.get_config("block_on_high", False)
        self.strict_mode = self.get_config("strict_mode", False)
        self.enable_external_scanner = self.get_config("enable_external_scanner", False)
        self.require_secure_fields = self.get_config("require_secure_fields", True)
        self.min_auth_coverage = self.get_config("min_auth_coverage", 0.9)
        
        # External scanner (Sovereign-DevKit)
        self._external_scanner = None
        if self.enable_external_scanner:
            self._init_external_scanner()
        
        # Analysis state
        self._current_report: Optional[SecurityReport] = None
        self._secure_fields: Set[str] = set()
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="security-hook",
            version="0.4.0",
            description="Sovereign security validation with vulnerability detection",
            author="El Madani El Mkhitar",
            hooks=[
                PluginHook.POST_PARSE,
                PluginHook.POST_COMPILE,
                PluginHook.POST_GENERATE,
                PluginHook.PRE_SIGN,
            ],
            priority=PluginPriority.CRITICAL,
            ethics_related=False,
            security_related=True,
            audit_required=True,
            enabled_by_default=True,
            requires=["ethics-hook"],
        )
    
    def _init_external_scanner(self):
        try:
            from sovereign_devkit import SecurityScanner
            self._external_scanner = SecurityScanner()
            self.log("Sovereign-DevKit scanner integrated successfully")
        except Exception as e:
            warnings.warn(
                f"Sovereign-DevKit scanner integration initialization failed: {e}. "
                "Falling back to built-in compiler security validation rules.",
                UserWarning
            )
            self._external_scanner = None
    
    # ────────────────────────────────────────────────────────────────────────
    # Hook Implementations
    # ────────────────────────────────────────────────────────────────────────
    
    def post_parse(self, context: PluginContext) -> Optional[ProgramNode]:
        if not context.ast:
            return None
        
        self.log("Running security analysis on AST...")
        try:
            report = self._analyze_ast(context.ast)
            self._current_report = report
            
            context.set_shared("security_report", report.to_dict())
            self._report_findings(report, context)
            
            if self.block_on_critical:
                critical = [f for f in report.findings if f.severity == SecuritySeverity.CRITICAL]
                if critical:
                    context.stop(f"Security validation stopped pipeline: {len(critical)} critical vulnerability detected.")
                    return None
            
            if self.block_on_high:
                high = [f for f in report.findings if f.severity == SecuritySeverity.HIGH]
                if high:
                    context.stop(f"Security validation stopped pipeline: {len(high)} high-severity vulnerability detected.")
                    return None
            
            return context.ast
            
        except Exception as e:
            context.add_error(f"Security plugin analysis crash on AST pipeline: {e}", self.name)
            return None
    
    def post_compile(self, context: PluginContext) -> Optional[IRProgram]:
        if not context.ir:
            return None
        
        self.log("Verifying security patterns in IR layer...")
        try:
            ir_findings = self._analyze_ir(context.ir)
            if ir_findings:
                if self._current_report:
                    self._current_report.findings.extend(ir_findings)
                    self._current_report.passed = (
                        self._current_report.passed and
                        not any(f.severity == SecuritySeverity.CRITICAL for f in ir_findings)
                    )
                
                for finding in ir_findings:
                    if finding.severity == SecuritySeverity.CRITICAL:
                        context.add_error(f"[SEC:{finding.rule_id}] {finding.message}", self.name)
                        if self.block_on_critical:
                            context.stop(f"Security pipeline terminated due to critical IR-level structural risk.")
                    else:
                        context.add_warning(f"[SEC:{finding.rule_id}] {finding.message}", self.name)
            
            return context.ir
            
        except Exception as e:
            context.add_error(f"Security IR analysis engine collapsed: {e}", self.name)
            return None
    
    def post_generate(self, context: PluginContext) -> Optional[str]:
        if not context.generated_code:
            return None
        
        self.log("Scanning raw compiled target code outputs...")
        try:
            if self._external_scanner:
                scan_result = self._external_scanner.scan(context.generated_code)
                
                if scan_result.get("critical_issues"):
                    for issue in scan_result["critical_issues"]:
                        context.add_error(f"[SCANNER-CRITICAL] {issue.get('message', 'Unresolved structural risk')}", self.name)
                    if self.block_on_critical:
                        context.stop("Sovereign-DevKit external security engine triggered an absolute compilation abort.")
                        return None
                
                if scan_result.get("warnings"):
                    for warning in scan_result["warnings"]:
                        context.add_warning(f"[SCANNER-WARN] {warning.get('message', 'Risk suggestion')}", self.name)
            
            return context.generated_code
            
        except Exception as e:
            # ✅ Fixed: Prevent bypasses via forced external engine exceptions in strict mode
            error_msg = f"External security verification engine tracking collapsed: {e}"
            if self.strict_mode or self.block_on_critical:
                context.add_error(error_msg, self.name)
                context.stop("Security compilation halted: External scanner failure under strict fail-secure mode.")
                return None
            else:
                context.add_warning(error_msg, self.name)
                return context.generated_code
    
    def pre_sign(self, context: PluginContext) -> Dict[str, Any]:
        if not self._current_report:
            return {}
        return {
            "passed": self._current_report.passed,
            "findings_count": len(self._current_report.findings),
            "critical_count": sum(1 for f in self._current_report.findings if f.severity == SecuritySeverity.CRITICAL),
            "secure_fields_verified": self._current_report.secure_fields_verified,
            "auth_coverage": self._current_report.auth_coverage,
        }
    
    # ────────────────────────────────────────────────────────────────────────
    # AST Analysis
    # ────────────────────────────────────────────────────────────────────────
    
    def _analyze_ast(self, program: ProgramNode) -> SecurityReport:
        """Analyze AST for secure routing patterns and field protection rules."""
        findings: List[SecurityFinding] = []
        self._secure_fields = set()
        
        for entity in program.entities:
            for field in entity.fields:
                if field.is_secure:
                    self._secure_fields.add(f"{entity.name}.{field.name}")
        
        for entity in program.entities:
            findings.extend(self._analyze_entity(entity))
        
        auth_count = 0
        sensitive_count = 0
        
        for intent in program.intents:
            # ✅ Fixed: Protect against missing or uninitialized routes via getattr boundary check
            route = getattr(intent, "route", "") or ""
            findings.extend(self._analyze_intent(intent))
            
            if self._is_sensitive_route(route):
                sensitive_count += 1
                if getattr(intent, "requires_auth", False):
                    auth_count += 1
        
        auth_coverage = auth_count / sensitive_count if sensitive_count > 0 else 1.0
        
        if sensitive_count == 0:
            findings.append(SecurityFinding(
                category=SecurityCategory.RATE_LIMITING,
                severity=SecuritySeverity.LOW,
                rule_id="SEC-099",
                message="Zero sensitive web API exposure boundaries found within compiled codebase context.",
                location="program",
                suggestion="Verify that routing parameters are correctly registered if exposure was intended."
            ))
        elif auth_coverage < self.min_auth_coverage:
            findings.append(SecurityFinding(
                category=SecurityCategory.AUTHENTICATION,
                severity=SecuritySeverity.HIGH,
                rule_id="SEC-010",
                message=f"Authentication coverage below target margin ({auth_coverage:.0%} < {self.min_auth_coverage:.0%})",
                location="program",
                suggestion="Enforce 'protect route' across newly registered intent handlers.",
                cwe_id="CWE-306",
            ))
        
        passed = not any(
            f.severity in (SecuritySeverity.CRITICAL, SecuritySeverity.HIGH)
            for f in findings
        )
        return SecurityReport(
            passed=passed,
            findings=findings,
            secure_fields_verified=len(self._secure_fields) > 0,
            auth_coverage=auth_coverage,
        )
    
    def _analyze_entity(self, entity: EntityNode) -> List[SecurityFinding]:
        findings = []
        loc = f"entity:{entity.name}"
        sensitive_patterns = [
            r"password", r"secret", r"token", r"key", r"api_key",
            r"ssn", r"credit_card", r"cvv", r"pin"
        ]
        
        for field in entity.fields:
            field_loc = f"{loc}.field:{field.name}"
            is_sensitive = any(re.search(p, field.name.lower()) for p in sensitive_patterns)
            
            if is_sensitive and not field.is_secure:
                findings.append(SecurityFinding(
                    category=SecurityCategory.DATA_PROTECTION,
                    severity=SecuritySeverity.HIGH,
                    rule_id="SEC-001",
                    message=f"Sensitive database data field attribute '{field.name}' lacks secure tag execution.",
                    location=field_loc,
                    suggestion="Add the (secure) decorator tag attribute to automatically inject cryptographical layers.",
                    cwe_id="CWE-312",
                ))
            
            if "password" in field.name.lower() and field.type != "string":
                findings.append(SecurityFinding(
                    category=SecurityCategory.CRYPTOGRAPHY,
                    severity=SecuritySeverity.MEDIUM,
                    rule_id="SEC-002",
                    message="Password metadata mapping must be represented explicitly as a string layer.",
                    location=field_loc,
                    suggestion="Re-assign raw type to standard string primitives to prevent digest derivation issues.",
                    cwe_id="CWE-257",
                ))
        return findings
    
    def _analyze_intent(self, intent: IntentNode) -> List[SecurityFinding]:
        findings = []
        loc = f"intent:{intent.name}"
        route = getattr(intent, "route", "") or ""
        
        if self._is_sensitive_route(route) and not getattr(intent, "requires_auth", False):
            if not any(k in intent.name.lower() for k in ("register", "signup")):
                findings.append(SecurityFinding(
                    category=SecurityCategory.AUTHENTICATION,
                    severity=SecuritySeverity.CRITICAL,
                    rule_id="SEC-003",
                    message=f"Critical sensitive transaction gateway exposing route '{route}' without active authentication layer.",
                    location=loc,
                    suggestion="Prepend 'protect route' or assign direct role authentication bounds.",
                    cwe_id="CWE-306",
                ))
        
        admin_keywords = {"admin", "delete", "remove", "ban", "suspend", "deactivate"}
        if any(k in intent.name.lower() for k in admin_keywords):
            if not getattr(intent, "required_roles", None):
                findings.append(SecurityFinding(
                    category=SecurityCategory.AUTHORIZATION,
                    severity=SecuritySeverity.CRITICAL,
                    rule_id="SEC-004",
                    message="Administrative database operational payload missing access token validation role guards.",
                    location=loc,
                    suggestion="Inject an 'allow only admin' contextual step constraint inside execution sequences.",
                    cwe_id="CWE-862",
                ))
        
        for step in intent.steps:
            findings.extend(self._analyze_step(step, intent, loc))
        
        for step in [s for s in intent.steps if s.step_type == StepType.RETURN_ERROR]:
            msg = step.args.get("message", "") if isinstance(step.args, dict) else str(step.args)
            if self._contains_sensitive_pattern(msg):
                findings.append(SecurityFinding(
                    category=SecurityCategory.ERROR_HANDLING,
                    severity=SecuritySeverity.MEDIUM,
                    rule_id="SEC-005",
                    message="Error diagnostic return payload contains trace patterns susceptible to telemetry leak vectors.",
                    location=f"{loc}.step:error",
                    suggestion="Sanitize errors; replace specific technical outputs with generic safe error responses.",
                    cwe_id="CWE-209",
                ))
        
        if any(k in intent.name.lower() for k in ("login", "auth")):
            if not any(s.step_type == StepType.PASSWORD_CHECK for s in intent.steps):
                findings.append(SecurityFinding(
                    category=SecurityCategory.AUTHENTICATION,
                    severity=SecuritySeverity.HIGH,
                    rule_id="SEC-006",
                    message="Authentication gateway endpoint processing validation without executing cross-match checks.",
                    location=loc,
                    suggestion="Add explicit password check step execution bounds.",
                    cwe_id="CWE-287",
                ))
        
        return findings
    
    def _analyze_step(self, step: StepNode, intent: IntentNode, intent_loc: str) -> List[SecurityFinding]:
        findings = []
        loc = f"{intent_loc}.step:{step.step_type.name}"
        
        if step.step_type == StepType.FIND:
            field_arg = step.args.get("field", "") if isinstance(step.args, dict) else ""
            if "password" in field_arg.lower():
                findings.append(SecurityFinding(
                    category=SecurityCategory.DATA_PROTECTION,
                    severity=SecuritySeverity.HIGH,
                    rule_id="SEC-007",
                    message="Querying database lookup execution contexts directly utilizing raw password strings is strictly forbidden.",
                    location=loc,
                    suggestion="Lookup accounts strictly using unique safe keys (e.g., email), then compute cryptographical matches separately.",
                    cwe_id="CWE-312",
                ))
        return findings
    
    # ────────────────────────────────────────────────────────────────────────
    # IR Analysis
    # ────────────────────────────────────────────────────────────────────────
    
    def _analyze_ir(self, ir_program: IRProgram) -> List[SecurityFinding]:
        """
        Verify security pattern preservation at the IR instruction layer.
        """
        findings = []
        for intent in ir_program.intents.values():
            loc = f"ir:intent:{intent.name}"
            
            # ✅ Fixed: Active active taint analysis checks on raw payloads inside IR generation
            for instr in intent.body.instructions:
                if isinstance(instr, (IRCreateInstruction, IRUpdateInstruction)):
                    entity = instr.entity
                    for field_name, value_node in instr.data.items():
                        if f"{entity}.{field_name}" in self._secure_fields:
                            # Verify if value tracking does not explicitly call hashing primitives
                            val_str = str(value_node).lower()
                            if not any(h in val_str for h in ("hash", "encrypt", "crypto", "pbkdf2", "argon2")):
                                findings.append(SecurityFinding(
                                    category=SecurityCategory.CRYPTOGRAPHY,
                                    severity=SecuritySeverity.CRITICAL,
                                    rule_id="SEC-020",
                                    message=f"IR Leak: Secure marked field data mapping '{entity}.{field_name}' injected into IR database write operation without digest pipeline calls.",
                                    location=loc,
                                    suggestion="Enforce immediate IR emitter protection layers to enforce field processing bounds before database serialization.",
                                    cwe_id="CWE-319",
                                ))
        return findings
    
    # ────────────────────────────────────────────────────────────────────────
    # Helper Methods
    # ────────────────────────────────────────────────────────────────────────
    
    def _is_sensitive_route(self, route: str) -> bool:
        if not route: return False
        sensitive_patterns = [
            r"/api/user", r"/api/profile", r"/api/account",
            r"/api/admin", r"/api/settings", r"/api/data",
            r"/api/private", r"/api/secure"
        ]
        return any(re.search(p, route.lower()) for p in sensitive_patterns)
    
    def _contains_sensitive_pattern(self, text: str) -> bool:
        if not text: return False
        sensitive_patterns = [
            r"password", r"secret", r"token", r"key",
            r"database", r"query", r"stack", r"trace"
        ]
        return any(re.search(p, text.lower()) for p in sensitive_patterns)
    
    def _report_findings(self, report: SecurityReport, context: PluginContext):
        for finding in report.findings:
            prefix = f"[SEC:{finding.rule_id}]"
            if finding.severity == SecuritySeverity.CRITICAL:
                context.add_error(f"{prefix} {finding.message}", self.name)
            elif finding.severity == SecuritySeverity.HIGH:
                if self.strict_mode:
                    context.add_error(f"{prefix} {finding.message}", self.name)
                else:
                    context.add_warning(f"{prefix} {finding.message}", self.name)
            elif finding.severity == SecuritySeverity.MEDIUM:
                context.add_warning(f"{prefix} {finding.message}", self.name)
            else:
                self.log(f"[INFO] {prefix} {finding.message}")
        
        if report.passed:
            self.log(f"✅ Security verification completed successfully. ({len(report.findings)} findings logged)")
        else:
            critical = sum(1 for f in report.findings if f.severity == SecuritySeverity.CRITICAL)
            high = sum(1 for f in report.findings if f.severity == SecuritySeverity.HIGH)
            self.log(f"❌ Security structural assertion failed: {critical} critical, {high} high vulnerabilities found.")
