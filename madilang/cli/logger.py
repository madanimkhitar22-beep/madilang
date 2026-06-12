# ════════════════════════════════════════════════════════════════════════════
# 🧠 MadiLang — CLI Logger & Output Formatter (Refined)
# ════════════════════════════════════════════════════════════════════════════
# Sovereign logging with color, emoji, and audit support.
# Status: v0.4.0 • Mobile-First • Terminal-Optimized
# ════════════════════════════════════════════════════════════════════════════

"""
MadiLang CLI Logger

This module provides a lightweight, mobile-friendly logging system for the CLI.
It supports colored output, emoji indicators, log levels, and audit logging
for sovereignty tracking.
"""

import sys
import os
import json
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, TextIO
from enum import Enum, auto
from dataclasses import dataclass, field
from pathlib import Path


# ────────────────────────────────────────────────────────────────────────────
# Log Levels
# ────────────────────────────────────────────────────────────────────────────

class LogLevel(Enum):
    """Log severity levels."""
    DEBUG = auto()
    INFO = auto()
    SUCCESS = auto()
    WARNING = auto()
    ERROR = auto()
    CRITICAL = auto()
    
    def __lt__(self, other):
        return self.value < other.value
    
    def __le__(self, other):
        return self.value <= other.value


# ────────────────────────────────────────────────────────────────────────────
# Color Codes (ANSI)
# ────────────────────────────────────────────────────────────────────────────

class Color:
    """ANSI color codes with safe fallback."""
    
    # Check if terminal supports colors
    _supports_color = (
        hasattr(sys.stdout, "isatty") and 
        sys.stdout.isatty() and
        os.getenv("NO_COLOR") is None and
        os.getenv("TERM") != "dumb"
    )
    
    RESET = "\033[0m" if _supports_color else ""
    
    BLACK = "\033[30m" if _supports_color else ""
    RED = "\033[31m" if _supports_color else ""
    GREEN = "\033[32m" if _supports_color else ""
    YELLOW = "\033[33m" if _supports_color else ""
    BLUE = "\033[34m" if _supports_color else ""
    MAGENTA = "\033[35m" if _supports_color else ""
    CYAN = "\033[36m" if _supports_color else ""
    WHITE = "\033[37m" if _supports_color else ""
    
    BRIGHT_RED = "\033[91m" if _supports_color else ""
    BRIGHT_GREEN = "\033[92m" if _supports_color else ""
    BRIGHT_YELLOW = "\033[93m" if _supports_color else ""
    BRIGHT_BLUE = "\033[94m" if _supports_color else ""
    BRIGHT_MAGENTA = "\033[95m" if _supports_color else ""
    BRIGHT_CYAN = "\033[96m" if _supports_color else ""
    
    BOLD = "\033[1m" if _supports_color else ""
    DIM = "\033[2m" if _supports_color else ""
    UNDERLINE = "\033[4m" if _supports_color else ""
    
    @classmethod
    def colorize(cls, text: str, color: str) -> str:
        """Apply color to text."""
        if not cls._supports_color:
            return text
        return f"{color}{text}{cls.RESET}"
    
    @classmethod
    def bold(cls, text: str) -> str:
        """Make text bold."""
        return cls.colorize(text, cls.BOLD)


# ────────────────────────────────────────────────────────────────────────────
# Log Entry
# ────────────────────────────────────────────────────────────────────────────

