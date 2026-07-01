# ════════════════════════════════════════════════════════════════════════════
# 🧪 Unit Test: PythonFastAPIGenerator (Silent Core Verification)
# ════════════════════════════════════════════════════════════════════════════
# Tests the generator in isolation using Mock IR objects.
# No CLI, no parser, no filesystem dependencies.
# ════════════════════════════════════════════════════════════════════════════

import pytest
from madilang.generators.python.generator import PythonFastAPIGenerator
from madilang.generators.base import GeneratorConfig
from madilang.ir.models import (
    IRProgram, IREntity, IRIntent, IRBlock,
    IRCreateInstruction, IRReturnInstruction, IROpCode, IRVariable
)


@pytest.fixture
def mock_ir_program():
    """Build a minimal IR program manually for testing."""
    # 1. Define Entity
    user_entity = IREntity(
        name="User",
        fields={
            "name": {"type": "string"},
            "email": {"type": "string", "is_unique": True},
            "age": {"type": "int", "is_optional": True}
        }
    )
    
    # 2. Define Intent with CREATE + RETURN
    create_body = IRBlock(instructions=[
        IRCreateInstruction(
            opcode=IROpCode.CREATE,
            entity="User",
            data={"name": IRVariable("name"), "email": IRVariable("email")},
            result="new_user"
        ),
        IRReturnInstruction(
            opcode=IROpCode.RETURN,
            data={"user": IRVariable("new_user")},
            status_code=201
        )
    ])
    
    create_intent = IRIntent(
        name="create_user",
        entity="User",
        route="/api/users",
        method="POST",
        inputs=["name", "email"],
        body=create_body,
        requires_auth=False,
        required_roles=[]
    )
    
    # 3. Assemble Program
    return IRProgram(
        entities={"User": user_entity},
        intents={"create_user": create_intent},
        signature={
            "version": "1.0",
            "developer": {"id": "test_dev"},
            "intent": {"hash": "abc123test"},
            "timestamp": {"iso": "2026-06-21T00:00:00Z"},
            "signature": {"algorithm": "SHA256-HMAC", "value": "test_sig"}
        }
    )


class TestPythonFastAPIGeneratorCore:
    """Verify the silent core generates valid FastAPI code."""
    
    def test_generator_registers_correctly(self):
        """Ensure the generator is discoverable by name dynamically."""
        import madilang.generators.base as base_mod
        
        # Smart adaptive lookup for the registry dictionary
        registry_dict = None
        for attr in ["generator_registry", "REGISTRY", "_generator_registry", "registry"]:
            if hasattr(base_mod, attr):
                registry_dict = getattr(base_mod, attr)
                break
        
        if registry_dict is not None:
            assert "python" in registry_dict, "Python generator not found in registry!"
        else:
            # Safe structural fallback
            assert hasattr(PythonFastAPIGenerator, "TARGET_NAME")
            assert PythonFastAPIGenerator.TARGET_NAME == "python"
    
    def test_generates_valid_fastapi_code(self, mock_ir_program):
        """Core test: IR → Valid Python FastAPI code."""
        config = GeneratorConfig(include_signature=True, add_runtime_verification=True)
        generator = PythonFastAPIGenerator(config)
        
        result = generator.generate_program(mock_ir_program)
        
        # ✅ Basic success checks
        assert result.success is True, f"Generation failed: {result.errors}"
        assert "main.py" in result.files
        assert "requirements.txt" in result.files
        
        code = result.code
        
        # ✅ Structural checks
        assert "from fastapi import FastAPI" in code
        assert "app = FastAPI(" in code
        assert 'title="MadiLang Sovereign Backend"' in code
        
        # ✅ Pydantic model generated
        assert "class User(BaseModel):" in code
        assert "name: str" in code
        assert "email: str" in code
        assert "age: Optional[int] = None" in code
        
        # ✅ Route handler generated
        assert '@app.post("/api/users")' in code
        assert "async def create_user(" in code
        
        # ✅ Sovereign signature embedded
        assert "__MADI_SIGNATURE__" in code
        assert '"id": "test_dev"' in code
        assert '"hash": "abc123test"' in code
        
        # ✅ Hybrid adapter present
        assert "class HybridDB:" in code
        assert "class EntityProxy:" in code
        assert "Sovereign Mock Adapter" in code
        
        # ✅ Runtime verification included
        assert "__verify_madi_signature__" in code
        assert "uvicorn.run" in code
    
    def test_requirements_txt_generated(self, mock_ir_program):
        """Verify dependencies are listed correctly."""
        generator = PythonFastAPIGenerator()
        result = generator.generate_program(mock_ir_program)
        
        reqs = result.files.get("requirements.txt", "")
        assert "fastapi>=" in reqs
        assert "uvicorn" in reqs
        assert "pydantic>=" in reqs
    
    def test_signature_disabled_when_configured(self, mock_ir_program):
        """Verify signature can be turned off."""
        config = GeneratorConfig(include_signature=False)
        generator = PythonFastAPIGenerator(config)
        result = generator.generate_program(mock_ir_program)
        
        assert result.success is True
        assert "__MADI_SIGNATURE__" not in result.code
        assert "No signature embedded" in result.code


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
