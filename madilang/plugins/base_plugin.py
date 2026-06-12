# ════════════════════════════════════════════════════════════════════════════
# 🧠 MadiLang — Plugin System Base (Refined)
# ════════════════════════════════════════════════════════════════════════════
# Sovereign plugin architecture for extensible ethics, security, and tools.
# Status: v0.4.0 • Sovereign-by-Design • Extensible Core
# ════════════════════════════════════════════════════════════════════════════

"""
MadiLang Plugin System

This module defines the base plugin architecture that enables extending
MadiLang without modifying the core.
"""

import importlib
import pkgutil
import warnings
from abc import ABC, abstractmethod
from typing import (
    Any, Dict, List, Optional, Callable, Type, Union, Tuple
)
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
import json

from madilang.compiler.ast_nodes import ProgramNode, ASTNode
from madilang.ir.models import IRProgram, IRNode


# ────────────────────────────────────────────────────────────────────────────
# Plugin Enums
# ────────────────────────────────────────────────────────────────────────────

class PluginHook(Enum):
    """Available plugin hook points."""
    PRE_PARSE = auto()
    POST_PARSE = auto()
    PRE_ANALYSIS = auto()
    POST_ANALYSIS = auto()
    PRE_COMPILE = auto()
    POST_COMPILE = auto()
    PRE_GENERATE = auto()
    POST_GENERATE = auto()
    PRE_SIGN = auto()
    POST_SIGN = auto()


class PluginPriority(Enum):
    """Plugin execution priority."""
    CRITICAL = 0      # Runs first (security, ethics)
    HIGH = 10
    NORMAL = 50
    LOW = 90
    LAST = 100        # Runs last (formatting, logging)


class PluginStatus(Enum):
    """Plugin lifecycle status."""
    LOADED = auto()
    ACTIVE = auto()
    DISABLED = auto()
    ERROR = auto()


# ────────────────────────────────────────────────────────────────────────────
# Plugin Metadata
# ────────────────────────────────────────────────────────────────────────────

@dataclass
class PluginMetadata:
    """Plugin metadata for discovery and management."""
    name: str
    version: str
    description: str
    author: str
    hooks: List[PluginHook] = field(default_factory=list)
    priority: PluginPriority = PluginPriority.NORMAL
    requires: List[str] = field(default_factory=list)
    optional: List[str] = field(default_factory=list)
    enabled_by_default: bool = True
    
    ethics_related: bool = False
    security_related: bool = False
    audit_required: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "hooks": [h.name for h in self.hooks],
            "priority": self.priority.name,
            "requires": self.requires,
            "optional": self.optional,
            "enabled_by_default": self.enabled_by_default,
            "ethics_related": self.ethics_related,
            "security_related": self.security_related,
            "audit_required": self.audit_required,
        }


# ────────────────────────────────────────────────────────────────────────────
# Plugin Context
# ────────────────────────────────────────────────────────────────────────────

@dataclass
class PluginContext:
    """Context passed to plugin hooks tracking structural changes."""
    source: Optional[str] = None
    ast: Optional[ProgramNode] = None
    ir: Optional[IRProgram] = None
    generated_code: Optional[str] = None
    generated_files: Dict[str, str] = field(default_factory=dict)
    
    shared: Dict[str, Any] = field(default_factory=dict)
    config: Dict[str, Any] = field(default_factory=dict)
    
    stop_pipeline: bool = False
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def set_shared(self, key: str, value: Any):
        self.shared[key] = value
    
    def get_shared(self, key: str, default: Any = None) -> Any:
        return self.shared.get(key, default)
    
    def add_error(self, message: str, plugin: str = ""):
        self.errors.append(f"[{plugin}] {message}" if plugin else message)
    
    def add_warning(self, message: str, plugin: str = ""):
        self.warnings.append(f"[{plugin}] {message}" if plugin else message)
    
    def stop(self, reason: str = ""):
        self.stop_pipeline = True
        if reason:
            self.add_error(f"Pipeline stopped: {reason}")


# ────────────────────────────────────────────────────────────────────────────
# Base Plugin
# ────────────────────────────────────────────────────────────────────────────