@dataclass
class LogEntry:
    """Represents a single log entry."""
    level: LogLevel
    message: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    emoji: str = ""
    color: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def format(self, include_timestamp: bool = True) -> str:
        """Format log entry for display."""
        parts = []
        
        if include_timestamp:
            ts = self.timestamp.strftime("%H:%M:%S")
            parts.append(Color.colorize(f"[{ts}]", Color.DIM))
        
        if self.emoji:
            parts.append(self.emoji)
        
        level_str = self.level.name
        if self.color:
            level_str = Color.colorize(level_str, self.color)
        parts.append(f"[{level_str}]")
        
        parts.append(self.message)
        
        return " ".join(parts)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON output."""
        return {
            "level": self.level.name,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }


# ────────────────────────────────────────────────────────────────────────────
# CLI Logger
# ────────────────────────────────────────────────────────────────────────────

class CLILogger:
    """Command-line logger with color, emoji, and audit support."""
    
    LEVEL_CONFIG = {
        LogLevel.DEBUG: {"emoji": "🔍", "color": Color.CYAN},
        LogLevel.INFO: {"emoji": "ℹ️", "color": Color.BLUE},
        LogLevel.SUCCESS: {"emoji": "✅", "color": Color.GREEN},
        LogLevel.WARNING: {"emoji": "⚠️", "color": Color.YELLOW},
        LogLevel.ERROR: {"emoji": "❌", "color": Color.RED},
        LogLevel.CRITICAL: {"emoji": "🚨", "color": Color.BRIGHT_RED},
    }
    
    def __init__(
        self,
        level: LogLevel = LogLevel.INFO,
        output: TextIO = sys.stdout,
        error_output: TextIO = sys.stderr,
        audit_file: Optional[str] = None,
        json_output: bool = False
    ):
        self.level = level
        self.output = output
        self.error_output = error_output
        self.json_output = json_output
        self._entries: List[LogEntry] = []
        self._audit_enabled = audit_file is not None
        self._audit_file = Path(audit_file) if audit_file else None
        
        if self._audit_enabled and self._audit_file:
            try:
                self._audit_file.parent.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                self.error_output.write(f"⚠️ [MadiLang] Fallback: Failed to create audit folder: {e}\n")
    
    def set_level(self, level: LogLevel):
        """Set minimum log level."""
        self.level = level
    
    def enable_audit(self, audit_file: str):
        """Enable audit logging to file."""
        self._audit_enabled = True
        self._audit_file = Path(audit_file)
        try:
            self._audit_file.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            self.error_output.write(f"⚠️ [MadiLang] Fallback: Failed to initialize dynamic audit trail: {e}\n")
    
    def disable_audit(self):
        """Disable audit logging."""
        self._audit_enabled = False
    
    def _should_log(self, level: LogLevel) -> bool:
        """Check if level should be logged."""
        return level >= self.level
    
    def _write(self, entry: LogEntry):
        """Write log entry to output with fallback serializer."""
        self._entries.append(entry)
        
        if self.json_output:
            # ✅ Fixed: Added default=str serializer to completely bypass object serialization crashes
            self.output.write(json.dumps(entry.to_dict(), default=str) + "\n")
        else:
            formatted = entry.format()
            if entry.level in (LogLevel.ERROR, LogLevel.CRITICAL):
                self.error_output.write(formatted + "\n")
            else:
                self.output.write(formatted + "\n")
        
        self.output.flush()
        self.error_output.flush()
        
        if self._audit_enabled and self._audit_file:
            self._write_audit(entry)
    
    def _write_audit(self, entry: LogEntry):
        """Write entry to audit file with transparent safety boundaries."""
        try:
            audit_entry = {
                **entry.to_dict(),
                "emoji": entry.emoji,
            }
            with open(self._audit_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(audit_entry, default=str) + "\n")
        except Exception as e:
            # ✅ Fixed: Swapped silent failure with descriptive error tracking on fallback channels
            self.error_output.write(f"⚠️ [MadiLang Sovereign Leak] Integrity failure writing audit records: {e}\n")
    
    def _log(self, level: LogLevel, message: str, metadata: Optional[Dict[str, Any]] = None):
        """Internal log method."""
        if not self._should_log(level):
            return
        
        config = self.LEVEL_CONFIG.get(level, {"emoji": "", "color": ""})
        entry = LogEntry(
            level=level,
            message=message,
            emoji=config["emoji"],
            color=config["color"],
            metadata=metadata or {}
        )
        self._write(entry)
    
    # ────────────────────────────────────────────────────────────────────────
    # Public Log Methods
    # ────────────────────────────────────────────────────────────────────────
    
    def debug(self, message: str, metadata: Optional[Dict[str, Any]] = None):
        self._log(LogLevel.DEBUG, message, metadata)
    
    def info(self, message: str, metadata: Optional[Dict[str, Any]] = None):
        self._log(LogLevel.INFO, message, metadata)
    
    def success(self, message: str, metadata: Optional[Dict[str, Any]] = None):
        self._log(LogLevel.SUCCESS, message, metadata)
    
    def warning(self, message: str, metadata: Optional[Dict[str, Any]] = None):
        self._log(LogLevel.WARNING, message, metadata)
    
    def error(self, message: str, metadata: Optional[Dict[str, Any]] = None):
        self._log(LogLevel.ERROR, message, metadata)
    
    def critical(self, message: str, metadata: Optional[Dict[str, Any]] = None):
        self._log(LogLevel.CRITICAL, message, metadata)
    
    # ────────────────────────────────────────────────────────────────────────
    # Specialized Methods
    # ────────────────────────────────────────────────────────────────────────
    
    def step(self, step_num: int, total: int, message: str):
        """Log a step in a process."""
        # ✅ Fixed: Guard text contamination if structured pipeline mode is configured
        if self.json_output:
            self.info(message, {"step_num": step_num, "total_steps": total})
        else:
            self.info(f"Step {step_num}/{total}: {message}")
    
    def progress(self, message: str, percent: Optional[float] = None):
        """Log progress update safely."""
        if self.json_output:
            self.info(message, {"progress_percent": percent if percent is not None else "pending"})
            return
            
        if percent is not None:
            bar_len = 20
            filled = int(bar_len * percent / 100)
            bar = "█" * filled + "░" * (bar_len - filled)
            self.info(f"[{bar}] {percent:.0f}% {message}")
        else:
            self.info(f"⏳ {message}")
    
    def banner(self, lines: List[str], border: str = "═"):
        """Print a banner."""
        if self.json_output:
            return
        
        max_len = max(len(line) for line in lines) if lines else 0
        border_line = border * (max_len + 4)
        
        self.output.write(f"\n{Color.colorize(border_line, Color.CYAN)}\n")
        for line in lines:
            self.output.write(f"{Color.colorize(f'{border} ', Color.CYAN)}{line.ljust(max_len)} {Color.colorize(border, Color.CYAN)}\n")
        self.output.write(f"{Color.colorize(border_line, Color.CYAN)}\n\n")
        self.output.flush()
    
    def section(self, title: str):
        """Print a section header."""
        if self.json_output:
            return
        self.output.write(f"\n{Color.bold(Color.colorize(f'📦 {title}', Color.MAGENTA))}\n")
        self.output.flush()
    
    # ────────────────────────────────────────────────────────────────────────
    # Audit Methods
    # ────────────────────────────────────────────────────────────────────────
    
    def audit(self, action: str, details: Dict[str, Any], success: bool = True):
        """Log an audit entry for sovereignty tracking."""
        metadata = {
            "action": action,
            "success": success,
            **details
        }
        
        level = LogLevel.SUCCESS if success else LogLevel.ERROR
        message = f"Audit: {action} {'✓' if success else '✗'}"
        
        entry = LogEntry(
            level=level,
            message=message,
            emoji="🔐" if success else "🚫",
            color=Color.GREEN if success else Color.RED,
            metadata=metadata
        )
        
        self._entries.append(entry)
        if self._audit_enabled and self._audit_file:
            self._write_audit(entry)
    
    def get_audit_entries(self) -> List[Dict[str, Any]]:
        """Get all audit entries."""
        return [e.to_dict() for e in self._entries if "action" in e.metadata]
    
    # ────────────────────────────────────────────────────────────────────────
    # Utility Methods
    # ────────────────────────────────────────────────────────────────────────
    
    def get_entries(self) -> List[LogEntry]:
        return self._entries.copy()
    
    def clear(self):
        self._entries.clear()
    
    def has_errors(self) -> bool:
        return any(e.level in (LogLevel.ERROR, LogLevel.CRITICAL) for e in self._entries)
    
    def get_error_count(self) -> int:
        return sum(1 for e in self._entries if e.level in (LogLevel.ERROR, LogLevel.CRITICAL))


# ────────────────────────────────────────────────────────────────────────────
# Global Logger Instance
# ────────────────────────────────────────────────────────────────────────────

_logger: Optional[CLILogger] = None


def get_logger() -> CLILogger:
    """Get or create global logger instance."""
    global _logger
    if _logger is None:
        _logger = CLILogger()
    return _logger


def set_logger(logger: CLILogger):
    """Set global logger instance."""
    global _logger
    _logger = logger


# ────────────────────────────────────────────────────────────────────────────
# Convenience Functions
# ────────────────────────────────────────────────────────────────────────────

def log_debug(message: str, metadata: Optional[Dict[str, Any]] = None):
    get_logger().debug(message, metadata)


def log_info(message: str, metadata: Optional[Dict[str, Any]] = None):
    get_logger().info(message, metadata)


def log_success(message: str, metadata: Optional[Dict[str, Any]] = None):
    get_logger().success(message, metadata)


def log_warning(message: str, metadata: Optional[Dict[str, Any]] = None):
    get_logger().warning(message, metadata)


def log_error(message: str, metadata: Optional[Dict[str, Any]] = None):
    get_logger().error(message, metadata)


def log_audit(action: str, details: Dict[str, Any], success: bool = True):
    get_logger().audit(action, details, success)
