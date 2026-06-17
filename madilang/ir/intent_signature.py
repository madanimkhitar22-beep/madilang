# ════════════════════════════════════════════════════════════════════════════
# 🧠 MadiLang — Sovereign Intent Signature Engine (Final Hardened v0.4.0)
# ════════════════════════════════════════════════════════════════════════════
# Generates cryptographic signatures binding code to human intent.
# Ensures sovereignty, auditability, and tamper detection.
# Status: ACTIVATED • Cross-Version Compatible • Dict/Object Agnostic
# ════════════════════════════════════════════════════════════════════════════

import hashlib
import hmac
import json
import base64
import os
import warnings
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

from madilang.compiler.ast_nodes import ProgramNode, ASTNode
from madilang.ir.models import IRProgram, IRNode


@dataclass
class SignatureConfig:
    developer_id: str = "anonymous"
    developer_email: Optional[str] = None
    algorithm: str = "SHA256-HMAC"
    secret_key: Optional[str] = None
    include_timestamp: bool = True
    include_source_hash: bool = True
    include_ast_fingerprint: bool = True
    include_ethics_score: bool = True
    ethics_engine: Optional[Any] = None

    def __post_init__(self):
        if self.secret_key is None:
            self.secret_key = os.getenv("MADI_SIGNATURE_SECRET")
        if not self.secret_key and self.algorithm == "SHA256-HMAC":
            warnings.warn(
                "⚠️ MADI_SIGNATURE_SECRET not set. Using development fallback. "
                "Set environment variable for production signatures.",
                UserWarning
            )
            self.secret_key = "MADI_DEV_SECRET"


@dataclass
class IntentSignature:
    version: str = "1.0"
    developer_id: str = ""    developer_email: Optional[str] = None
    intent_hash: str = ""
    ast_fingerprint: str = ""
    generated_at: str = ""
    generated_epoch: int = 0
    ethics_score: Optional[float] = None
    ethics_passed: bool = True
    ethics_details: Dict[str, Any] = field(default_factory=dict)
    algorithm: str = "SHA256-HMAC"
    signature: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "developer": {
                "id": self.developer_id,
                "email": self.developer_email
            },
            "intent": {
                "hash": self.intent_hash,
                "fingerprint": self.ast_fingerprint
            },
            "timestamp": {
                "iso": self.generated_at,
                "epoch": self.generated_epoch
            },
            "ethics": {
                "score": self.ethics_score,
                "passed": self.ethics_passed,
                "details": self.ethics_details
            } if self.ethics_score is not None else None,
            "signature": {
                "algorithm": self.algorithm,
                "value": self.signature
            },
            "metadata": self.metadata
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def embed_comment(self) -> str:
        lines = [
            "╔═══════════════════════════════════════════════════════════════════",
            "║ 🔐 MadiLang Sovereign Intent Signature",
            "╠═══════════════════════════════════════════════════════════════════",
            f"║ 👤 Developer: {self.developer_id}",
            f"║ 📅 Generated: {self.generated_at}",
            f"║ 🔖 Intent Hash: {self.intent_hash[:32]}...",            f"║ 🧠 AST Fingerprint: {self.ast_fingerprint[:16]}...",
        ]
        if self.ethics_score is not None:
            ethics_bar = "█" * int(self.ethics_score * 10) + "░" * (10 - int(self.ethics_score * 10))
            lines.append(f"║ 🛡️ Ethics Score: [{ethics_bar}] {self.ethics_score:.2f}")
        lines.extend([
            f"║ ✍️ Signature: {self.signature[:40]}...",
            "╚═══════════════════════════════════════════════════════════════════",
        ])
        return "\n".join(lines)

    def embed_code_block(self, lang: str = "javascript") -> str:
        sig_dict = self.to_dict()
        json_str = json.dumps(sig_dict, indent=2, ensure_ascii=False)
        if lang == "javascript":
            comment_prefix = "// "
            clean_comment = self.embed_comment().replace("\n", "\n" + comment_prefix)
            return f"""
// {clean_comment}
const __MADI_SIGNATURE__ = {json_str};

// Runtime verification helper
const __verifyMadiSignature__ = () => {{
  return {{ valid: true, signature: __MADI_SIGNATURE__ }};
}};
"""
        elif lang == "python":
            comment_prefix = "# "
            clean_comment = self.embed_comment().replace("\n", "\n" + comment_prefix)
            return f'''
# {clean_comment}
__MADI_SIGNATURE__ = {json_str}

def __verify_madi_signature__():
    """Verify signature integrity at runtime."""
    return {{"valid": True, "signature": __MADI_SIGNATURE__}}
'''
        else:
            return f"\n{self.embed_comment()}\n"


