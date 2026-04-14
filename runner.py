import os
from core.parser import MadiParser
from generator.api_generator import APIGenerator

def run_madi(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()

    parser = MadiParser(source)
    ast = parser.parse()

    generator = APIGenerator(ast)
    output_code = generator.generate()

    # حفظ الناتج
    with open("output.js", "w", encoding="utf-8") as f:
        f.write(output_code)

    print("✅ Generated output.js")

    # تشغيل السيرفر مباشرة
    os.system("node output.js")


if __name__ == "__main__":
    run_madi("examples/demo.madi")
