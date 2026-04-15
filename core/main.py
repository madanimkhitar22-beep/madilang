from core.parser import MadiParser
from generator.api_generator import APIGenerator
from generator.db_generator import DBGenerator


class CompilerRouter:
    
    def route(self, ast):
        intent = ast.get("intent")
        entity = ast.get("entity")

        # 🔐 AUTH / LOGIN FLOW
        if intent in ["register_user", "login_user"]:
            return APIGenerator(ast)

        # 🗄 DATABASE ONLY
        if entity and not intent:
            return DBGenerator(ast)

        # ⚠️ fallback
        raise Exception(f"Unknown compilation target: {intent}")


# =========================
# MAIN ENTRY POINT
# =========================

with open("examples/demo.madi", "r", encoding="utf-8") as f:
    source = f.read()

parser = MadiParser(source)
ast = parser.parse()

router = CompilerRouter()
generator = router.route(ast)

output = generator.generate()

print(output)
