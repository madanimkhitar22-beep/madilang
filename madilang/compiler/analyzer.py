# ════════════════════════════════════════════════════════════════════════════
# 🧠 MadiLang — Semantic Analyzer (Refined)
# ════════════════════════════════════════════════════════════════════════════
# Validates AST for semantic correctness and enriches with derived information.
# Status: v0.4.0 • Sovereign-by-Design • Mobile-First
# ════════════════════════════════════════════════════════════════════════════

"""
MadiLang Semantic Analyzer

This module performs semantic analysis on the AST produced by the parser.
It validates correctness, resolves references, and enriches nodes with
derived information needed for IR compilation and code generation.
"""

from typing import List, Dict, Set, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timezone

from madilang.compiler.ast_nodes import (
    ProgramNode,
    EntityNode,
    FieldNode,
    IntentNode,
    StepNode,
    StepType,
    ASTNode,
    ASTVisitor,
)


# ────────────────────────────────────────────────────────────────────────────
# Analysis Errors
# ────────────────────────────────────────────────────────────────────────────

@dataclass
class AnalysisError:
    """Represents a semantic analysis error."""
    message: str
    line: Optional[int] = None
    column: Optional[int] = None
    severity: str = "error"  # error, warning, info
    
    def __str__(self) -> str:
        loc = f" at line {self.line}" if self.line else ""
        return f"[{self.severity.upper()}]{loc}: {self.message}"


class AnalysisException(Exception):
    """Exception raised when analysis fails with errors."""
    def __init__(self, errors: List[AnalysisError]):
        self.errors = errors
        messages = "\n".join(str(e) for e in errors)
        super().__init__(f"Analysis failed with {len(errors)} error(s):\n{messages}")


# ────────────────────────────────────────────────────────────────────────────
# Analysis Context
# ────────────────────────────────────────────────────────────────────────────

@dataclass
class AnalysisContext:
    """Holds state during semantic analysis tracking entities, intents, and variables."""
    errors: List[AnalysisError] = field(default_factory=list)
    warnings: List[AnalysisError] = field(default_factory=list)
    
    entities: Dict[str, EntityNode] = field(default_factory=dict)
    intents: Dict[str, IntentNode] = field(default_factory=dict)
    
    current_entity: Optional[str] = None
    current_intent: Optional[str] = None
    defined_variables: Set[str] = field(default_factory=set)
    
    supported_types: Set[str] = field(default_factory=lambda: {
        "string", "int", "float", "boolean", "datetime", "json"
    })
    
    def add_error(self, message: str, node: Optional[ASTNode] = None, severity: str = "error"):
        """Add an analysis error or warning cleanly to its designated stack."""
        error = AnalysisError(
            message=message,
            line=node.line if node else None,
            column=node.column if node else None,
            severity=severity
        )
        if severity == "error":
            self.errors.append(error)
        else:
            self.warnings.append(error)
    
    def register_entity(self, entity: EntityNode):
        if entity.name in self.entities:
            self.add_error(f"Duplicate entity definition: '{entity.name}'", entity, "error")
        else:
            self.entities[entity.name] = entity
    
    def register_intent(self, intent: IntentNode):
        if intent.name in self.intents:
            self.add_error(f"Duplicate intent definition: '{intent.name}'", intent, "error")
        else:
            self.intents[intent.name] = intent
    
    def has_errors(self) -> bool:
        return len(self.errors) > 0
    
    def raise_if_errors(self):
        if self.has_errors():
            raise AnalysisException(self.errors)


# ────────────────────────────────────────────────────────────────────────────
# Semantic Analyzer
# ────────────────────────────────────────────────────────────────────────────

