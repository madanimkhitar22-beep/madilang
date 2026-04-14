from core.parser import MadiParser
from generator.api_generator import APIGenerator

with open("examples/demo.madi", "r", encoding="utf-8") as f:
    code = f.read()

parser = MadiParser(code)
parsed = parser.parse()

generator = APIGenerator(parsed)
api_code = generator.generate()

print("=== Generated API ===")
print(api_code)
