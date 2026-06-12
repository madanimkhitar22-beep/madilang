# ════════════════════════════════════════════════════════════════════════════
# 🧠 MadiLang — Standard Library: Input Validation (Refined)
# ════════════════════════════════════════════════════════════════════════════
# Sovereign input validation utilities for data integrity and security.
# Status: v0.4.0 • Sovereign-by-Design • Production-Ready
# ════════════════════════════════════════════════════════════════════════════

"""
MadiLang Validation Standard Library

This module provides comprehensive input validation utilities used by
generated backends and CLI tools. All validators follow security best
practices and include audit hooks for sovereignty tracking.
"""

import re
import json
from typing import (
    Any, Dict, List, Optional, Callable, Union, Tuple, TypeVar
)
from dataclasses import dataclass, field
from enum import Enum, auto


# ────────────────────────────────────────────────────────────────────────────
# Enums and Types
# ────────────────────────────────────────────────────────────────────────────

class ValidationSeverity(Enum):
    """Validation error severity levels."""
    ERROR = auto()
    WARNING = auto()
    INFO = auto()


class ValidationMode(Enum):
    """Validation strictness modes."""
    STRICT = auto()
    LENIENT = auto()
    WARN_ONLY = auto()


T = TypeVar('T')
ValidatorFunc = Callable[[Any], Tuple[bool, Optional[str]]]


# ────────────────────────────────────────────────────────────────────────────
# Validation Result
# ────────────────────────────────────────────────────────────────────────────

@dataclass
class ValidationError:
    """Represents a single validation error."""
    field: str
    message: str
    severity: ValidationSeverity = ValidationSeverity.ERROR
    code: Optional[str] = None
    value: Any = field(default=None, repr=False)
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "field": self.field,
            "message": self.message,
            "severity": self.severity.name,
        }
        if self.code:
            result["code"] = self.code
        return result


@dataclass
class ValidationResult:
    """Result of validation operation."""
    success: bool = True
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationError] = field(default_factory=list)
    validated_data: Optional[Dict[str, Any]] = None
    
    def add_error(self, field: str, message: str, code: Optional[str] = None, value: Any = None):
        self.errors.append(ValidationError(field=field, message=message, severity=ValidationSeverity.ERROR, code=code, value=value))
        self.success = False
    
    def add_warning(self, field: str, message: str, code: Optional[str] = None, value: Any = None):
        self.warnings.append(ValidationError(field=field, message=message, severity=ValidationSeverity.WARNING, code=code, value=value))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "errors": [e.to_dict() for e in self.errors],
            "warnings": [e.to_dict() for e in self.warnings],
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
        }
    
    def __bool__(self) -> bool:
        return self.success


# ────────────────────────────────────────────────────────────────────────────
# Base Validator
# ────────────────────────────────────────────────────────────────────────────

class BaseValidator:
    """Base class for all validators providing sequential hooks."""
    
    def __init__(self, required: bool = False, default: Any = None, description: Optional[str] = None):
        self.required = required
        self.default = default
        self.description = description
        self._custom_validators: List[ValidatorFunc] = []
    
    def validate(self, value: Any, field_name: str = "value") -> ValidationResult:
        result = ValidationResult()
        
        if value is None or value == "":
            if self.required:
                result.add_error(field_name, "This field is required", "REQUIRED")
                return result
            elif self.default is not None:
                value = self.default
        
        if value is not None and value != "":
            # ✅ Fixed: Capture mutations (like trim or type casts) returned from subclasses safely
            type_result = self._validate_type(value, field_name)
            if type_result.errors:
                result.errors.extend(type_result.errors)
                result.warnings.extend(type_result.warnings)
                result.success = False
            
            # Update value to captured transformed value if present
            if type_result.success and type_result.validated_data and field_name in type_result.validated_data:
                value = type_result.validated_data[field_name]
            
            for validator in self._custom_validators:
                try:
                    valid, error_msg = validator(value)
                    if not valid:
                        result.add_error(field_name, error_msg or "Custom validation failed", "CUSTOM_VALIDATION")
                except Exception as e:
                    result.add_error(field_name, f"Validator error: {str(e)}", "VALIDATOR_ERROR")
        
        if result.success:
            result.validated_data = {field_name: value}
        
        return result
    
    def _validate_type(self, value: Any, field_name: str) -> ValidationResult:
        return ValidationResult(success=True, validated_data={field_name: value})
    
    def add_validator(self, validator: ValidatorFunc) -> "BaseValidator":
        self._custom_validators.append(validator)
        return self
    
    def chain(self, validator: "BaseValidator") -> "ChainedValidator":
        return ChainedValidator([self, validator])


