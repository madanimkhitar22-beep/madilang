# ════════════════════════════════════════════════════════════════════════════
# 🧠 MadiLang — Recursive Descent Parser (Refined)
# ════════════════════════════════════════════════════════════════════════════
# Transforms MadiLang source code into Abstract Syntax Tree (AST).
# Implements recursive descent parsing with integrated scanner.
# Status: v0.4.0 • Mobile-First • Sovereign-by-Design
# ════════════════════════════════════════════════════════════════════════════

"""
MadiLang Parser

This module implements a recursive descent parser that transforms MadiLang
source code into an Abstract Syntax Tree (AST). The parser uses an integrated
scanner approach for memory efficiency on mobile devices.
"""

from typing import List, Optional, Tuple, Dict, Any
from madilang.compiler.ast_nodes import (
    ProgramNode,
    EntityNode,
    FieldNode,
    IntentNode,
    StepNode,
    StepType,
    HTTPMethod,
)


class ParseError(Exception):
    """Exception raised for parsing errors with location info."""
    def __init__(self, message: str, line: int, column: int = 0):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"ParseError at line {line}, col {column}: {message}")


class MadiParser:
    """Recursive descent parser for MadiLang with integrated scanner."""
    
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.current_char = source[0] if source else None
    
    # ────────────────────────────────────────────────────────────────────────
    # Scanner Helpers
    # ────────────────────────────────────────────────────────────────────────
    
    def _advance(self) -> str:
        """Advance to next character and return current."""
        current = self.current_char
        self.pos += 1
        if self.pos < len(self.source):
            self.current_char = self.source[self.pos]
            self.column += 1
        else:
            self.current_char = None
        return current
    
    def _peek(self, offset: int = 0) -> Optional[str]:
        """Look ahead without advancing."""
        pos = self.pos + offset
        if pos < len(self.source):
            return self.source[pos]
        return None
    
    def _match(self, expected: str) -> bool:
        """Check if current position matches expected string."""
        return self.source[self.pos:].startswith(expected)
    
    def _consume(self, expected: str) -> bool:
        """Consume expected string if matched."""
        if self._match(expected):
            for _ in expected:
                self._advance()
            return True
        return False
    
    def _skip_whitespace(self) -> None:
        """Skip spaces and tabs (not newlines)."""
        while self.current_char and self.current_char in " \t":
            self._advance()
    
    def _skip_line(self) -> None:
        """Skip to end of line."""
        while self.current_char and self.current_char != "\n":
            self._advance()
        if self.current_char == "\n":
            self._advance()
            self.line += 1
            self.column = 1
    
    def _get_indent(self) -> int:
        """Get current indentation level without shifting position."""
        indent = 0
        pos = self.pos
        while pos < len(self.source) and self.source[pos] in " \t":
            indent += 1
            pos += 1
        return indent
    
    def _error(self, message: str) -> ParseError:
        return ParseError(message, self.line, self.column)
    
    # ────────────────────────────────────────────────────────────────────────
    # Parsing Primitives
    # ────────────────────────────────────────────────────────────────────────
    
    def _parse_identifier(self) -> str:
        """Parse an identifier (letters, digits, underscores)."""
        start_pos = self.pos
        while self.current_char and (self.current_char.isalnum() or self.current_char == "_"):
            self._advance()
        if self.pos == start_pos:
            raise self._error("Expected identifier")
        return self.source[start_pos:self.pos]
    
    def _parse_string(self) -> str:
        """Parse a quoted string."""
        quote = self.current_char
        if quote not in '"\'':
            raise self._error("Expected string starting with ' or \"")
        self._advance()
        start = self.pos
        while self.current_char and self.current_char != quote:
            if self.current_char == "\\":
                self._advance()
            self._advance()
        if not self.current_char:
            raise self._error("Unterminated string")
        value = self.source[start:self.pos]
        self._advance()  # consume closing quote
        return value
    
    def _parse_type(self) -> str:
        """Parse a type identifier."""
        return self._parse_identifier().lower()
    
    # ────────────────────────────────────────────────────────────────────────
    # Field Parsing
    # ────────────────────────────────────────────────────────────────────────
    
    def _parse_modifiers(self) -> List[str]:
        modifiers = []
        if self.current_char == "(":
            self._advance()
            self._skip_whitespace()
            while self.current_char and self.current_char != ")":
                mod = self._parse_identifier()
                modifiers.append(mod.lower())
                self._skip_whitespace()
                if self.current_char == ",":
                    self._advance()
                    self._skip_whitespace()
            if self.current_char != ")":
                raise self._error("Expected closing ')' for modifiers")
            self._advance()
        return modifiers
    
    def _parse_field(self) -> FieldNode:
        start_line = self.line
        self._skip_whitespace()
        
        if self.current_char == "-":
            self._advance()
            self._skip_whitespace()
        
        name = self._parse_identifier()
        self._skip_whitespace()
        
        if self.current_char != ":":
            raise self._error(f"Expected ':' after field name '{name}'")
        self._advance()
        self._skip_whitespace()
        
        field_type = self._parse_type()
        self._skip_whitespace()
        
        modifiers = self._parse_modifiers()
        
        node = FieldNode(name=field_name, type_name=field_type, modifiers=modifiers)
        node.set_location(start_line)
        return node
    
    def _parse_fields(self) -> List[FieldNode]:
        fields = []
        self._skip_whitespace()
        
        if not self._consume("fields:"):
            return fields
        
        self._skip_line()
        
        while self.current_char:
            # Check for empty lines safely
            current_indent = self._get_indent()
            pos_after_spaces = self.pos + current_indent
            if pos_after_spaces < len(self.source) and self.source[pos_after_spaces] == "\n":
                self._skip_line()
                continue
                
            if current_indent == 0:
                break
            
            self._skip_whitespace()
            if self.current_char == "-" or current_indent > 0:
                fields.append(self._parse_field())
                self._skip_line()
            else:
                break
        
        return fields
    
    # ────────────────────────────────────────────────────────────────────────
    # Entity Parsing
    # ────────────────────────────────────────────────────────────────────────
    
    def _parse_entity(self) -> EntityNode:
        start_line = self.line
        if not self._consume("entity:"):
            raise self._error("Expected 'entity:'")
        self._skip_whitespace()
        
        name = self._parse_identifier()
        self._skip_line()
        
        fields = self._parse_fields()
        
        node = EntityNode(name=name, fields=fields)
        node.set_location(start_line)
        return node
    
    # ────────────────────────────────────────────────────────────────────────
    # Intent Parsing
    # ────────────────────────────────────────────────────────────────────────
    
    def _parse_inputs(self) -> List[str]:
        inputs = []
        if not self._consume("inputs:"):
            return inputs
        
        self._skip_whitespace()
        if self.current_char != "(":
            raise self._error("Expected '(' after 'inputs:'")
        self._advance()
        
        while self.current_char and self.current_char != ")":
            self._skip_whitespace()
            if self.current_char == ")":
                break
            inputs.append(self._parse_identifier())
            self._skip_whitespace()
            if self.current_char == ",":
                self._advance()
        
        if self.current_char != ")":
            raise self._error("Expected closing ')' for inputs")
        self._advance()
        self._skip_line()
        return inputs
    
    def _parse_step_condition(self, text: str) -> Tuple[StepType, Dict[str, Any]]:
        text = text.strip().rstrip(":")
        
        if text.startswith("if ") and " exists" in text:
            field_name = text[3:].replace("exists", "").strip()
            return StepType.IF_EXISTS, {"field": field_name}
        
        if text.startswith("if ") and " not found" in text:
            var_name = text[3:].replace("not found", "").strip()
            return StepType.IF_NOT_FOUND, {"var": var_name}
        
        if text.startswith("if password does not match"):
            parts = text.replace("if password does not match", "").strip().split(".")
            if len(parts) == 2:
                return StepType.PASSWORD_CHECK, {"var": parts[0], "field": parts[1]}
        
        if text.startswith("if "):
            condition = text[3:].strip()
            return StepType.IF_CONDITION, {"condition": condition}
        
        return StepType.RAW, {"text": text}
    
    def _parse_step_type(self, text: str) -> Tuple[StepType, Dict[str, Any]]:
        text = text.strip()
        
        if text.startswith("find ") and " by " in text and " as " in text:
            parts = text[5:].split(" by ")
            entity = parts[0].strip()
            rest = parts[1].split(" as ")
            field_name = rest[0].strip()
            as_var = rest[1].strip()
            return StepType.FIND, {"entity": entity, "field": field_name, "as": as_var}
        
        if text.startswith("create "):
            entity = text[7:].strip()
            return StepType.CREATE, {"entity": entity}
        
        if text.startswith("update "):
            entity = text[7:].strip()
            return StepType.UPDATE, {"entity": entity}
        
        if text.startswith("delete "):
            entity = text[7:].strip()
            return StepType.DELETE, {"entity": entity}
        
        if text.startswith("if "):
            return self._parse_step_condition(text)
        
        if text.startswith("show error"):
            msg_start = text.find('"')
            if msg_start != -1:
                msg_end = text.find('"', msg_start + 1)
                if msg_end != -1:
                    message = text[msg_start+1:msg_end]
                    return StepType.RETURN_ERROR, {"message": message}
            return StepType.RETURN_ERROR, {"message": text[10:].strip().strip('"')}
        
        if text == "return success" or text == "return success with token":
            return StepType.RETURN_SUCCESS, {"with_token": "token" in text}
        
        if "generate token" in text:
            return StepType.GENERATE_TOKEN, {}
        
        if text == "protect route" or "auth required" in text:
            return StepType.AUTH_REQUIRED, {}
        
        if text.startswith("allow only"):
            role = text[10:].strip()
            return StepType.ROLE_GUARD, {"role": role}
        
        if text == "stop" or text == "stop process":
            return StepType.STOP, {}
        
        return StepType.RAW, {"text": text}

    def _parse_steps(self) -> List[StepNode]:
        """Parse structured steps block with explicit block-indentation safety."""
        steps = []
        if not self._consume("steps:"):
            return steps
        
        self._skip_line()
        base_steps_indent = None
        
        while self.current_char:
            # Skip blank lines cleanly
            current_indent = self._get_indent()
            pos_after_spaces = self.pos + current_indent
            if pos_after_spaces < len(self.source) and self.source[pos_after_spaces] == "\n":
                self._skip_line()
                continue
            
            if current_indent == 0:
                break
                
            if base_steps_indent is None:
                base_steps_indent = current_indent
            
            # If indent drops below the steps base indentation, exit block safely
            if current_indent < base_steps_indent:
                break
                
            start_line = self.line
            self._skip_whitespace()
            
            line_start = self.pos
            while self.current_char and self.current_char != "\n":
                self._advance()
            text = self.source[line_start:self.pos].strip()
            self._skip_line()
            
            step_type, args = self._parse_step_type(text)
            current_node = StepNode(step_type=step_type, args=args)
            current_node.set_location(start_line)
            
            # Smart Nested Handling: If this step is conditional, look for indented body steps
            if step_type in [StepType.IF_EXISTS, StepType.IF_NOT_FOUND, StepType.IF_CONDITION, StepType.PASSWORD_CHECK]:
                next_indent = self._get_indent()
                if next_indent > current_indent:
                    # Recursive parsing for nested conditional body
                    while self.current_char:
                        sub_indent = self._get_indent()
                        if sub_indent <= current_indent:
                            break
                        
                        sub_line = self.line
                        self._skip_whitespace()
                        sub_start = self.pos
                        while self.current_char and self.current_char != "\n":
                            self._advance()
                        sub_text = self.source[sub_start:self.pos].strip()
                        self._skip_line()
                        
                        sub_type, sub_args = self._parse_step_type(sub_text)
                        sub_node = StepNode(step_type=sub_type, args=sub_args)
                        sub_node.set_location(sub_line)
                        current_node.body.append(sub_node)
            
            steps.append(current_node)
            
        return steps
    
    def _parse_intent(self) -> IntentNode:
        start_line = self.line
        if not self._consume("intent:"):
            raise self._error("Expected 'intent:'")
        self._skip_whitespace()
        
        name = self._parse_identifier()
        self._skip_line()
        
        entity = ""
        route = ""
        method = HTTPMethod.POST
        inputs: List[str] = []
        steps: List[StepNode] = []
        
        while self.current_char:
            current_indent = self._get_indent()
            
            # Avoid Infinite Loops: Safely boundary check next root declarations
            if current_indent == 0:
                pos_after_spaces = self.pos + current_indent
                if self.source[pos_after_spaces:].startswith("entity:") or \
                   self.source[pos_after_spaces:].startswith("intent:"):
                    break
            
            self._skip_whitespace()
            if self.current_char == "\n":
                self._skip_line()
                continue
            
            if self._match("entity:"):
                self._consume("entity:")
                self._skip_whitespace()
                entity = self._parse_identifier()
                self._skip_line()
            elif self._match("route:"):
                self._consume("route:")
                self._skip_whitespace()
                route = self._parse_string() if self.current_char in '"\'' else self._parse_identifier()
                self._skip_line()
            elif self._match("method:"):
                self._consume("method:")
                self._skip_whitespace()
                method_str = self._parse_identifier()
                method = HTTPMethod.from_string(method_str)
                self._skip_line()
            elif self._match("inputs:"):
                inputs = self._parse_inputs()
            elif self._match("steps:"):
                steps = self._parse_steps()
            else:
                self._skip_line()
        
        node = IntentNode(
            name=name, entity=entity, route=route,
            method=method, inputs=inputs, steps=steps
        )
        node.set_location(start_line)
        return node
    
    # ────────────────────────────────────────────────────────────────────────
    # Program Parsing
    # ────────────────────────────────────────────────────────────────────────
    
    def parse(self) -> ProgramNode:
        entities: List[EntityNode] = []
        intents: List[IntentNode] = []
        
        while self.current_char:
            self._skip_whitespace()
            if not self.current_char:
                break
            if self.current_char == "\n":
                self._skip_line()
                continue
            if self.current_char == "#":
                self._skip_line()
                continue
            
            try:
                if self._match("entity:"):
                    entities.append(self._parse_entity())
                elif self._match("intent:"):
                    intents.append(self._parse_intent())
                else:
                    self._skip_line()
            except ParseError:
                raise
                
        return ProgramNode(entities=entities, intents=intents)


def parse_madi(source: str) -> ProgramNode:
    parser = MadiParser(source)
    return parser.parse()
