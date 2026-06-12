# ════════════════════════════════════════════════════════════════════════════
# 🧠 MadiLang — Ethics Hook Plugin
# ════════════════════════════════════════════════════════════════════════════
# Sovereign ethics validation plugin for MadiLang compilation pipeline.
# Integrates with Sovereign-Cognition-Engine for quantifiable ethics scoring.
# Status: v0.4.0 • Sovereign-by-Design • Ethics-by-Default
# ════════════════════════════════════════════════════════════════════════════

"""
MadiLang Ethics Hook Plugin

This plugin integrates ethical validation into the MadiLang compilation pipeline.
It analyzes intents and entities for ethical compliance, assigns scores, and
can block compilation if critical ethical violations are detected.

Features:
    • Quantifiable ethics scoring (0.0 to 1.0)
    • Detection of privacy, consent, and transparency issues
    • Integration with Sovereign-Cognition-Engine (optional)
    • Configurable thresholds and strictness
    • Audit logging for compliance tracking
    • Graceful degradation when ethics engine unavailable

Ethics Dimensions:
    • Privacy: Handling of sensitive data
    • Consent: Explicit user consent requirements
    • Transparency: Clear intent and data usage
    • Accountability: Audit trails and responsibility
    • Fairness: Non-discriminatory logic patterns

Design Principles:
    • Non-Blocking by Default: Warns without stopping unless configured
    • Quantifiable: Ethics as measurable scores, not vague statements
    • Extensible: Custom rules and dimensions can be added
    • Sovereign: Respects developer intent while enforcing boundaries
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto
import warnings
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

from madilang.ir.models import IRProgram, IRIntent, IREntity


# ────────────────────────────────────────────────────────────────────────────
# Ethics Enums and Constants
# ────────────────────────────────────────────────────────────────────────────

class EthicsDimension(Enum):
    """Ethical dimensions evaluated by the plugin."""
    PRIVACY = "privacy"
    CONSENT = "consent"
    TRANSPARENCY = "transparency"
    ACCOUNTABILITY = "accountability"
    FAIRNESS = "fairness"
    SECURITY = "security"


class EthicsSeverity(Enum):
    """Severity levels for ethics findings."""
    CRITICAL = auto()  # Blocks compilation
    HIGH = auto()      # Strong warning, may block
    MEDIUM = auto()    # Warning
    LOW = auto()       # Info/suggestion


# Default weights for ethics scoring
DEFAULT_WEIGHTS = {
    EthicsDimension.PRIVACY: 0.25,
    EthicsDimension.CONSENT: 0.20,
    EthicsDimension.TRANSPARENCY: 0.15,
    EthicsDimension.ACCOUNTABILITY: 0.15,
    EthicsDimension.FAIRNESS: 0.15,
    EthicsDimension.SECURITY: 0.10,
}

# Default threshold for passing
DEFAULT_THRESHOLD = 0.70


# ────────────────────────────────────────────────────────────────────────────# Ethics Finding
# ────────────────────────────────────────────────────────────────────────────

@dataclass
class EthicsFinding:
    """Represents an ethics validation finding."""
    dimension: EthicsDimension
    severity: EthicsSeverity
    message: str
    location: str = ""  # e.g., "intent:register_user", "entity:User.field:password"
    suggestion: Optional[str] = None
    score_impact: float = 0.0  # Negative impact on score
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "dimension": self.dimension.value,
            "severity": self.severity.name,
            "message": self.message,
            "location": self.location,
            "suggestion": self.suggestion,
            "score_impact": self.score_impact,
        }


# ────────────────────────────────────────────────────────────────────────────
# Ethics Score
# ────────────────────────────────────────────────────────────────────────────

@dataclass
class EthicsScore:
    """Comprehensive ethics scoring result."""
    overall: float = 1.0  # 0.0 to 1.0
    dimensions: Dict[EthicsDimension, float] = field(default_factory=dict)
    findings: List[EthicsFinding] = field(default_factory=list)
    passed: bool = True
    threshold: float = DEFAULT_THRESHOLD
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "overall": round(self.overall, 3),
            "passed": self.passed,
            "threshold": self.threshold,
            "dimensions": {d.value: round(s, 3) for d, s in self.dimensions.items()},
            "findings": [f.to_dict() for f in self.findings],
            "critical_count": sum(1 for f in self.findings if f.severity == EthicsSeverity.CRITICAL),
            "high_count": sum(1 for f in self.findings if f.severity == EthicsSeverity.HIGH),
        }
        def get_bar(self, width: int = 20) -> str:
        """Generate visual score bar."""
        filled = int(self.overall * width)
        return "█" * filled + "░" * (width - filled)


# ────────────────────────────────────────────────────────────────────────────
# Ethics Hook Plugin
# ────────────────────────────────────────────────────────────────────────────

class EthicsHookPlugin(BasePlugin):
    """
    Plugin for ethical validation of MadiLang programs.
    
    Analyzes AST and IR for ethical compliance, assigns scores,
    and can enforce thresholds.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        
        # Configuration
        self.threshold = self.get_config("threshold", DEFAULT_THRESHOLD)
        self.weights = self.get_config("weights", DEFAULT_WEIGHTS)
        self.strict_mode = self.get_config("strict_mode", False)
        self.block_on_critical = self.get_config("block_on_critical", True)
        self.block_on_threshold = self.get_config("block_on_threshold", False)
        self.enable_external_engine = self.get_config("enable_external_engine", False)
        
        # External ethics engine (Sovereign-Cognition-Engine)
        self._external_engine = None
        if self.enable_external_engine:
            self._init_external_engine()
        
        # Analysis state
        self._current_score: Optional[EthicsScore] = None
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="ethics-hook",
            version="0.4.0",
            description="Sovereign ethics validation with quantifiable scoring",
            author="El Madani El Mkhitar",
            hooks=[
                PluginHook.POST_PARSE,
                PluginHook.POST_ANALYSIS,
                PluginHook.PRE_SIGN,
            ],
            priority=PluginPriority.CRITICAL,            ethics_related=True,
            security_related=True,
            audit_required=True,
            enabled_by_default=True,
        )
    
    def _init_external_engine(self):
        """Initialize external ethics engine if available."""
        try:
            # Attempt to import Sovereign-Cognition-Engine
            from sovereign_cognition import EthicsEngine
            self._external_engine = EthicsEngine()
            self.log("Sovereign-Cognition-Engine integrated successfully")
        except ImportError:
            warnings.warn(
                "Sovereign-Cognition-Engine not available. "
                "Using built-in ethics validation only.",
                UserWarning
            )
            self._external_engine = None
    
    # ────────────────────────────────────────────────────────────────────────
    # Hook Implementations
    # ────────────────────────────────────────────────────────────────────────
    
    def post_parse(self, context: PluginContext) -> Optional[ProgramNode]:
        """
        Hook: After parsing, perform initial ethics scan.
        
        Analyzes AST structure for ethical patterns.
        """
        if not context.ast:
            return None
        
        self.log("Running ethics analysis on AST...")
        
        try:
            score = self._analyze_ast(context.ast)
            self._current_score = score
            
            # Store score in context for other plugins
            context.set_shared("ethics_score", score.to_dict())
            
            # Report findings
            self._report_findings(score, context)
            
            # Check for critical violations
            if self.block_on_critical:
                critical_findings = [
                    f for f in score.findings                     if f.severity == EthicsSeverity.CRITICAL
                ]
                if critical_findings:
                    context.stop(
                        f"Ethics validation failed: {len(critical_findings)} critical finding(s)"
                    )
                    return None
            
            # Enrich AST with ethics metadata
            self._enrich_ast(context.ast, score)
            
            return context.ast
            
        except Exception as e:
            context.add_error(f"Ethics plugin error: {e}", self.name)
            return None
    
    def post_analysis(self, context: PluginContext) -> Optional[ProgramNode]:
        """
        Hook: After semantic analysis, refine ethics score.
        
        Uses enriched AST for more accurate scoring.
        """
        if not context.ast or not self._current_score:
            return None
        
        # Refine score based on analysis results
        refined_score = self._refine_score(context.ast, self._current_score)
        self._current_score = refined_score
        
        # Update shared score
        context.set_shared("ethics_score", refined_score.to_dict())
        
        return None
    
    def pre_sign(self, context: PluginContext) -> Dict[str, Any]:
        """
        Hook: Before signature, add ethics metadata.
        
        Returns ethics data for inclusion in signature.
        """
        if not self._current_score:
            return {}
        
        return {
            "score": self._current_score.overall,
            "passed": self._current_score.passed,
            "threshold": self.threshold,
            "dimensions": {
                d.value: s for d, s in self._current_score.dimensions.items()            },
            "findings_count": len(self._current_score.findings),
        }
    
    # ────────────────────────────────────────────────────────────────────────
    # AST Analysis
    # ────────────────────────────────────────────────────────────────────────
    
    def _analyze_ast(self, program: ProgramNode) -> EthicsScore:
        """
        Analyze AST for ethical compliance.
        
        Returns comprehensive ethics score.
        """
        findings: List[EthicsFinding] = []
        dimension_scores: Dict[EthicsDimension, float] = {
            d: 1.0 for d in EthicsDimension
        }
        
        # Analyze entities
        for entity in program.entities:
            entity_findings = self._analyze_entity(entity)
            findings.extend(entity_findings)
        
        # Analyze intents
        for intent in program.intents:
            intent_findings = self._analyze_intent(intent)
            findings.extend(intent_findings)
        
        # Calculate dimension scores from findings
        for finding in findings:
            dim = finding.dimension
            impact = finding.score_impact
            dimension_scores[dim] = max(0.0, dimension_scores[dim] - impact)
        
        # Calculate overall score
        overall = sum(
            dimension_scores[d] * self.weights.get(d, 0)
            for d in EthicsDimension
        )
        
        # Determine pass/fail
        passed = overall >= self.threshold
        
        # Check for critical findings
        if any(f.severity == EthicsSeverity.CRITICAL for f in findings):
            passed = False
        
        return EthicsScore(
            overall=overall,            dimensions=dimension_scores,
            findings=findings,
            passed=passed,
            threshold=self.threshold,
        )
    
    def _analyze_entity(self, entity: EntityNode) -> List[EthicsFinding]:
        """Analyze entity for ethical issues."""
        findings = []
        loc = f"entity:{entity.name}"
        
        # Check for secure fields
        has_secure = any(f.is_secure for f in entity.fields)
        
        if has_secure:
            # Good: Entity has secure fields marked
            pass
        else:
            # Check if entity likely contains sensitive data
            sensitive_names = {"password", "secret", "token", "key", "ssn", "credit"}
            for field in entity.fields:
                if any(s in field.name.lower() for s in sensitive_names):
                    findings.append(EthicsFinding(
                        dimension=EthicsDimension.SECURITY,
                        severity=EthicsSeverity.HIGH,
                        message=f"Field '{field.name}' appears sensitive but not marked as secure",
                        location=f"{loc}.field:{field.name}",
                        suggestion="Add (secure) modifier to sensitive fields",
                        score_impact=0.15,
                    ))
        
        # Check for audit fields
        has_audit = any("audit" in f.name.lower() for f in entity.fields)
        has_timestamps = any(
            f.name.lower() in ("createdat", "updatedat", "created_at", "updated_at")
            for f in entity.fields
        )
        
        if not has_audit and not has_timestamps:
            findings.append(EthicsFinding(
                dimension=EthicsDimension.ACCOUNTABILITY,
                severity=EthicsSeverity.MEDIUM,
                message="Entity lacks audit trail fields",
                location=loc,
                suggestion="Add createdAt/updatedAt fields for accountability",
                score_impact=0.05,
            ))
        
        return findings
        def _analyze_intent(self, intent: IntentNode) -> List[EthicsFinding]:
        """Analyze intent for ethical issues."""
        findings = []
        loc = f"intent:{intent.name}"
        
        # Check for authentication on sensitive operations
        sensitive_routes = {"/api/register", "/api/login", "/api/user", "/api/profile"}
        if intent.route in sensitive_routes and not intent.requires_auth:
            # Registration may not require auth, but login should return token
            if "login" in intent.name.lower() or "profile" in intent.name.lower():
                findings.append(EthicsFinding(
                    dimension=EthicsDimension.SECURITY,
                    severity=EthicsSeverity.HIGH,
                    message="Sensitive route without authentication",
                    location=loc,
                    suggestion="Add 'protect route' or 'auth required' step",
                    score_impact=0.20,
                ))
        
        # Check for consent on data collection
        has_create = any(s.step_type == StepType.CREATE for s in intent.steps)
        if has_create and "consent" not in intent.name.lower():
            # Check if consent is mentioned in steps
            has_consent_check = any(
                "consent" in str(s.args).lower()
                for s in intent.steps
            )
            if not has_consent_check:
                findings.append(EthicsFinding(
                    dimension=EthicsDimension.CONSENT,
                    severity=EthicsSeverity.MEDIUM,
                    message="Data creation without explicit consent verification",
                    location=loc,
                    suggestion="Add consent check step or include consent in inputs",
                    score_impact=0.10,
                ))
        
        # Check for error handling
        has_error_handling = any(
            s.step_type in (StepType.RETURN_ERROR, StepType.IF_EXISTS, StepType.IF_NOT_FOUND)
            for s in intent.steps
        )
        if not has_error_handling:
            findings.append(EthicsFinding(
                dimension=EthicsDimension.TRANSPARENCY,
                severity=EthicsSeverity.LOW,
                message="Intent lacks explicit error handling",
                location=loc,
                suggestion="Add error handling steps for better transparency",
                score_impact=0.05,            ))
        
        # Check for role-based access on admin operations
        admin_keywords = {"admin", "delete", "remove", "ban", "suspend"}
        if any(k in intent.name.lower() for k in admin_keywords):
            if not intent.required_roles:
                findings.append(EthicsFinding(
                    dimension=EthicsDimension.SECURITY,
                    severity=EthicsSeverity.CRITICAL,
                    message="Admin operation without role restriction",
                    location=loc,
                    suggestion="Add 'allow only admin' or role guard step",
                    score_impact=0.30,
                ))
        
        return findings
    
    # ────────────────────────────────────────────────────────────────────────
    # Score Refinement
    # ────────────────────────────────────────────────────────────────────────
    
    def _refine_score(
        self,
        program: ProgramNode,
        score: EthicsScore
    ) -> EthicsScore:
        """
        Refine ethics score after semantic analysis.
        
        Uses enriched AST for more accurate assessment.
        """
        # If external engine available, use it for refinement
        if self._external_engine:
            try:
                external_result = self._external_engine.evaluate(program)
                if external_result:
                    # Merge external score
                    score.overall = external_result.get("score", score.overall)
                    score.passed = external_result.get("passed", score.passed)
                    
                    # Add external findings
                    for ext_finding in external_result.get("findings", []):
                        score.findings.append(EthicsFinding(
                            dimension=EthicsDimension(ext_finding.get("dimension", "transparency")),
                            severity=EthicsSeverity[ext_finding.get("severity", "MEDIUM")],
                            message=ext_finding.get("message", ""),
                            location=ext_finding.get("location", ""),
                            suggestion=ext_finding.get("suggestion"),
                            score_impact=ext_finding.get("impact", 0.0),
                        ))                    
            except Exception as e:
                self.log(f"External engine refinement failed: {e}", "warning")
        
        return score
    
    # ────────────────────────────────────────────────────────────────────────
    # Reporting and Enrichment
    # ────────────────────────────────────────────────────────────────────────
    
    def _report_findings(self, score: EthicsScore, context: PluginContext):
        """Report ethics findings to context."""
        for finding in score.findings:
            if finding.severity == EthicsSeverity.CRITICAL:
                context.add_error(
                    f"[ETHICS:{finding.dimension.value}] {finding.message}",
                    self.name
                )
            elif finding.severity == EthicsSeverity.HIGH:
                if self.strict_mode:
                    context.add_error(
                        f"[ETHICS:{finding.dimension.value}] {finding.message}",
                        self.name
                    )
                else:
                    context.add_warning(
                        f"[ETHICS:{finding.dimension.value}] {finding.message}",
                        self.name
                    )
            elif finding.severity == EthicsSeverity.MEDIUM:
                context.add_warning(
                    f"[ETHICS:{finding.dimension.value}] {finding.message}",
                    self.name
                )
            else:
                # LOW severity - log only
                self.log(f"[INFO] {finding.message}")
        
        # Report overall score
        bar = score.get_bar(10)
        status = "✅ PASS" if score.passed else "❌ FAIL"
        self.log(f"Ethics Score: [{bar}] {score.overall:.2f} {status}")
    
    def _enrich_ast(self, program: ProgramNode, score: EthicsScore):
        """Enrich AST with ethics metadata."""
        # Add score to program metadata
        program.add_metadata("ethics_score", score.overall)
        program.add_metadata("ethics_passed", score.passed)
        program.add_metadata("ethics_threshold", self.threshold)
                # Add dimension scores
        for dim, dim_score in score.dimensions.items():
            program.add_metadata(f"ethics_{dim.value}", dim_score)
        
        # Add findings count
        program.add_metadata("ethics_findings", len(score.findings))
