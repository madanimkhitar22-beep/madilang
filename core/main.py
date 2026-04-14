from core.parser import MadiParser
from generator.api_generator import APIGenerator

with open("examples/demo.madi", "r", encoding="utf-8") as f:
    source = f.read()

parser = MadiParser(source)
ast = parser.parse()

generator = APIGenerator(ast)
output = generator.generate()

print(output)