class SemanticAnalyzer(ASTVisitor):
    """Performs semantic analysis on MadiLang AST validating logic constraints."""
    
    def __init__(self, context: Optional[AnalysisContext] = None):
        self.context = context or AnalysisContext()
    
    def analyze(self, program: ProgramNode) -> ProgramNode:
        # Phase 1: Build symbol tables
        self._build_symbol_tables(program)
        
        # Phase 2: Validate entities
        for entity in program.entities:
            self.visit_entitynode(entity)
        
        # Phase 3: Validate intents
        for intent in program.intents:
            self.visit_intentnode(intent)
        
        # Phase 4: Enforce error ceilings
        self.context.raise_if_errors()
        
        # Phase 5: Inject sovereignty metadata
        self._inject_sovereignty_metadata(program)
        
        return program
    
    def _build_symbol_tables(self, program: ProgramNode):
        for entity in program.entities:
            self.context.register_entity(entity)
        for intent in program.intents:
            self.context.register_intent(intent)
    
    def _inject_sovereignty_metadata(self, program: ProgramNode):
        for intent in program.intents:
            entity = self.context.entities.get(intent.entity)
            if entity and entity.has_secure_fields():
                intent.add_metadata("requires_secure_handling", True)
                intent.add_metadata("ethics", {
                    "privacy": "high",
                    "audit": True,
                    "consent": "required"
                })
        
        program.add_metadata("analyzed_at", datetime.now(timezone.utc).isoformat())
        program.add_metadata("analyzer_version", "0.4.0")
    
    # ────────────────────────────────────────────────────────────────────────
    # Entity Validation
    # ────────────────────────────────────────────────────────────────────────
    
    def visit_entitynode(self, node: EntityNode):
        self.context.current_entity = node.name
        field_names: Set[str] = set()
        
        for f in node.fields:
            self.visit_fieldnode(f)
            if f.name in field_names:
                self.context.add_error(f"Duplicate field '{f.name}' in entity '{node.name}'", f)
            field_names.add(f.name)
        
        if node.has_secure_fields():
            node.add_metadata("contains_secure_data", True)
        
        self.context.current_entity = None
    
    def visit_fieldnode(self, node: FieldNode):
        if node.type not in self.context.supported_types:
            self.context.add_error(
                f"Unsupported field type '{node.type}'. Supported: {', '.join(self.context.supported_types)}", 
                node
            )
        
        # ✅ Fixed add_warning missing references by calling explicit unified wrapper
        if node.is_auto and node.type != "datetime":
            self.context.add_error(
                f"Field '{node.name}' has 'auto' modifier but type is '{node.type}'. 'auto' belongs to datetime fields.",
                node, severity="warning"
            )
        
        if node.is_secure and node.type != "string":
            self.context.add_error(
                f"Secure field '{node.name}' has type '{node.type}'. Strings are preferred for cryptographic secure payloads.",
                node, severity="warning"
            )
    
    # ────────────────────────────────────────────────────────────────────────
    # Intent Validation
    # ────────────────────────────────────────────────────────────────────────
    
    def visit_intentnode(self, node: IntentNode):
        self.context.current_intent = node.name
        self.context.defined_variables = set()
        
        if node.entity:
            if node.entity not in self.context.entities:
                self.context.add_error(f"Intent '{node.name}' references undefined entity '{node.entity}'", node)
            else:
                node.add_metadata("resolved_entity", self.context.entities[node.entity])
        
        if not node.route:
            self.context.add_error(f"Intent '{node.name}' must have a route defined", node)
        elif not node.route.startswith("/"):
            self.context.add_error(f"Route '{node.route}' must start with '/'", node)
        
        for other_name, other_intent in self.context.intents.items():
            if other_name != node.name and other_intent.route == node.route:
                if other_intent.method == node.method:
                    self.context.add_error(
                        f"Duplicate route '{node.route}' with method '{node.method.name}' inside intent '{other_name}'", 
                        node
                    )
        
        for inp in node.inputs:
            self.context.defined_variables.add(inp)
        
        for step in node.steps:
            self.visit_stepnode(step)
        
        self.context.current_intent = None
        self.context.defined_variables = set()
    
    # ────────────────────────────────────────────────────────────────────────
    # Step Validation
    # ────────────────────────────────────────────────────────────────────────
    
    def visit_stepnode(self, node: StepNode):
        step_type = node.step_type
        args = node.args
        
        if step_type == StepType.FIND:
            entity_name = args.get("entity")
            field_name = args.get("field")
            as_var = args.get("as")
            
            if entity_name and entity_name not in self.context.entities:
                self.context.add_error(f"FIND references undefined entity '{entity_name}'", node)
            elif entity_name and field_name:
                entity = self.context.entities[entity_name]
                if not entity.get_field(field_name):
                    self.context.add_error(f"FIND references undefined field '{field_name}' in entity '{entity_name}'", node)
            
            if as_var:
                self.context.defined_variables.add(as_var)
        
        elif step_type in (StepType.CREATE, StepType.UPDATE, StepType.DELETE):
            entity_name = args.get("entity")
            if entity_name and entity_name not in self.context.entities:
                self.context.add_error(f"{step_type.name} references undefined entity '{entity_name}'", node)
        
        elif step_type == StepType.IF_EXISTS:
            field_target = args.get("field")
            # ✅ Fixed: Resolve validation checks against active Entity fields to avoid false positive error traps
            active_intent = self.context.intents.get(self.context.current_intent)
            associated_entity = self.context.entities.get(active_intent.entity) if active_intent else None
            
            if field_target and field_target not in self.context.defined_variables:
                if associated_entity and not associated_entity.get_field(field_target):
                    self.context.add_error(f"IF_EXISTS references an unmapped field/variable target: '{field_target}'", node)
        
        elif step_type == StepType.IF_NOT_FOUND:
            var = args.get("var")
            if var and var not in self.context.defined_variables:
                self.context.add_error(f"IF_NOT_FOUND checks undefined variable tracking pointer '{var}'", node)
        
        elif step_type == StepType.PASSWORD_CHECK:
            var = args.get("var")
            if var and var not in self.context.defined_variables:
                self.context.add_error(f"PASSWORD_CHECK references undefined variable target '{var}'", node)
        
        elif step_type == StepType.RETURN_ERROR:
            message = args.get("message")
            if not message:
                self.context.add_error("RETURN_ERROR block omitted its verbal error message context descriptor string.", node, severity="warning")
        
        # ✅ Scope Shielding: Create temporary memory frames for block indentation branches
        saved_scopes = set(self.context.defined_variables)
        for body_step in node.body:
            self.visit_stepnode(body_step)
        self.context.defined_variables = saved_scopes
        
        for else_step in node.else_body:
            self.visit_stepnode(else_step)
        self.context.defined_variables = saved_scopes
    
    # ────────────────────────────────────────────────────────────────────────
    # Helper Methods
    # ────────────────────────────────────────────────────────────────────────
    
    def get_errors(self) -> List[AnalysisError]:
        return self.context.errors
    
    def get_warnings(self) -> List[AnalysisError]:
        return self.context.warnings
    
    def get_report(self) -> Dict[str, Any]:
        return {
            "errors": [str(e) for e in self.context.errors],
            "warnings": [str(w) for w in self.context.warnings],
            "entities_count": len(self.context.entities),
            "intents_count": len(self.context.intents),
            "success": not self.context.has_errors()
        }


def analyze_madi(program: ProgramNode) -> ProgramNode:
    analyzer = SemanticAnalyzer()
    return analyzer.analyze(program)
