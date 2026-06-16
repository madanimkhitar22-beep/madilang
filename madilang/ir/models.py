# ════════════════════════════════════════════════════════════════════════════
# 🧠 MadiLang — Intermediate Representation (IR) Models (Final Version)
# ════════════════════════════════════════════════════════════════════════════
# Defines language-agnostic IR structures for code generation.
# IR is the sovereign layer between intent and execution.
# Status: v0.4.0 • Sovereign-by-Design • Multi-Target Ready
# ════════════════════════════════════════════════════════════════════════════

"""
MadiLang Intermediate Representation (IR)

This module defines the IR models that represent MadiLang programs in a
language-agnostic form. The IR is produced by the step compiler from the AST
and consumed by code generators for various target languages.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Union
from enum import Enum, auto


# ────────────────────────────────────────────────────────────────────────────
# IR Enums
# ────────────────────────────────────────────────────────────────────────────

class IROpCode(Enum):
    """IR operation codes for step execution."""
    FIND = auto()
    FIND_UNIQUE = auto()
    CREATE = auto()
    UPDATE = auto()
    DELETE = auto()
    
    IF = auto()
    IF_NOT = auto()
    RETURN = auto()
    STOP = auto()
    
    # Authentication & Cryptography layers
    AUTH_CHECK = auto()
    ROLE_CHECK = auto()
    GENERATE_TOKEN = auto()
    VERIFY_PASSWORD = auto()
    
    RETURN_SUCCESS = auto()
    RETURN_ERROR = auto()
    RETURN_JSON = auto()
    
    ASSIGN = auto()
    LOAD = auto()
    RAW = auto()


class IRValueType(Enum):
    """Types of values in IR."""
    STRING = auto()
    INTEGER = auto()
    FLOAT = auto()
    BOOLEAN = auto()
    NULL = auto()
    VARIABLE = auto()
    INPUT = auto()
    LITERAL = auto()


# ────────────────────────────────────────────────────────────────────────────
# Base IR Node
# ────────────────────────────────────────────────────────────────────────────

@dataclass
class IRNode:
    """Base class for all IR nodes carrying sovereignty metadata for intent tracking."""
    source_line: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    annotations: Dict[str, Any] = field(default_factory=dict)
    
    def add_metadata(self, key: str, value: Any) -> "IRNode":
        self.metadata[key] = value
        return self
    
    def add_annotation(self, key: str, value: Any) -> "IRNode":
        self.annotations[key] = value
        return self
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize node to dictionary safely for auditing and pipeline visibility."""
        return {
            "type": self.__class__.__name__,
            "source_line": self.source_line,
            "metadata": self.metadata,
            "annotations": self.annotations,
        }


# ────────────────────────────────────────────────────────────────────────────
# IR Values & Expressions
# ────────────────────────────────────────────────────────────────────────────

@dataclass
class IRValue(IRNode):
    value_type: IRValueType = IRValueType.LITERAL
    
    def to_dict(self) -> Dict[str, Any]:
        res = super().to_dict()
        res["value_type"] = self.value_type.name
        return res


@dataclass
class IRLiteral(IRValue):
    value: Any = None
    
    def __post_init__(self):
        self.value_type = IRValueType.LITERAL

    def to_dict(self) -> Dict[str, Any]:
        res = super().to_dict()
        res["value"] = self.value
        return res


@dataclass
class IRVariable(IRValue):
    name: str = ""
    
    def __post_init__(self):
        self.value_type = IRValueType.VARIABLE

    def to_dict(self) -> Dict[str, Any]:
        res = super().to_dict()
        res["name"] = self.name
        return res


@dataclass
class IRInput(IRValue):
    name: str = ""
    
    def __post_init__(self):
        self.value_type = IRValueType.INPUT

    def to_dict(self) -> Dict[str, Any]:
        res = super().to_dict()
        res["name"] = self.name
        return res


@dataclass
class IRExpression(IRNode):
    pass


@dataclass
class IRBinaryOp(IRExpression):
    operator: str = ""  # ==, !=, <, >, etc.
    left: Any = None
    right: Any = None

    def __post_init__(self):
        if self.left is None:
            self.left = IRLiteral()
        if self.right is None:
            self.right = IRLiteral()

    def to_dict(self) -> Dict[str, Any]:
        res = super().to_dict()
        res.update({
            "operator": self.operator,
            "left": self.left.to_dict() if hasattr(self.left, 'to_dict') else self.left,
            "right": self.right.to_dict() if hasattr(self.right, 'to_dict') else self.right
        })
        return res