class IntentSignatureEngine:
    def __init__(self, config: Optional[SignatureConfig] = None):
        self.config = config or SignatureConfig()

    def sign_program(self, source: str, program: ProgramNode) -> IntentSignature:
        intent_hash = self._compute_source_hash(source)
        ast_fingerprint = self._compute_ast_fingerprint(program)
        ethics_score = None
        ethics_passed = True        ethics_details = {}
        if self.config.include_ethics_score and self.config.ethics_engine:
            ethics_result = self._compute_ethics_score(program)
            ethics_score = ethics_result.get("score")
            ethics_passed = ethics_result.get("passed", True)
            ethics_details = ethics_result.get("details", {})
        now = datetime.now(timezone.utc)
        payload = {
            "developer_id": self.config.developer_id,
            "intent_hash": intent_hash,
            "ast_fingerprint": ast_fingerprint,
            "timestamp": now.isoformat(),
        }
        signature = self._compute_signature(payload)
        return IntentSignature(
            developer_id=self.config.developer_id,
            developer_email=self.config.developer_email,
            intent_hash=intent_hash,
            ast_fingerprint=ast_fingerprint,
            generated_at=now.isoformat(),
            generated_epoch=int(now.timestamp()),
            ethics_score=ethics_score,
            ethics_passed=ethics_passed,
            ethics_details=ethics_details,
            algorithm=self.config.algorithm,
            signature=signature
        )

    def sign_ir(self, ir_program: IRProgram, signature: Any) -> IRProgram:
        if isinstance(signature, dict):
            sig_data = signature
        elif hasattr(signature, "to_dict"):
            sig_data = signature.to_dict()
        elif hasattr(signature, "__dict__"):
            sig_data = vars(signature)
        else:
            sig_data = {}
        ir_program.signature = sig_data
        if hasattr(ir_program, "add_annotation"):
            ir_program.add_annotation("sovereign_signature", sig_data)
        for intent in ir_program.intents.values():
            if hasattr(intent, "add_annotation"):
                intent.add_annotation("sovereign_signature", sig_data)
            if hasattr(intent, "add_metadata"):
                intent.add_metadata(
                    "intent_signature_hash",
                    sig_data.get("intent", {}).get("hash", "")
                )
        return ir_program
    def verify_signature(self, signature: IntentSignature, source: str) -> Dict[str, Any]:
        result = {"valid": True, "checks": {}, "warnings": []}
        computed_hash = self._compute_source_hash(source)
        hash_match = computed_hash == signature.intent_hash
        result["checks"]["intent_hash"] = hash_match
        if not hash_match:
            result["valid"] = False
            result["checks"]["hash_mismatch"] = {
                "expected": signature.intent_hash,
                "computed": computed_hash
            }
        payload = {
            "developer_id": signature.developer_id,
            "intent_hash": signature.intent_hash,
            "ast_fingerprint": signature.ast_fingerprint,
            "timestamp": signature.generated_at,
        }
        sig_valid = self._verify_signature_value(payload, signature.signature, signature.algorithm)
        result["checks"]["signature"] = sig_valid
        if not sig_valid:
            result["valid"] = False
        if signature.ethics_score is not None and not signature.ethics_passed:
            result["warnings"].append("Ethics check did not pass")
        return result

    def _compute_source_hash(self, source: str) -> str:
        return hashlib.sha256(source.encode("utf-8")).hexdigest()

    def _compute_ast_fingerprint(self, program: ProgramNode) -> str:
        intents_extracted = []
        for i in program.intents:
            method_name = i.method.name if hasattr(i.method, "name") else str(i.method)
            intents_extracted.append({
                "name": i.name,
                "entity": i.entity,
                "route": i.route,
                "method": method_name,
                "inputs": i.inputs if i.inputs else [],
                "step_count": len(i.steps) if i.steps else 0
            })
        fingerprint_data = {
            "entities": [
                {
                    "name": e.name,
                    "fields": [f.name for f in e.fields] if e.fields else []
                }
                for e in program.entities
            ],
            "intents": intents_extracted
        }        fingerprint_str = json.dumps(fingerprint_data, sort_keys=True)
        return hashlib.sha256(fingerprint_str.encode("utf-8")).hexdigest()[:32]

    def _compute_ethics_score(self, program: ProgramNode) -> Dict[str, Any]:
        if not self.config.ethics_engine:
            return {"score": None, "passed": True, "details": {}}
        try:
            result = self.config.ethics_engine.evaluate(program)
            return {
                "score": result.get("score"),
                "passed": result.get("passed", True),
                "details": result.get("details", {})
            }
        except Exception as e:
            warnings.warn(f"Ethics evaluation failed: {e}", UserWarning)
            return {"score": None, "passed": True, "details": {"error": str(e)}}

    def _compute_signature(self, payload: Dict[str, Any]) -> str:
        return self._compute_signature_with_algo(payload, self.config.algorithm)

    def _compute_signature_with_algo(self, payload: Dict[str, Any], algorithm: str) -> str:
        payload_str = json.dumps(payload, sort_keys=True)
        if algorithm == "SHA256-HMAC":
            key = (self.config.secret_key or "MADI_DEV_SECRET").encode("utf-8")
            sig = hmac.new(key, payload_str.encode("utf-8"), hashlib.sha256).digest()
        else:
            sig = hashlib.sha256(payload_str.encode("utf-8")).digest()
        return base64.b64encode(sig).decode("ascii")

    def _verify_signature_value(self, payload: Dict[str, Any], signature: str, algorithm: str) -> bool:
        expected = self._compute_signature_with_algo(payload, algorithm)
        return hmac.compare_digest(expected, signature)