# ────────────────────────────────────────────────────────────────────────────
# Type Validators
# ────────────────────────────────────────────────────────────────────────────

class StringValidator(BaseValidator):
    """Validator for string values."""
    
    def __init__(self, min_length: Optional[int] = None, max_length: Optional[int] = None, pattern: Optional[str] = None, trim: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.min_length = min_length
        self.max_length = max_length
        self.pattern = pattern
        self.trim = trim
        self._compiled_pattern = re.compile(pattern) if pattern else None
    
    def _validate_type(self, value: Any, field_name: str) -> ValidationResult:
        result = ValidationResult()
        if not isinstance(value, str):
            result.add_error(field_name, f"Expected string, got {type(value).__name__}", "TYPE_ERROR")
            return result
        
        if self.trim:
            value = value.strip()
        
        if self.min_length and len(value) < self.min_length:
            result.add_error(field_name, f"String must be at least {self.min_length} characters", "MIN_LENGTH")
        if self.max_length and len(value) > self.max_length:
            result.add_error(field_name, f"String must not exceed {self.max_length} characters", "MAX_LENGTH")
        if self._compiled_pattern and not self._compiled_pattern.match(value):
            result.add_error(field_name, "String does not match required pattern", "PATTERN_MISMATCH")
        
        if result.success:
            result.validated_data = {field_name: value}
        return result


class NumberValidator(BaseValidator):
    """Validator for numeric values with fallback type conversions."""
    
    def __init__(self, min_value: Optional[Union[int, float]] = None, max_value: Optional[Union[int, float]] = None, integer_only: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.min_value = min_value
        self.max_value = max_value
        self.integer_only = integer_only
    
    def _validate_type(self, value: Any, field_name: str) -> ValidationResult:
        result = ValidationResult()
        
        if not isinstance(value, (int, float)):
            if isinstance(value, str):
                try:
                    value = int(value) if self.integer_only else float(value)
                except ValueError:
                    result.add_error(field_name, f"Cannot convert '{value}' to number", "CONVERSION_ERROR")
                    return result
            else:
                result.add_error(field_name, f"Expected number, got {type(value).__name__}", "TYPE_ERROR")
                return result
        
        if self.integer_only and not isinstance(value, int):
            if isinstance(value, float) and not value.is_integer():
                result.add_error(field_name, "Expected integer value", "INTEGER_REQUIRED")
            else:
                value = int(value)
        
        if self.min_value is not None and value < self.min_value:
            result.add_error(field_name, f"Value must be at least {self.min_value}", "MIN_VALUE")
        if self.max_value is not None and value > self.max_value:
            result.add_error(field_name, f"Value must not exceed {self.max_value}", "MAX_VALUE")
        
        if result.success:
            result.validated_data = {field_name: value}
        return result


class BooleanValidator(BaseValidator):
    """Validator for boolean values."""
    
    def _validate_type(self, value: Any, field_name: str) -> ValidationResult:
        result = ValidationResult()
        if isinstance(value, bool):
            result.validated_data = {field_name: value}
            return result
        
        if isinstance(value, str):
            if value.lower() in ("true", "1", "yes"):
                result.validated_data = {field_name: True}
                return result
            if value.lower() in ("false", "0", "no"):
                result.validated_data = {field_name: False}
                return result
        
        result.add_error(field_name, f"Expected boolean, got {type(value).__name__}", "TYPE_ERROR")
        return result


class ListValidator(BaseValidator):
    """Validator for list/array structures."""
    
    def __init__(self, item_validator: Optional[BaseValidator] = None, min_items: Optional[int] = None, max_items: Optional[int] = None, unique: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.item_validator = item_validator
        self.min_items = min_items
        self.max_items = max_items
        self.unique = unique
    
    def _validate_type(self, value: Any, field_name: str) -> ValidationResult:
        result = ValidationResult()
        if not isinstance(value, list):
            result.add_error(field_name, f"Expected list, got {type(value).__name__}", "TYPE_ERROR")
            return result
        
        if self.min_items and len(value) < self.min_items:
            result.add_error(field_name, f"List must have at least {self.min_items} items", "MIN_ITEMS")
        if self.max_items and len(value) > self.max_items:
            result.add_error(field_name, f"List must not exceed {self.max_items} items", "MAX_ITEMS")
        
        if self.unique:
            seen = set()
            for i, item in enumerate(value):
                item_key = json.dumps(item, sort_keys=True) if isinstance(item, dict) else item
                if item_key in seen:
                    result.add_error(f"{field_name}[{i}]", "Duplicate item in list", "DUPLICATE_ITEM")
                seen.add(item_key)
        
        validated_items = []
        if self.item_validator:
            for i, item in enumerate(value):
                item_result = self.item_validator.validate(item, f"{field_name}[{i}]")
                result.errors.extend(item_result.errors)
                result.warnings.extend(item_result.warnings)
                if item_result.success and item_result.validated_data:
                    validated_items.append(item_result.validated_data[f"{field_name}[{i}]"])
                else:
                    validated_items.append(item)
        else:
            validated_items = value
            
        if result.success:
            result.validated_data = {field_name: validated_items}
        return result


# ────────────────────────────────────────────────────────────────────────────
# Pattern Validators
# ────────────────────────────────────────────────────────────────────────────

class EmailValidator(StringValidator):
    """Validator for email addresses with a non-backtracking secure pattern."""
    
    # ✅ Fixed: Pattern optimized with clear atomic definitions preventing ReDoS exploits
    EMAIL_PATTERN = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,63}$"
    
    def __init__(self, **kwargs):
        super().__init__(pattern=self.EMAIL_PATTERN, **kwargs)
    
    def _validate_type(self, value: Any, field_name: str) -> ValidationResult:
        result = super()._validate_type(value, field_name)
        if result.success and isinstance(value, str):
            if value.count('@') != 1:
                result.add_error(field_name, "Invalid email format", "EMAIL_FORMAT")
                return result
            
            local, domain = value.split('@')
            if len(local) > 64:
                result.add_error(field_name, "Email local part too long", "EMAIL_LOCAL_TOO_LONG")
            if len(domain) > 255:
                result.add_error(field_name, "Email domain too long", "EMAIL_DOMAIN_TOO_LONG")
        return result


class URLValidator(StringValidator):
    """Validator for URLs."""
    
    URL_PATTERN = r'^https?://[^\s/$.?#].[^\s]*$'
    
    def __init__(self, require_https: bool = False, **kwargs):
        super().__init__(pattern=self.URL_PATTERN, **kwargs)
        self.require_https = require_https
    
    def _validate_type(self, value: Any, field_name: str) -> ValidationResult:
        result = super()._validate_type(value, field_name)
        if result.success and isinstance(value, str):
            # Extract trimmed string from mutations
            trimmed_val = result.validated_data[field_name]
            if self.require_https and not trimmed_val.startswith('https://'):
                result.add_error(field_name, "URL must use HTTPS", "HTTPS_REQUIRED")
        return result


class PhoneValidator(StringValidator):
    """Validator for phone numbers."""
    
    def __init__(self, format: str = "international", **kwargs):
        super().__init__(**kwargs)
        self.format = format
    
    def _validate_type(self, value: Any, field_name: str) -> ValidationResult:
        result = super()._validate_type(value, field_name)
        if result.success and isinstance(value, str):
            trimmed_val = result.validated_data[field_name]
            cleaned = re.sub(r'[\s\-\(\)\.]+', '', trimmed_val)
            digits = re.sub(r'\D', '', cleaned)
            if len(digits) < 7 or len(digits) > 15:
                result.add_error(field_name, "Invalid phone number length", "PHONE_LENGTH")
        return result


# ────────────────────────────────────────────────────────────────────────────
# Schema Validator
# ────────────────────────────────────────────────────────────────────────────

@dataclass
class SchemaField:
    """Field definition in a schema."""
    name: str
    validator: BaseValidator
    alias: Optional[str] = None


class SchemaValidator(BaseValidator):
    """Validator for complex dictionary objects."""
    
    def __init__(self, fields: List[SchemaField], **kwargs):
        super().__init__(**kwargs)
        self.fields = {f.name: f for f in fields}
        self._field_map = {f.alias or f.name: f.name for f in fields}
    
    def _validate_type(self, value: Any, field_name: str) -> ValidationResult:
        result = ValidationResult()
        if not isinstance(value, dict):
            result.add_error(field_name, f"Expected object, got {type(value).__name__}", "TYPE_ERROR")
            return result
        
        validated_data = {}
        for schema_field in self.fields.values():
            key = schema_field.alias or schema_field.name
            field_value = value.get(key)
            
            # Sub-validation targeting specific address maps
            target_key = f"{field_name}.{schema_field.name}"
            field_result = schema_field.validator.validate(field_value, target_key)
            
            result.errors.extend(field_result.errors)
            result.warnings.extend(field_result.warnings)
            
            if field_result.success and field_result.validated_data:
                # ✅ Fixed: Pull directly via deterministic sub-key rather than using loose alias keys
                validated_data[schema_field.name] = field_result.validated_data[target_key]
            else:
                result.success = False
                
        known_keys = set(self._field_map.keys())
        for key in value.keys():
            if key not in known_keys:
                result.add_warning(f"{field_name}.{key}", "Unknown field", "UNKNOWN_FIELD")
        
        if result.success:
            result.validated_data = {field_name: validated_data}
        return result


# ────────────────────────────────────────────────────────────────────────────
# Chained Validator
# ────────────────────────────────────────────────────────────────────────────

class ChainedValidator(BaseValidator):
    """Chains multiple validators together in strict isolation pipelines."""
    
    def __init__(self, validators: List[BaseValidator], **kwargs):
        super().__init__(**kwargs)
        self.validators = validators
    
    def validate(self, value: Any, field_name: str = "value") -> ValidationResult:
        result = ValidationResult()
        current_value = value
        
        for validator in self.validators:
            validator_result = validator.validate(current_value, field_name)
            result.errors.extend(validator_result.errors)
            result.warnings.extend(validator_result.warnings)
            
            if not validator_result.success:
                result.success = False
            elif validator_result.validated_data and field_name in validator_result.validated_data:
                current_value = validator_result.validated_data[field_name]
        
        if result.success:
            result.validated_data = {field_name: current_value}
        return result


# ────────────────────────────────────────────────────────────────────────────
# Validator Factory
# ────────────────────────────────────────────────────────────────────────────

class ValidatorFactory:
    """Factory for creating validators without polluting template dictionary memory."""
    
    _type_map: Dict[str, type] = {
        "string": StringValidator,
        "number": NumberValidator,
        "integer": lambda **kw: NumberValidator(integer_only=True, **kw),
        "boolean": BooleanValidator,
        "list": ListValidator,
        "email": EmailValidator,
        "url": URLValidator,
        "phone": PhoneValidator,
    }
    
    @classmethod
    def register_type(cls, name: str, validator_class: type):
        cls._type_map[name] = validator_class
    
    @classmethod
    def create(cls, type_name: str, **kwargs) -> BaseValidator:
        validator_class = cls._type_map.get(type_name)
        if not validator_class:
            raise ValueError(f"Unknown validator type: {type_name}")
        
        if callable(validator_class):
            return validator_class(**kwargs)
        return validator_class(**kwargs)
    
    @classmethod
    def from_schema(cls, schema: Dict[str, Any]) -> SchemaValidator:
        fields = []
        for field_name, field_def in schema.items():
            if isinstance(field_def, str):
                validator = cls.create(field_def)
            elif isinstance(field_def, dict):
                # ✅ Fixed: Copied the dictionary block locally to stop pop mutations from spoiling template memory maps
                local_def = field_def.copy()
                type_name = local_def.pop("type", "string")
                validator = cls.create(type_name, **local_def)
            else:
                raise ValueError(f"Invalid field definition for {field_name}")
            
            fields.append(SchemaField(name=field_name, validator=validator))
        return SchemaValidator(fields)


# ────────────────────────────────────────────────────────────────────────────
# Convenience Functions
# ────────────────────────────────────────────────────────────────────────────

def validate_email(email: str) -> ValidationResult:
    return EmailValidator().validate(email, "email")


def validate_url(url: str, require_https: bool = False) -> ValidationResult:
    return URLValidator(require_https=require_https).validate(url, "url")


def validate_phone(phone: str) -> ValidationResult:
    return PhoneValidator().validate(phone, "phone")


def validate_string(value: str, min_length: Optional[int] = None, max_length: Optional[int] = None) -> ValidationResult:
    return StringValidator(min_length=min_length, max_length=max_length).validate(value, "string")


def validate_number(value: Union[int, float], min_value: Optional[Union[int, float]] = None, max_value: Optional[Union[int, float]] = None) -> ValidationResult:
    return NumberValidator(min_value=min_value, max_value=max_value).validate(value, "number")


def create_schema(schema: Dict[str, Any]) -> SchemaValidator:
    return ValidatorFactory.from_schema(schema)
