import argparse
import os
from core.parser import MadiParser
from generator.api_generator import APIGenerator

def run_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()

    parser = MadiParser(source)
    ast = parser.parse()

    generator = APIGenerator(ast)
    output = generator.generate()

    with open("output.js", "w", encoding="utf-8") as f:
        f.write(output)

    print("🔥 Compiled successfully → output.js")

    os.system("node output.js")


def init_project():
    os.makedirs("examples", exist_ok=True)

    with open("examples/app.madi", "w", encoding="utf-8") as f:
        f.write("""entity: User
intent: register_user
path: /api/signup
method: POST
inputs: (name, email, password)

steps:
    validate email
    create user
""")

    print("✅ Madi project initialized")


def main():
    parser = argparse.ArgumentParser(prog="madi")

    sub = parser.add_subparsers(dest="command")

    run_cmd = sub.add_parser("run")
    run_cmd.add_argument("file")

    sub.add_parser("init")

    args = parser.parse_args()

    if args.command == "run":
        run_file(args.file)

    elif args.command == "init":
        init_project()

    else:
        print("MadiLang CLI")
        print("Commands:")
        print("  madi init")
        print("  madi run <file>")
    

if __name__ == "__main__":
    main()
