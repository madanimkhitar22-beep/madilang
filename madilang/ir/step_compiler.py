# ════════════════════════════════════════════════════════════════════════════
# 🧠 MadiLang — Step Compiler (AST to IR - Refined)
# ════════════════════════════════════════════════════════════════════════════
# Transforms validated AST into language-agnostic Intermediate Representation.
# IR is the sovereign layer where intent becomes executable structure.
# Status: v0.4.0 • Sovereign-by-Design • Multi-Target Ready
# ════════════════════════════════════════════════════════════════════════════

"""
MadiLang Step Compiler

This module compiles the validated AST into Intermediate Representation (IR).
The IR is language-agnostic and carries all sovereignty metadata needed for
secure, ethical code generation.
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field

from madilang.compiler.ast_nodes import (
    ProgramNode,
    EntityNode,
    FieldNode,
    IntentNode,
    StepNode,
    StepType,
    ASTNode,
)

from madilang.ir.models import (
    IRProgram,
    IREntity,
    IRIntent,
    IRBlock,
    IRInstruction,
    IRFindInstruction,
    IRCreateInstruction,
    IRUpdateInstruction,
    IRDeleteInstruction,
    IRIfInstruction,
    IRReturnInstruction,
    IRErrorInstruction,
    IRAuthCheckInstruction,
    IRRoleCheckInstruction,
    IRGenerateTokenInstruction,
    IRVerifyPasswordInstruction,
    IRRawInstruction,
    IRBinaryOp,
    IRVariable,
    IRInput,
    IRLiteral,
    IROpCode,
    IRValue,
)


# ────────────────────────────────────────────────────────────────────────────
# Compilation Context
# ────────────────────────────────────────────────────────────────────────────

@dataclass
class CompilationContext:
    """Holds state during AST to IR compilation, tracking scopes and local variables."""
    current_entity: Optional[str] = None
    current_intent: Optional[str] = None
    
    # Variable tracking: var_name -> type
    defined_variables: Dict[str, str] = field(default_factory=dict)
    entities: Dict[str, EntityNode] = field(default_factory=dict)
    
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def register_variable(self, name: str, type_hint: str = "any"):
        self.defined_variables[name] = type_hint
    
    def is_variable_defined(self, name: str) -> bool:
        return name in self.defined_variables
    
    def get_variable_type(self, name: str) -> str:
        return self.defined_variables.get(name, "any")
    
    def reset_scope(self):
        self.defined_variables.clear()


# ────────────────────────────────────────────────────────────────────────────
# Step Compiler
# ────────────────────────────────────────────────────────────────────────────

class StepCompiler:
    """Compiles MadiLang AST steps into structural explicit IR instructions."""
    
    def __init__(self, context: Optional[CompilationContext] = None):
        self.context = context or CompilationContext()
    
    def compile(self, program: ProgramNode) -> IRProgram:
        ir_program = IRProgram()
        ir_program.metadata = program.metadata.copy() if program.metadata else {}
        ir_program.source_line = program.line
        
        # Phase 1: Compile entities
        for entity in program.entities:
            ir_entity = self._compile_entity(entity)
            ir_program.add_entity(ir_entity)
            self.context.entities[entity.name] = entity
        
        # Phase 2: Compile intents
        for intent in program.intents:
            ir_intent = self._compile_intent(intent)
            ir_program.add_intent(ir_intent)
        
        # Phase 3: Inject signature placeholder for the transformer
        ir_program.signature = {
            "status": "pending",
            "message": "Signature will be injected by IntentSignature transformer"
        }
        
        return ir_program
    
    def _compile_entity(self, entity: EntityNode) -> IREntity:
        ir_entity = IREntity(name=entity.name)
        ir_entity.source_line = entity.line
        ir_entity.metadata = entity.metadata.copy() if entity.metadata else {}
        
        for f in entity.fields:
            ir_entity.add_field(
                name=f.name,
                type_=f.type,
                modifiers=f.modifiers
            )
        
        return ir_entity
    
    def _compile_intent(self, intent: IntentNode) -> IRIntent:
        self.context.current_intent = intent.name
        self.context.reset_scope()
        
        ir_intent = IRIntent(
            name=intent.name,
            entity=intent.entity,
            route=intent.route,
            method=intent.method.name if hasattr(intent.method, 'name') else str(intent.method),
            inputs=intent.inputs.copy() if intent.inputs else [],
            requires_auth=intent.requires_auth,
            required_roles=intent.required_roles.copy() if intent.required_roles else []
        )
        
        ir_intent.source_line = intent.line
        ir_intent.metadata = intent.metadata.copy() if intent.metadata else {}
        
        # Register inputs as valid initial variables
        for inp in ir_intent.inputs:
            self.context.register_variable(inp, "input")
            ir_intent.body.add_variable(inp, "input")
        
        # Compile sequential steps
        for step in intent.steps:
            ir_instructions = self._compile_step(step)
            for instr in ir_instructions:
                ir_intent.body.add_instruction(instr)
        
        self.context.current_intent = None
        return ir_intent
    
    def _compile_step(self, step: StepNode) -> List[IRInstruction]:
        instructions: List[IRInstruction] = []
        step_type = step.step_type
        args = step.args or {}
        
        def set_meta(instr: IRInstruction) -> IRInstruction:
            instr.source_line = step.line
            instr.metadata = step.metadata.copy() if step.metadata else {}
            return instr
        
        # ────────────────────────────────────────────────────────────────────
        # Database Operations
        # ────────────────────────────────────────────────────────────────────
        
        if step_type == StepType.FIND:
            entity = args.get("entity", "")
            field = args.get("field", "")
            as_var = args.get("as", "result")
            # ✅ Fixed: Resolve value pointer dynamically to prevent hardcoded collisions
            value_source = args.get("value", field)
            
            instr = IRFindInstruction(
                entity=entity,
                field=field,
                value=IRVariable(name=value_source),
                result=as_var
            )
            instructions.append(set_meta(instr))
            self.context.register_variable(as_var, entity)
        
        elif step_type == StepType.CREATE:
            entity = args.get("entity", "")
            data: Dict[str, IRValue] = {}
            entity_node = self.context.entities.get(entity)
            
            if entity_node:
                for f in entity_node.fields:
                    if f.name in self.context.defined_variables:
                        data[f.name] = IRVariable(name=f.name)
            
            instr = IRCreateInstruction(entity=entity, data=data, result=args.get("as", "result"))
            instructions.append(set_meta(instr))
        
        elif step_type == StepType.UPDATE:
            entity = args.get("entity", "")
            # ✅ Fixed: Extract actual criteria arrays instead of generating blind bulk queries
            where_field = args.get("where_field", "id")
            where_val = args.get("where_value", "id")
            
            where_clause = {where_field: IRVariable(name=where_val)}
            update_data: Dict[str, IRValue] = {}
            
            entity_node = self.context.entities.get(entity)
            if entity_node:
                for f in entity_node.fields:
                    if f.name in self.context.defined_variables and f.name != where_field:
                        update_data[f.name] = IRVariable(name=f.name)
            
            instr = IRUpdateInstruction(entity=entity, where=where_clause, data=update_data)
            instructions.append(set_meta(instr))
        
        elif step_type == StepType.DELETE:
            entity = args.get("entity", "")
            # ✅ Fixed: Map clear scoping conditions to restrict target destruction boundaries
            where_field = args.get("where_field", "id")
            where_val = args.get("where_value", "id")
            
            where_clause = {where_field: IRVariable(name=where_val)}
            instr = IRDeleteInstruction(entity=entity, where=where_clause)
            instructions.append(set_meta(instr))
        
        # ────────────────────────────────────────────────────────────────────
        # Control Flow (With Safe Block Scope Isolation)
        # ────────────────────────────────────────────────────────────────────
        
        elif step_type == StepType.IF_EXISTS:
            field_target = args.get("field", "")
            condition = IRBinaryOp(operator="!=", left=IRVariable(name=field_target), right=IRLiteral(value=None))
            if_instr = IRIfInstruction(condition=condition)
            
            # Isolated Scope Shielding
            saved_scope = self.context.defined_variables.copy()
            for body_step in step.body:
                if_instr.body.extend(self._compile_step(body_step))
            self.context.defined_variables = saved_scope.copy()
            
            for else_step in step.else_body:
                if_instr.else_body.extend(self._compile_step(else_step))
            self.context.defined_variables = saved_scope
            
            instructions.append(set_meta(if_instr))
        
        elif step_type == StepType.IF_NOT_FOUND:
            var = args.get("var", "")
            condition = IRBinaryOp(operator="==", left=IRVariable(name=var), right=IRLiteral(value=None))
            if_instr = IRIfInstruction(condition=condition)
            
            saved_scope = self.context.defined_variables.copy()
            for body_step in step.body:
                if_instr.body.extend(self._compile_step(body_step))
            self.context.defined_variables = saved_scope.copy()
            
            for else_step in step.else_body:
                if_instr.else_body.extend(self._compile_step(else_step))
            self.context.defined_variables = saved_scope
            
            instructions.append(set_meta(if_instr))
        
        elif step_type == StepType.IF_CONDITION:
            condition_text = args.get("condition", "")
            condition = self._parse_condition(condition_text)
            if_instr = IRIfInstruction(condition=condition)
            
            saved_scope = self.context.defined_variables.copy()
            for body_step in step.body:
                if_instr.body.extend(self._compile_step(body_step))
            self.context.defined_variables = saved_scope.copy()
            
            for else_step in step.else_body:
                if_instr.else_body.extend(self._compile_step(else_step))
            self.context.defined_variables = saved_scope
            
            instructions.append(set_meta(if_instr))
        
        # ────────────────────────────────────────────────────────────────────
        # Authentication
        # ────────────────────────────────────────────────────────────────────
        
        elif step_type == StepType.AUTH_REQUIRED:
            instr = IRAuthCheckInstruction(required=True)
            instructions.append(set_meta(instr))
        
        elif step_type == StepType.ROLE_GUARD:
            role = args.get("role", "")
            instr = IRRoleCheckInstruction(roles=[role])
            instructions.append(set_meta(instr))
        
        elif step_type == StepType.PASSWORD_CHECK:
            var = args.get("var", "")
            field_name = args.get("field", "password")
            # ✅ Fixed: Removed hardcoded input binding to resolve fluid user naming schemas
            input_secret = args.get("input_secret", "password")
            
            instr = IRVerifyPasswordInstruction(
                input_var=input_secret,
                stored_var=var,
                stored_field=field_name
            )
            instructions.append(set_meta(instr))
        
        elif step_type == StepType.GENERATE_TOKEN:
            instr = IRGenerateTokenInstruction(
                payload={"id": IRVariable(name="user.id")},
                result=args.get("as", "token")
            )
            instructions.append(set_meta(instr))
        
        # ────────────────────────────────────────────────────────────────────
        # Response
        # ────────────────────────────────────────────────────────────────────
        
        elif step_type == StepType.RETURN_SUCCESS:
            with_token = args.get("with_token", False)
            instr = IRReturnInstruction(
                status_code=200,
                data={"success": IRLiteral(value=True)},
                with_token=with_token
            )
            instructions.append(set_meta(instr))
        
        elif step_type == StepType.RETURN_ERROR:
            message = args.get("message", "Error occurred")
            instr = IRErrorInstruction(
                status_code=args.get("status_code", 400),
                message=message
            )
            instructions.append(set_meta(instr))
        
        elif step_type == StepType.STOP:
            instr = IRErrorInstruction(
                status_code=400,
                message="Process stopped"
            )
            instructions.append(set_meta(instr))
        
        elif step_type == StepType.RAW:
            text = args.get("text", "")
            instr = IRRawInstruction(text=text)
            instructions.append(set_meta(instr))
        
        else:
            instr = IRRawInstruction(text=f"Unknown step: {step_type}")
            instructions.append(set_meta(instr))
        
        return instructions
    
    def _parse_condition(self, condition: str) -> IRBinaryOp:
        condition = condition.strip()
        
        if " exists" in condition:
            field = condition.replace(" exists", "").strip()
            return IRBinaryOp(operator="!=", left=IRVariable(name=field), right=IRLiteral(value=None))
        
        if " is null" in condition or " not found" in condition:
            field = condition.replace(" is null", "").replace(" not found", "").strip()
            return IRBinaryOp(operator="==", left=IRVariable(name=field), right=IRLiteral(value=None))
        
        return IRBinaryOp(operator="!=", left=IRVariable(name=condition), right=IRLiteral(value=None))


# ────────────────────────────────────────────────────────────────────────────
# Convenience Functions
# ────────────────────────────────────────────────────────────────────────────

def compile_to_ir(program: ProgramNode) -> IRProgram:
    compiler = StepCompiler()
    return compiler.compile(program)


def compile_step_to_ir(step: StepNode, context: Optional[CompilationContext] = None) -> List[IRInstruction]:
    compiler = StepCompiler(context)
    return compiler._compile_step(step)