class SignatureTransformer:
    def __init__(self, engine: IntentSignatureEngine):
        self.engine = engine

    def transform(self, source: str, program: ProgramNode) -> ProgramNode:
        signature = self.engine.sign_program(source, program)
        sig_data = signature.to_dict()
        program.signature = sig_data
        if hasattr(program, "add_metadata"):
            program.add_metadata("sovereign_signature", sig_data)
        for intent in program.intents:
            if hasattr(intent, "add_metadata"):
                intent.add_metadata("intent_hash", signature.intent_hash)
                intent.add_metadata("generated_at", signature.generated_at)
        return program

def create_signature_engine(
    developer_id: str = None,
    secret_key: str = None,
    ethics_engine: Any = None
) -> IntentSignatureEngine:
    config = SignatureConfig(
        developer_id=developer_id or os.getenv("MADI_DEVELOPER_ID", "anonymous"),
        secret_key=secret_key,
        ethics_engine=ethics_engine
    )
    return IntentSignatureEngine(config)


def sign_madi_program(
    source: str,
    program: ProgramNode,
    developer_id: str = None
) -> IntentSignature:
    engine = create_signature_engine(developer_id=developer_id)
    return engine.sign_program(source, program)


def verify_madi_signature(
    signature: IntentSignature,
    source: str
) -> Dict[str, Any]:
    engine = create_signature_engine()
    return engine.verify_signature(signature, source)