@dataclass
class IRFieldAccess(IRExpression):
    variable: str = ""
    field: str = ""

    def to_dict(self) -> Dict[str, Any]:
        res = super().to_dict()
        res.update({"variable": self.variable, "field": self.field})
        return res


# ────────────────────────────────────────────────────────────────────────────
# IR Instructions
# ────────────────────────────────────────────────────────────────────────────

@dataclass
class IRInstruction(IRNode):
    opcode: IROpCode = IROpCode.RAW
    result: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        res = super().to_dict()
        res.update({"opcode": self.opcode.name, "result": self.result})
        return res


@dataclass
class IRFindInstruction(IRInstruction):
    def __init__(self, entity_name: str = "", query_field: str = "", value: Any = None, assign_to: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        
        self.entity_name = entity_name
        self.query_field = query_field
        
        if value is None:
            try:
                self.value = IRLiteral(value="")
            except NameError:
                self.value = ""
        else:
            self.value = value
            
        self.assign_to = assign_to


@dataclass
class IRCreateInstruction(IRInstruction):
    entity: str = ""
    data: Dict[str, IRValue] = field(default_factory=dict)
    
    def __post_init__(self):
        self.opcode = IROpCode.CREATE
        if self.result is None:
            self.result = "result"

    def to_dict(self) -> Dict[str, Any]:
        res = super().to_dict()
        res.update({
            "entity": self.entity,
            "data": {k: v.to_dict() if hasattr(v, 'to_dict') else v for k, v in self.data.items()}
        })
        return res


@dataclass
class IRUpdateInstruction(IRInstruction):
    entity: str = ""
    where: Dict[str, IRValue] = field(default_factory=dict)
    data: Dict[str, IRValue] = field(default_factory=dict)
    
    def __post_init__(self):
        self.opcode = IROpCode.UPDATE

    def to_dict(self) -> Dict[str, Any]:
        res = super().to_dict()
        res.update({
            "entity": self.entity,
            "where": {k: v.to_dict() if hasattr(v, 'to_dict') else v for k, v in self.where.items()},
            "data": {k: v.to_dict() if hasattr(v, 'to_dict') else v for k, v in self.data.items()}
        })
        return res


@dataclass
class IRDeleteInstruction(IRInstruction):
    entity: str = ""
    where: Dict[str, IRValue] = field(default_factory=dict)
    
    def __post_init__(self):
        self.opcode = IROpCode.DELETE

    def to_dict(self) -> Dict[str, Any]:
        res = super().to_dict()
        res.update({
            "entity": self.entity,
            "where": {k: v.to_dict() if hasattr(v, 'to_dict') else v for k, v in self.where.items()}
        })
        return res


@dataclass
class IRIfInstruction(IRInstruction):
    condition: Any = None
    body: List[IRInstruction] = field(default_factory=list)
    else_body: List[IRInstruction] = field(default_factory=list)
    
    def __post_init__(self):
        self.opcode = IROpCode.IF
        if self.condition is None:
            self.condition = IRBinaryOp()

    def to_dict(self) -> Dict[str, Any]:
        res = super().to_dict()
        res.update({
            "condition": self.condition.to_dict() if hasattr(self.condition, 'to_dict') else self.condition,
            "body": [i.to_dict() for i in self.body],
            "else_body": [i.to_dict() for i in self.else_body]
        })
        return res


@dataclass
class IRReturnInstruction(IRInstruction):
    status_code: int = 200
    data: Dict[str, IRValue] = field(default_factory=dict)
    with_token: bool = False
    
    def __post_init__(self):
        self.opcode = IROpCode.RETURN

    def to_dict(self) -> Dict[str, Any]:
        res = super().to_dict()
        res.update({
            "status_code": self.status_code,
            "with_token": self.with_token,
            "data": {k: v.to_dict() if hasattr(v, 'to_dict') else v for k, v in self.data.items()}
        })
        return res


@dataclass
class IRErrorInstruction(IRInstruction):
    status_code: int = 400
    message: str = ""
    
    def __post_init__(self):
        self.opcode = IROpCode.RETURN_ERROR

    def to_dict(self) -> Dict[str, Any]:
        res = super().to_dict()
        res.update({"status_code": self.status_code, "message": self.message})
        return res


@dataclass
class IRAuthCheckInstruction(IRInstruction):
    required: bool = True
    
    def __post_init__(self):
        self.opcode = IROpCode.AUTH_CHECK

    def to_dict(self) -> Dict[str, Any]:
        res = super().to_dict()
        res["required"] = self.required
        return res


@dataclass
class IRRoleCheckInstruction(IRInstruction):
    roles: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        self.opcode = IROpCode.ROLE_CHECK

    def to_dict(self) -> Dict[str, Any]:
        res = super().to_dict()
        res["roles"] = self.roles
        return res


@dataclass
class IRGenerateTokenInstruction(IRInstruction):
    payload: Dict[str, IRValue] = field(default_factory=dict)
    expires_in: str = "7d"
    
    def __post_init__(self):
        self.opcode = IROpCode.GENERATE_TOKEN
        if self.result is None:
            self.result = "token"

    def to_dict(self) -> Dict[str, Any]:
        res = super().to_dict()
        res.update({
            "result": self.result,
            "expires_in": self.expires_in,
            "payload": {k: v.to_dict() if hasattr(v, 'to_dict') else v for k, v in self.payload.items()}
        })
        return res


@dataclass
class IRVerifyPasswordInstruction(IRInstruction):
    input_var: str = "password"
    stored_var: str = ""
    stored_field: str = "password"
    
    def __post_init__(self):
        self.opcode = IROpCode.VERIFY_PASSWORD
        if self.result is None:
            self.result = "password_valid"

    def to_dict(self) -> Dict[str, Any]:
        res = super().to_dict()
        res.update({
            "input_var": self.input_var,
            "stored_var": self.stored_var,
            "stored_field": self.stored_field,
            "result": self.result
        })
        return res


@dataclass
class IRRawInstruction(IRInstruction):
    text: str = ""
    
    def __post_init__(self):
        self.opcode = IROpCode.RAW

    def to_dict(self) -> Dict[str, Any]:
        res = super().to_dict()
        res["text"] = self.text
        return res


# ────────────────────────────────────────────────────────────────────────────
# IR Blocks and Functions
# ────────────────────────────────────────────────────────────────────────────

@dataclass
class IRBlock(IRNode):
    """Block of IR instructions representing a unified localized scope sequence."""
    instructions: List[IRInstruction] = field(default_factory=list)
    variables: Dict[str, str] = field(default_factory=dict)  # var_name -> type
    
    def add_instruction(self, instr: IRInstruction) -> "IRBlock":
        self.instructions.append(instr)
        return self
    
    def add_variable(self, name: str, type_hint: str = "any") -> "IRBlock":
        self.variables[name] = type_hint
        return self

    def to_dict(self) -> Dict[str, Any]:
        res = super().to_dict()
        res.update({
            "variables": self.variables,
            "instructions": [i.to_dict() for i in self.instructions]
        })
        return res


@dataclass
class IRIntent(IRNode):
    """IR representation of an intent mapped to target endpoints."""
    name: str = ""
    entity: str = ""
    route: str = ""
    method: str = "POST"
    inputs: List[str] = field(default_factory=list)
    body: IRBlock = field(default_factory=IRBlock)
    
    requires_auth: bool = False
    required_roles: List[str] = field(default_factory=list)
    signature: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        res = super().to_dict()
        res.update({
            "name": self.name,
            "entity": self.entity,
            "route": self.route,
            "method": self.method,
            "inputs": self.inputs,
            "requires_auth": self.requires_auth,
            "required_roles": self.required_roles,
            "signature": self.signature,
            "body": self.body.to_dict()
        })
        return res


@dataclass
class IREntity(IRNode):
    """IR representation of an entity holding dynamic physical mappings."""
    name: str = ""
    fields: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    has_secure_fields: bool = False
    secure_field_names: List[str] = field(default_factory=list)
    
    def add_field(self, name: str, type_: str, modifiers: List[str] = None):
        mods = modifiers or []
        self.fields[name] = {
            "type": type_,
            "modifiers": mods,
            "is_unique": "unique" in mods,
            "is_secure": "secure" in mods,
            "is_optional": "optional" in mods,
            "is_auto": "auto" in mods,
        }
        if "secure" in mods:
            self.has_secure_fields = True
            self.secure_field_names.append(name)

    def to_dict(self) -> Dict[str, Any]:
        res = super().to_dict()
        res.update({
            "name": self.name,
            "fields": self.fields,
            "has_secure_fields": self.has_secure_fields,
            "secure_field_names": self.secure_field_names
        })
        return res


@dataclass
class IRProgram(IRNode):
    """Complete IR program containing cross-compiled structures."""
    entities: Dict[str, IREntity] = field(default_factory=dict)
    intents: Dict[str, IRIntent] = field(default_factory=dict)
    signature: Optional[Dict[str, Any]] = None
    analysis_report: Dict[str, Any] = field(default_factory=dict)
    
    def add_entity(self, entity: IREntity) -> "IRProgram":
        self.entities[entity.name] = entity
        return self
    
    def add_intent(self, intent: IRIntent) -> "IRProgram":
        self.intents[intent.name] = intent
        return self
    
    def get_intent(self, name: str) -> Optional[IRIntent]:
        return self.intents.get(name)
    
    def get_entity(self, name: str) -> Optional[IREntity]:
        return self.entities.get(name)
    
    def to_dict(self) -> Dict[str, Any]:
        res = super().to_dict()
        res.update({
            "entities": {k: v.to_dict() for k, v in self.entities.items()},
            "intents": {k: v.to_dict() for k, v in self.intents.items()},
            "signature": self.signature,
            "analysis": self.analysis_report,
        })
        return res
    
    def dump_json(self, indent: int = 2) -> str:
        import json
        return json.dumps(self.to_dict(), indent=indent, default=str)


# ────────────────────────────────────────────────────────────────────────────
# IR Builder (Fluent API for constructing IR)
# ────────────────────────────────────────────────────────────────────────────

class IRBuilder:
    """Fluent API for constructing valid language-agnostic IR environments programmatically."""
    
    def __init__(self):
        self.program = IRProgram()
        self._current_intent: Optional[IRIntent] = None
    
    def entity(self, name: str) -> "IRBuilder":
        entity = IREntity(name=name)
        self.program.add_entity(entity)
        return self
    
    def field(self, name: str, type_: str, *modifiers: str) -> "IRBuilder":
        if self.program.entities:
            last_entity = list(self.program.entities.values())[-1]
            last_entity.add_field(name, type_, list(modifiers))
        return self
    
    def intent(self, name: str, entity: str, route: str, method: str = "POST") -> "IRBuilder":
        intent = IRIntent(name=name, entity=entity, route=route, method=method)
        self.program.add_intent(intent)
        self._current_intent = intent
        return self
    
    def input(self, *names: str) -> "IRBuilder":
        if self._current_intent:
            self._current_intent.inputs.extend(names)
        return self
    
    def find(self, entity: str, field: str, value: str, as_var: str) -> "IRBuilder":
        if self._current_intent:
            instr = IRFindInstruction(entity=entity, field=field, 
                                      value=IRVariable(name=value))
            instr.result = as_var
            self._current_intent.body.add_instruction(instr)
            self._current_intent.body.add_variable(as_var, entity)
        return self
    
    def create(self, entity: str, **data) -> "IRBuilder":
        if self._current_intent:
            instr_data = {k: IRVariable(name=v) if isinstance(v, str) else IRLiteral(value=v) 
                         for k, v in data.items()}
            instr = IRCreateInstruction(entity=entity, data=instr_data)
            self._current_intent.body.add_instruction(instr)
        return self
    
    def if_exists(self, field: str) -> "IRBuilder":
        return self
    
    def error(self, message: str, status: int = 400) -> "IRBuilder":
        if self._current_intent:
            instr = IRErrorInstruction(message=message, status_code=status)
            self._current_intent.body.add_instruction(instr)
        return self
    
    def success(self, with_token: bool = False) -> "IRBuilder":
        if self._current_intent:
            instr = IRReturnInstruction(with_token=with_token)
            self._current_intent.body.add_instruction(instr)
        return self
    
    def build(self) -> IRProgram:
        return self.program


# ────────────────────────────────────────────────────────────────────────────
# Convenience Functions
# ────────────────────────────────────────────────────────────────────────────

def create_ir_program() -> IRProgram:
    return IRProgram()


def ir_builder() -> IRBuilder:
    return IRBuilder()
