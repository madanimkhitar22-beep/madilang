# ════════════════════════════════════════════════════════════════════════════
# 🩺 MadiLang Diagnostics — Network Connectivity Checker
# ════════════════════════════════════════════════════════════════════════════

import subprocess
from typing import Dict, Any


class NetworkChecker:
    """Checks network connectivity to package registries."""
    
    ENDPOINTS = {
        "npm_registry": "https://registry.npmjs.org/",
        "pypi_index": "https://pypi.org/simple/",
        "github_api": "https://api.github.com/",
    }
    
    def check_all(self, timeout: int = 5) -> Dict[str, Any]:
        """Test connectivity to all critical endpoints."""
        results = {}
        
        for name, url in self.ENDPOINTS.items():
            results[name] = self._check_endpoint(name, url, timeout)
        
        return {
            "endpoints": results,
            "online": any(r["reachable"] for r in results.values()),
            "all_reachable": all(r["reachable"] for r in results.values()),
        }
    
    def _check_endpoint(self, name: str, url: str, timeout: int) -> Dict[str, Any]:
        """Test single endpoint reachability."""
        try:
            result = subprocess.run(
                ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", 
                 "--max-time", str(timeout), url],
                capture_output=True, text=True, timeout=timeout + 2
            )
            
            status_code = result.stdout.strip()
            reachable = status_code.startswith(("2", "3"))
            
            return {
                "url": url,
                "status_code": status_code,
                "reachable": reachable,
                "latency_ok": True,
                "status": "✅" if reachable else f"⚠️ HTTP {status_code}",
            }
            
        except subprocess.TimeoutExpired:
            return {
                "url": url,
                "status_code": None,
                "reachable": False,
                "latency_ok": False,
                "status": f"❌ TIMEOUT (>{timeout}s)",
            }
        except FileNotFoundError:
            return {
                "url": url,
                "status_code": None,
                "reachable": False,
                "error": "curl not found",
                "status": "❌ NO CURL",
            }
        except Exception as e:
            return {
                "url": url,
                "status_code": None,
                "reachable": False,
                "error": str(e),
                "status": "❌ ERROR",
      }
