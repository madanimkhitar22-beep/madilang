from core.parser import MadiParser

with open("examples/demo.madi", "r", encoding="utf-8") as f:
    code = f.read()

parser = MadiParser(code)
result = parser.parse()

print("=== Parsed Intent ===")
print(result)
