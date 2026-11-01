"""MadiLang plugin package."""

from madilang.plugins.base_plugin import BasePlugin, PluginContext, PluginHook
from madilang.plugins.ethics_hook import EthicsHookPlugin, evaluate_ethics
from madilang.plugins.security_hook import SecurityHookPlugin

__all__ = [
    "BasePlugin", "PluginContext", "PluginHook",
    "EthicsHookPlugin", "evaluate_ethics", "SecurityHookPlugin",
]
