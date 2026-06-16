# ════════════════════════════════════════════════════════════════════════════
# 🧠 MadiLang — Abstract Syntax Tree Nodes
# ════════════════════════════════════════════════════════════════════════════
# Defines the structural representation of MadiLang source code.
# Uses dataclasses for type safety, immutability, and clean serialization.
# Status: v0.4.0 • Sovereign-by-Design • Mobile-First
# ════════════════════════════════════════════════════════════════════════════

"""
AST Nodes for MadiLang Compiler

This module defines the Abstract Syntax Tree (AST) node classes that represent
the structure of MadiLang source code after parsing. These nodes are used by
the analyzer, IR compiler, and code generators.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum, auto


# ────────────────────────────────────────────────────────────────────────────
# Enums for Type Safety
# ────────────────────────────────────────────────────────────────────────────

class HTTPMethod(Enum):
    """Supported HTTP methods for intent routes."""
    GET = auto()
    POST = auto()
    PUT = auto()
    PATCH = auto()
    DELETE = auto()
    
    @classmethod
    def from_string(cls, value: str) -> "HTTPMethod":
        mapping = {
            "get": cls.GET,
            "post": cls.POST,
            "put": cls.PUT,
            "patch": cls.PATCH,
            "delete": cls.DELETE,
        }
        return mapping.get(value.lower(), cls.POST)


class StepType(Enum):
    """Types of steps in an intent."""
    FIND = auto()
    CREATE = auto()
    UPDATE = auto()
    DELETE = auto()
    IF_EXISTS = auto()
    IF_NOT_FOUND = auto()
    IF_CONDITION = auto()
    PASSWORD_CHECK = auto()
    RETURN_SUCCESS = auto()
    RETURN_ERROR = auto()
    GENERATE_TOKEN = auto()
    AUTH_REQUIRED = auto()
    ROLE_GUARD = auto()
    STOP = auto()
    RAW = auto()


# ────────────────────────────────────────────────────────────────────────────
# Base Node
# ────────────────────────────────────────────────────────────────────────────

@dataclass
class ASTNode:
    """Base class for all AST nodes with location and sovereignty tracking."""
    line: Optional[int] = None
    column: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def set_location(self, line: int, column: int = 0) -> "ASTNode":
        self.line = line
        self.column = column
        return self
    
    def add_metadata(self, key: str, value: Any) -> "ASTNode":
        self.metadata[key] = value
        return self


# ────────────────────────────────────────────────────────────────────────────
# Program Structure
# ────────────────────────────────────────────────────────────────────────────

@dataclass
class ProgramNode(ASTNode):
    entities: List["EntityNode"] = field(default_factory=list)
    intents: List["IntentNode"] = field(default_factory=list)
    signature: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.entities is None:
            self.entities = []
        if self.intents is None:
            self.intents = []


# ────────────────────────────────────────────────────────────────────────────
# Entity Definitions
# ────────────────────────────────────────────────────────────────────────────

from dataclasses import dataclass, field
from typing import Any, List, Optional

@dataclass
class ASTNode:
    line: Optional[int] = None
    column: Optional[int] = None

    def set_location(self, line: Optional[int] = None, column: Optional[int] = None):
        self.line = line
        self.column = column


class FieldNode(ASTNode):
    def __init__(self, *args, **kwargs):
        self.name = kwargs.pop('name', "")
        
        self.type_name = kwargs.pop('type_name', "")
        self.type = kwargs.pop('type', "")
        if self.type and not self.type_name:
            self.type_name = self.type
        elif self.type_name and not self.type:
            self.type = self.type_name
            
        self.is_unique = kwargs.pop('is_unique', False)
        self.is_secure = kwargs.pop('is_secure', False)
        self.is_nullable = kwargs.pop('is_nullable', False)
        self.is_auto = kwargs.pop('is_auto', False)
        self.modifiers = kwargs.pop('modifiers', None)
        
        super().__init__(
            line=kwargs.pop('line', None), 
            column=kwargs.pop('column', None)
        )
        
        for key, value in kwargs.items():
            setattr(self, key, value)
            

@dataclass
class EntityNode(ASTNode):
    name: str = ""
    fields: List[FieldNode] = field(default_factory=list)
    
    def __post_init__(self):
        if self.fields is None:
            self.fields = []
    
    def get_field(self, name: str) -> Optional[FieldNode]:
        for field in self.fields:
            if field.name == name:
                return field
        return None
    
    def has_secure_fields(self) -> bool:
        return any(f.is_secure for f in self.fields)


# ────────────────────────────────────────────────────────────────────────────
# Intent Definitions
# ────────────────────────────────────────────────────────────────────────────

@dataclass
class IntentNode(ASTNode):
    name: str = ""
    entity: str = ""
    route: str = ""
    method: HTTPMethod = HTTPMethod.POST
    inputs: List[str] = field(default_factory=list)
    steps: List["StepNode"] = field(default_factory=list)
    
    requires_auth: bool = field(init=False)
    required_roles: List[str] = field(init=False)
    
    def __post_init__(self):
        if self.inputs is None:
            self.inputs = []
        if self.steps is None:
            self.steps = []
        
        self.requires_auth = any(
            s.step_type == StepType.AUTH_REQUIRED for s in self.steps
        )
        self.required_roles = [
            s.args.get("role") for s in self.steps
            if s.step_type == StepType.ROLE_GUARD and s.args.get("role")
        ]


@dataclass
class StepNode(ASTNode):
    step_type: str = ""
    args: Dict[str, Any] = field(default_factory=dict)
    body: List["StepNode"] = field(default_factory=list)
    else_body: List["StepNode"] = field(default_factory=list)
    
    def __post_init__(self):
        if self.args is None:
            self.args = {}
        if self.body is None:
            self.body = []
        if self.else_body is None:
            self.else_body = []
    
    @classmethod
    def find(cls, entity: str, field: str, as_var: str, **kwargs) -> "StepNode":
        return cls(
            step_type=StepType.FIND,
            args={"entity": entity, "field": field, "as": as_var, **kwargs}
        )
    
    @classmethod
    def create(cls, entity: str, **kwargs) -> "StepNode":
        return cls(
            step_type=StepType.CREATE,
            args={"entity": entity, **kwargs}
        )
    
    @classmethod
    def if_exists(cls, field: str, body: List["StepNode"] = None, **kwargs) -> "StepNode":
        return cls(
            step_type=StepType.IF_EXISTS,
            args={"field": field, **kwargs},
            body=body or []
        )
    
    @classmethod
    def error(cls, message: str, **kwargs) -> "StepNode":
        return cls(
            step_type=StepType.RETURN_ERROR,
            args={"message": message, **kwargs}
        )
    
    @classmethod
    def success(cls, **kwargs) -> "StepNode":
        return cls(
            step_type=StepType.RETURN_SUCCESS,
            args=kwargs
        )


# ────────────────────────────────────────────────────────────────────────────
# Visitor Pattern Support
# ────────────────────────────────────────────────────────────────────────────

class ASTVisitor:
    def visit(self, node: ASTNode) -> Any:
        method_name = f"visit_{type(node).__name__.lower()}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)
    
    def generic_visit(self, node: ASTNode) -> Any:
        for field_name, field_value in node.__dict__.items():
            if isinstance(field_value, ASTNode):
                self.visit(field_value)
            elif isinstance(field_value, list):
                for item in field_value:
                    if isinstance(item, ASTNode):
                        self.visit(item)
        return node


class ASTTransformer(ASTVisitor):
    def generic_visit(self, node: ASTNode) -> ASTNode:
        for field_name, field_value in node.__dict__.items():
            if isinstance(field_value, ASTNode):
                setattr(node, field_name, self.visit(field_value))
            elif isinstance(field_value, list):
                new_list = []
                for item in field_value:
                    if isinstance(item, ASTNode):
                        new_list.append(self.visit(item))
                    else:
                        new_list.append(item)
                setattr(node, field_name, new_list)
        return node
