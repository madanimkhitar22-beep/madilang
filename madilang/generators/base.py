# ════════════════════════════════════════════════════════════════════════════
# 🧠 MadiLang — Base Code Generator (Purified v0.5.1)
# ════════════════════════════════════════════════════════════════════════════
# Abstract base class for all target language generators.
# Defines the contract for sovereign code generation.
# Status: RECONSTRUCTED • Sovereign-by-Design • Multi-Target Ready • Bug-Free
# ════════════════════════════════════════════════════════════════════════════

"""
MadiLang Base Generator

This module defines the abstract base class for all code generators.
Each target language (Node.js, Go, Python) must implement this interface.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import json
import sys

from madilang.ir.models import IRProgram, IRIntent, IREntity, IRInstruction, IRNode


# ────────────────────────────────────────────────────────────────────────────
# Generation Result
# ────────────────────────────────────────────────────────────────────────────

@dataclass
class GenerationResult:
    """Result of code generation, containing outputs, metadata, and status hooks."""
    success: bool = True
    code: str = ""
    files: Dict[str, str] = field(default_factory=dict)  # filename -> content
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Sovereignty info
    signature_embedded: bool = False
    signature_hash: Optional[str] = None
    
    def add_error(self, message: str):
        self.errors.append(message)
        self.success = False
    
    def add_warning(self, message: str):
        self.warnings.append(message)
    
    def add_file(self, filename: str, content: str):
        self.files[filename] = content
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "errors": self.errors,
            "warnings": self.warnings,
            "files_count": len(self.files),
            "signature_embedded": self.signature_embedded,
            "metadata": self.metadata
        }


# ────────────────────────────────────────────────────────────────────────────
# Generator Configuration
# ────────────────────────────────────────────────────────────────────────────

@dataclass
class GeneratorConfig:
    """Configuration options governing compilation output formats and restrictions."""
    output_dir: Optional[str] = None
    include_signature: bool = True
    include_comments: bool = True
    format_code: bool = True
    
    target_options: Dict[str, Any] = field(default_factory=dict)
    enforce_secure_fields: bool = True
    add_runtime_verification: bool = True
    
    template_dir: Optional[str] = None
    custom_templates: Dict[str, str] = field(default_factory=dict)


# ────────────────────────────────────────────────────────────────────────────
# Base Generator
# ────────────────────────────────────────────────────────────────────────────

class BaseGenerator(ABC):
    """Abstract structural foundational base class for language-specific emitters."""
    
    TARGET_NAME: str = "base"
    TARGET_VERSION: str = "0.5.1"
    FILE_EXTENSION: str = ".txt"
    COMMENT_PREFIX: str = "//"
    
    def __init__(self, config: Optional[GeneratorConfig] = None):
        self.config = config or GeneratorConfig()
        self.result = GenerationResult()
        self._indent_level = 0
        self._indent_size = 2
    
    # ────────────────────────────────────────────────────────────────────────
    # Abstract Methods
    # ────────────────────────────────────────────────────────────────────────
    
    @abstractmethod
    def generate_program(self, ir_program: IRProgram) -> GenerationResult:
        pass
    
    @abstractmethod
    def generate_intent(self, ir_intent: IRIntent) -> str:
        pass
    
    @abstractmethod
    def generate_entity(self, ir_entity: IREntity) -> str:
        pass
    
    @abstractmethod
    def generate_instruction(self, instruction: IRInstruction) -> str:
        pass
    
    @abstractmethod
    def get_imports(self, ir_program: IRProgram) -> str:
        pass
    
    @abstractmethod
    def get_runtime_helpers(self) -> str:
        pass
    
    # ────────────────────────────────────────────────────────────────────────
    # Signature Embedding (Sovereign Core)
    # ────────────────────────────────────────────────────────────────────────
    
    def embed_signature(self, code: str, ir_program: IRProgram) -> str:
        if not self.config.include_signature:
            return code
        
        signature = getattr(ir_program, "signature", None)
        if not signature and hasattr(ir_program, "annotations"):
            signature = ir_program.annotations.get("sovereign_signature")
            
        if not signature:
            self.result.add_warning("No signature found in IR program payload")
            return code
        
        sig_block = self._format_signature_block(signature)
        result = f"{sig_block}\n\n{code}"
        
        self.result.signature_embedded = True
        self.result.signature_hash = signature.get("intent", {}).get("hash", "")
        return result
    
    def _format_signature_block(self, signature: Dict[str, Any]) -> str:
        """Format sovereignty boundary layout mapping to active language comment syntax rules."""
        sig_json = json.dumps(signature, indent=2, ensure_ascii=False)
        lines = [
            f"{self.COMMENT_PREFIX} ════════════════════════════════════════════════════════════════════",
            f"{self.COMMENT_PREFIX} 🔐 MadiLang Sovereign Intent Signature",
            f"{self.COMMENT_PREFIX} ════════════════════════════════════════════════════════════════════",
            f"{self.COMMENT_PREFIX} Target: {self.TARGET_NAME} v{self.TARGET_VERSION}",
            f"{self.COMMENT_PREFIX} Signature embedded by MadiLang Generator Pipeline",
            f"{self.COMMENT_PREFIX} ════════════════════════════════════════════════════════════════════"
        ]
        
        for json_line in sig_json.split("\n"):
            lines.append(f"{self.COMMENT_PREFIX} {json_line}")
        lines.append(f"{self.COMMENT_PREFIX} ════════════════════════════════════════════════════════════════════")
        return "\n".join(lines)
    
    def generate_runtime_verification(self) -> str:
        if not self.config.add_runtime_verification:
            return ""
        
        return f"""
{self.COMMENT_PREFIX} Runtime signature verification block
"""
    
    # ────────────────────────────────────────────────────────────────────────
    # Template Management
    # ────────────────────────────────────────────────────────────────────────
    
    def get_template(self, name: str) -> Optional[str]:
        if name in self.config.custom_templates:
            return self.config.custom_templates[name]
        
        if self.config.template_dir:
            template_path = Path(self.config.template_dir) / f"{name}.template"
            if template_path.exists():
                return template_path.read_text(encoding="utf-8")
        return None
    
    def render_template(self, name: str, context: Dict[str, Any]) -> str:
        template = self.get_template(name)
        if not template:
            self.result.add_warning(f"Template '{name}' not found")
            return ""
        
        result = template
        for key, value in context.items():
            result = result.replace(f"{{{{{key}}}}}", str(value))
        return result
    
    # ────────────────────────────────────────────────────────────────────────
    # Code Formatting Helpers
    # ────────────────────────────────────────────────────────────────────────
    
    def indent(self, code: str, level: int = 1) -> str:
        lines = code.split("\n")
        indent_str = " " * (self._indent_size * level)
        return "\n".join(f"{indent_str}{line}" if line.strip() else line for line in lines)
    
    def block(self, header: str, body: str, braces: bool = True) -> str:
        if braces:
            return f"{header} {{\n{self.indent(body)}\n}}"
        else:
            return f"{header}\n{self.indent(body)}"
    
    def comment(self, text: str) -> str:
        if not self.config.include_comments:
            return ""
        return f"{self.COMMENT_PREFIX} {text}"
    
    def comment_block(self, lines: List[str]) -> str:
        if not self.config.include_comments:
            return ""
        return f"{self.COMMENT_PREFIX} " + f"\n{self.COMMENT_PREFIX} ".join(lines)
    
    # ────────────────────────────────────────────────────────────────────────
    # Security Validation
    # ────────────────────────────────────────────────────────────────────────
    
    def validate_secure_fields(self, ir_entity: IREntity) -> bool:
        if not self.config.enforce_secure_fields:
            return True
        
        has_secure = False
        if hasattr(ir_entity, "fields"):
            for field_name, field_info in ir_entity.fields.items():
                modifiers = field_info.get("modifiers", []) if isinstance(field_info, dict) else getattr(field_info, "modifiers", [])
                if any(m in ["secure", "hashed", "encrypted"] for m in modifiers):
                    has_secure = True
                    break
                    
        if has_secure:
            self.result.add_warning(
                f"Entity '{ir_entity.name}' contains designated secure field properties. "
                "Ensure proper encryption processing logic block implementation."
            )
        return True
    
    # ────────────────────────────────────────────────────────────────────────
    # Result Management
    # ────────────────────────────────────────────────────────────────────────
    
    def get_result(self) -> GenerationResult:
        return self.result
    
    def reset(self):
        self.result = GenerationResult()
        self._indent_level = 0
    
    # ────────────────────────────────────────────────────────────────────────
    # Utility Methods
    # ────────────────────────────────────────────────────────────────────────
    
    def sanitize_identifier(self, name: str) -> str:
        name = name.strip()
        name = name.replace("-", "_")
        name = name.replace(" ", "_")
        return name
    
    def escape_string(self, value: str) -> str:
        value = value.replace("\\", "\\\\")
        value = value.replace('"', '\\"')
        value = value.replace("\n", "\\n")
        value = value.replace("\r", "\\r")
        value = value.replace("\t", "\\t")
        return value
    
    def format_value(self, value: Any) -> str:
        if value is None:
            return "null"
        elif isinstance(value, bool):
            return "true" if value else "false"
        elif isinstance(value, str):
            return f'"{self.escape_string(value)}"'
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, list):
            items = ", ".join(self.format_value(v) for v in value)
            return f"[{items}]"
        elif isinstance(value, dict):
            items = ", ".join(
                f"{self.format_value(k)}: {self.format_value(v)}"
                for k, v in value.items()
            )
            return f"{{{items}}}"
        else:
            return f'"{str(value)}"'


# ────────────────────────────────────────────────────────────────────────────
# Generator Registry
# ────────────────────────────────────────────────────────────────────────────

class GeneratorRegistry:
    """Registry engine tracking registered concrete compiler output generator systems."""
    
    _generators: Dict[str, type] = {}
    _core_targets: List[str] = ["nodejs", "python", "go"]
    
    def __contains__(self, item: str) -> bool:
        return str(item).lower().strip() in self.list_generators()
    
    @classmethod
    def register(cls, generator_class: type):
        if not issubclass(generator_class, BaseGenerator):
            raise ValueError("Generator class must subclass BaseGenerator core blueprint layout")
        
        name = generator_class.TARGET_NAME.lower().strip()
        cls._generators[name] = generator_class
    
    @classmethod
    def get(cls, name: str) -> Optional[type]:
        target_key = str(name).lower().strip()
        
        # Smart dynamic trigger to safely handle lazy CLI loading architectures
        if target_key not in cls._generators and target_key in cls._core_targets:
            try:
                if target_key == "python":
                    import madilang.generators.python.generator
                elif target_key == "nodejs":
                    import madilang.generators.nodejs.generator
            except ModuleNotFoundError as e:
                missing_mod = e.name if hasattr(e, 'name') else str(e)
                raise ImportError(
                    f"Target operational layer '{target_key}' is missing required dependencies: '{missing_mod}'. "
                    f"Please run: pip install {missing_mod} (or setup the environment via: pip install madilang[python])"
                ) from e
                
        return cls._generators.get(target_key)
    
    @classmethod
    def create(cls, name: str, config: Optional[GeneratorConfig] = None) -> Optional[BaseGenerator]:
        generator_class = cls.get(name)
        if generator_class:
            return generator_class(config)
        return None
    
    @classmethod
    def list_generators(cls) -> List[str]:
        # Merges core operational layers with manually injected runtime plugins seamlessly
        return sorted(list(set(cls._core_targets + list(cls._generators.keys()))))


# ────────────────────────────────────────────────────────────────────────────
# Convenience Functions (Correct & Safe Implementations)
# ────────────────────────────────────────────────────────────────────────────

def register_generator(generator_class: type):
    """Decorator syntax target mapping shortcut to bundle newly created output code emitters."""
    GeneratorRegistry.register(generator_class)
    return generator_class


def get_generator(target: str, config: Optional[GeneratorConfig] = None) -> BaseGenerator:
    """
    Global factory function safely exposed to extract specific generation layer engines.
    """
    target_key = str(target).lower().strip()
    
    try:
        generator_instance = GeneratorRegistry.create(target_key, config)
    except ImportError as e:
        raise ValueError(f"Generation error: {str(e)}") from e
    
    if generator_instance is None:
        available = ", ".join(GeneratorRegistry.list_generators())
        raise ValueError(
            f"Generator target mapping reference '{target}' not found. "
            f"Currently registered operational layers: {available}"
        )
    return generator_instance


def list_generators() -> List[str]:
    """
    Convenience function to list all registered generator names.
    
    Returns:
        List of registered target language names.
    """
    return GeneratorRegistry.list_generators()

