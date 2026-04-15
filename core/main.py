from core.parser import MadiParser
from generator.api_generator import APIGenerator
from generator.db_generator import DBGenerator

with open("examples/demo.madi", "r", encoding="utf-8") as f:
    source = f.read()

# 1. PARSE
parser = MadiParser(source)
ast = parser.parse()

# 2. ROUTING (NEW LAYER 🔥)
intent = ast.get("intent")

if intent in ["register_user", "login_user"]:
    generator = APIGenerator(ast)

elif ast.get("entity"):
    generator = DBGenerator(ast)

else:
    raise Exception("Unknown intent type")

# 3. GENERATE
output = generator.generate()

# 4. OUTPUT
print(output)