class BasePlugin(ABC):
    """Abstract base class for all MadiLang plugins."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self._status = PluginStatus.LOADED
        self._errors: List[str] = []
        self._warnings: List[str] = []
    
    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        pass
    
    @property
    def status(self) -> PluginStatus:
        return self._status
        
    @status.setter
    def status(self, value: PluginStatus):
        self._status = value
    
    @property
    def name(self) -> str:
        return self.metadata.name
    
    @property
    def priority(self) -> PluginPriority:
        return self.metadata.priority
    
    def initialize(self) -> bool:
        try:
            self._status = PluginStatus.ACTIVE
            return True
        except Exception as e:
            self._errors.append(f"Initialization failed: {e}")
            self._status = PluginStatus.ERROR
            return False
    
    def shutdown(self):
        pass
    
    def is_active(self) -> bool:
        return self._status == PluginStatus.ACTIVE
    
    # Hooks fallbacks
    def pre_parse(self, context: PluginContext) -> Optional[str]: return None
    def post_parse(self, context: PluginContext) -> Optional[ProgramNode]: return None
    def pre_analysis(self, context: PluginContext) -> bool: return True
    def post_analysis(self, context: PluginContext) -> Optional[ProgramNode]: return None
    def pre_compile(self, context: PluginContext) -> bool: return True
    def post_compile(self, context: PluginContext) -> Optional[IRProgram]: return None
    def pre_generate(self, context: PluginContext) -> bool: return True
    def post_generate(self, context: PluginContext) -> Optional[str]: return None
    def pre_sign(self, context: PluginContext) -> Dict[str, Any]: return {}
    def post_sign(self, context: PluginContext) -> bool: return True
    
    def log(self, message: str, level: str = "info"):
        print(f"[{self.name}] {message}")
    
    def get_config(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)
    
    def report_error(self, message: str):
        self._errors.append(message)
    
    def report_warning(self, message: str):
        self._warnings.append(message)
    
    def get_errors(self) -> List[str]:
        return self._errors.copy()
    
    def get_warnings(self) -> List[str]:
        return self._warnings.copy()


# ────────────────────────────────────────────────────────────────────────────
# Plugin Manager
# ────────────────────────────────────────────────────────────────────────────

class PluginManager:
    """Manages secure plugin lifecycle and cascades execution transformations cleanly."""
    
    def __init__(self):
        self._plugins: Dict[str, BasePlugin] = {}
        self._plugin_order: List[str] = []
        self._disabled: set = set()
    
    def register(self, plugin: BasePlugin) -> bool:
        name = plugin.name
        if name in self._plugins:
            warnings.warn(f"Plugin '{name}' already registered, replacing")
        
        # ✅ Fixed: Reject integration if missing core dependency payloads completely
        for req in plugin.metadata.requires:
            if req not in self._plugins:
                warnings.warn(f"Plugin '{name}' rejected: missing absolute dependency requirement: '{req}'")
                plugin.status = PluginStatus.ERROR
                return False
                
        if not plugin.initialize():
            warnings.warn(f"Plugin '{name}' failed initialization sequences")
            return False
        
        self._plugins[name] = plugin
        self._update_order()
        return True
    
    def register_class(self, plugin_class: Type[BasePlugin], config: Dict = None) -> bool:
        try:
            plugin = plugin_class(config or {})
            return self.register(plugin)
        except Exception as e:
            warnings.warn(f"Failed to instantiate plugin class {plugin_class}: {e}")
            return False
    
    def _update_order(self):
        self._plugin_order = sorted(
            self._plugins.keys(),
            key=lambda name: self._plugins[name].priority.value
        )
    
    def enable(self, name: str):
        self._disabled.discard(name)
    
    def disable(self, name: str):
        self._disabled.add(name)
    
    def is_enabled(self, name: str) -> bool:
        return name not in self._disabled
    
    def get_plugin(self, name: str) -> Optional[BasePlugin]:
        return self._plugins.get(name)
    
    def list_plugins(self) -> List[Dict[str, Any]]:
        return [
            {
                **plugin.metadata.to_dict(),
                "status": plugin.status.name,
                "enabled": self.is_enabled(name)
            }
            for name, plugin in self._plugins.items()
        ]
    
    def _execute_hook(
        self,
        hook_name: str,
        context: PluginContext,
        transform: bool = False,
        expected_type: Optional[Type] = None
    ) -> Any:
        """
        Execute a hook across all active plugins with mutations cascade tracking.
        """
        # ✅ Fixed: Protected dynamic snapshot to eliminate mutation scale exceptions
        active_order = list(self._plugin_order)
        
        for name in active_order:
            if not self.is_enabled(name) or name not in self._plugins:
                continue
            
            plugin = self._plugins[name]
            if not plugin.is_active():
                continue
            
            hook = getattr(plugin, hook_name, None)
            if not hook:
                continue
            
            try:
                hook_result = hook(context)
                if context.stop_pipeline:
                    break
                
                # ✅ Fixed: Cascade the mutated transformation into context immediately for subsequent layers
                if transform and hook_result is not None:
                    if expected_type and not isinstance(hook_result, expected_type):
                        context.add_error(
                            f"Type boundary failure in plugin '{name}' hook '{hook_name}': "
                            f"Expected {expected_type.__name__}, got {type(hook_result).__name__}",
                            name
                        )
                        continue
                    
                    # Store dynamic pipeline transformation step immediately inside context
                    if hook_name in ("pre_parse", "post_generate"):
                        if hook_name == "pre_parse": context.source = hook_result
                        else: context.generated_code = hook_result
                    elif hook_name in ("post_parse", "post_analysis"):
                        context.ast = hook_result
                    elif hook_name == "post_compile":
                        context.ir = hook_result
                        
            except Exception as e:
                context.add_error(f"Plugin '{name}' failed runtime execution in {hook_name}: {e}", name)
        
        # Resolve clean terminal boundary output tracking values
        if hook_name == "pre_parse": return context.source
        if hook_name in ("post_parse", "post_analysis"): return context.ast
        if hook_name == "post_compile": return context.ir
        if hook_name == "post_generate": return context.generated_code
        return None
    
    def run_pre_parse(self, context: PluginContext) -> str:
        return self._execute_hook("pre_parse", context, transform=True, expected_type=str)
    
    def run_post_parse(self, context: PluginContext) -> ProgramNode:
        return self._execute_hook("post_parse", context, transform=True, expected_type=ProgramNode)
    
    def run_pre_analysis(self, context: PluginContext) -> bool:
        self._execute_hook("pre_analysis", context, transform=False)
        return not context.stop_pipeline
    
    def run_post_analysis(self, context: PluginContext) -> ProgramNode:
        return self._execute_hook("post_analysis", context, transform=True, expected_type=ProgramNode)
    
    def run_pre_compile(self, context: PluginContext) -> bool:
        self._execute_hook("pre_compile", context, transform=False)
        return not context.stop_pipeline
    
    def run_post_compile(self, context: PluginContext) -> IRProgram:
        return self._execute_hook("post_compile", context, transform=True, expected_type=IRProgram)
    
    def run_pre_generate(self, context: PluginContext) -> bool:
        self._execute_hook("pre_generate", context, transform=False)
        return not context.stop_pipeline
    
    def run_post_generate(self, context: PluginContext) -> str:
        return self._execute_hook("post_generate", context, transform=True, expected_type=str)
    
    def run_pre_sign(self, context: PluginContext) -> Dict[str, Any]:
        metadata = {}
        active_order = list(self._plugin_order)
        
        for name in active_order:
            if not self.is_enabled(name) or name not in self._plugins:
                continue
            
            plugin = self._plugins[name]
            if not plugin.is_active():
                continue
            
            hook = getattr(plugin, "pre_sign", None)
            if not hook:
                continue
            
            try:
                plugin_meta = hook(context)
                if plugin_meta and isinstance(plugin_meta, dict):
                    metadata[name] = plugin_meta
            except Exception as e:
                context.add_error(f"Plugin '{name}' pre_sign execution collapsed: {e}")
        
        return metadata
    
    def run_post_sign(self, context: PluginContext) -> bool:
        self._execute_hook("post_sign", context, transform=False)
        return not context.stop_pipeline
    
    def shutdown_all(self):
        for plugin in list(self._plugins.values()):
            try:
                plugin.shutdown()
            except Exception:
                pass


# ────────────────────────────────────────────────────────────────────────────
# Plugin Discovery
# ────────────────────────────────────────────────────────────────────────────

def discover_plugins(package_name: str = "madilang.plugins") -> List[Type[BasePlugin]]:
    """Discover fully compliant plugins within structural packages safely."""
    plugins = []
    try:
        package = importlib.import_module(package_name)
        for _, mod_name, _ in pkgutil.iter_modules(package.__path__):
            try:
                mod = importlib.import_module(f"{package_name}.{mod_name}")
                for attr_name in dir(mod):
                    attr = getattr(mod, attr_name)
                    if (
                        isinstance(attr, type) and
                        issubclass(attr, BasePlugin) and
                        attr != BasePlugin
                    ):
                        plugins.append(attr)
            except ImportError:
                continue
    except ImportError:
        pass
    return plugins


# ────────────────────────────────────────────────────────────────────────────
# Global Plugin Manager
# ────────────────────────────────────────────────────────────────────────────

_plugin_manager: Optional[PluginManager] = None


def get_plugin_manager() -> PluginManager:
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = PluginManager()
    return _plugin_manager


def register_plugin(plugin: Union[BasePlugin, Type[BasePlugin]], config: Dict = None):
    manager = get_plugin_manager()
    if isinstance(plugin, type):
        manager.register_class(plugin, config)
    else:
        manager.register(plugin)

