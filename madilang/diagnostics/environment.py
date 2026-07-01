# ════════════════════════════════════════════════════════════════════════════
# 🩺 MadiLang Diagnostics — Environment Checker
# ════════════════════════════════════════════════════════════════════════════
# Verifies system prerequisites for sovereign development.
# ════════════════════════════════════════════════════════════════════════════

import shutil
import subprocess
import os
from pathlib import Path
from typing import Dict, Any, List


class EnvironmentChecker:
    """Checks system environment for MadiLang compatibility."""
    
    MIN_PYTHON = (3, 8)
    MIN_NODE = (18, 0)
    
    def check_all(self) -> Dict[str, Any]:
        """Run all environment checks and return structured report."""
        return {
            "python": self._check_python(),
            "nodejs": self._check_nodejs(),
            "npm": self._check_npm(),
            "permissions": self._check_permissions(),
            "platform": self._get_platform_info(),
        }
    
    def _check_python(self) -> Dict[str, Any]:
        import sys
        version = sys.version_info[:3]
        version_str = ".".join(map(str, version))
        ok = version >= self.MIN_PYTHON
        
        return {
            "status": "✅" if ok else "❌",
            "version": version_str,
            "required": f">={'.'.join(map(str, self.MIN_PYTHON))}",
            "path": sys.executable,
            "ok": ok,
        }
    
    def _check_nodejs(self) -> Dict[str, Any]:
        path = shutil.which("node")
        if not path:
            return {"status": "❌", "version": None, "path": None, "ok": False}
        
        try:
            result = subprocess.run(
                ["node", "--version"], capture_output=True, text=True, timeout=5
            )
            version_str = result.stdout.strip().lstrip("v")
            major = int(version_str.split(".")[0])
            ok = major >= self.MIN_NODE[0]
            
            return {
                "status": "✅" if ok else "⚠️",
                "version": version_str,
                "required": f">={self.MIN_NODE[0]}.x",
                "path": path,
                "ok": ok,
            }
        except Exception as e:
            return {"status": "❌", "version": None, "error": str(e), "ok": False}
    
    def _check_npm(self) -> Dict[str, Any]:
        path = shutil.which("npm")
        if not path:
            return {"status": "❌", "version": None, "path": None, "ok": False}
        
        try:
            result = subprocess.run(
                ["npm", "--version"], capture_output=True, text=True, timeout=5
            )
            return {
                "status": "✅",
                "version": result.stdout.strip(),
                "path": path,
                "ok": True,
            }
        except Exception as e:
            return {"status": "❌", "version": None, "error": str(e), "ok": False}
    
    def _check_permissions(self) -> Dict[str, Any]:
        cwd = Path.cwd()
        writable = os.access(cwd, os.W_OK)
        
        test_file = cwd / ".madi_permission_test"
        can_write = False
        try:
            test_file.write_text("test")
            test_file.unlink()
            can_write = True
        except Exception:
            pass
        
        ok = writable and can_write
        return {
            "status": "✅" if ok else "❌",
            "cwd": str(cwd),
            "writable": writable,
            "can_create_files": can_write,
            "ok": ok,
        }
    
    def _get_platform_info(self) -> Dict[str, Any]:
        import platform
        return {
            "system": platform.system(),
            "machine": platform.machine(),
            "is_termux": "TERMUX_VERSION" in os.environ,
            "is_mobile": platform.machine().startswith(("arm", "aarch")),
      }
