"""MadiLang CLI — init command."""

from pathlib import Path
from madilang.cli.logger import CLILogger


def cmd_init(args, logger: CLILogger) -> int:
    project_name = args.name
    project_path = Path(project_name)
    logger.info(f"🚀 Initializing MadiLang project: {project_name}")

    try:
        project_path.mkdir(parents=True, exist_ok=True)
        (project_path / "src").mkdir(exist_ok=True)
        (project_path / "examples").mkdir(exist_ok=True)

        main_madi = _get_template_madi(args.template)
        (project_path / "src" / "main.madi").write_text(main_madi, encoding="utf-8")
        (project_path / ".env.example").write_text(_get_env_template(), encoding="utf-8")
        (project_path / ".gitignore").write_text(_get_gitignore(), encoding="utf-8")
        (project_path / "README.md").write_text(f"# {project_name}\nSovereign backend powered by MadiLang.\n", encoding="utf-8")

        logger.success(f"✅ Project initialized at {project_path}")
        logger.info("\n📋 Next steps:")
        logger.info(f"   cd {project_name}")
        logger.info("   madi run src/main.madi")
        return 0
    except Exception as e:
        logger.error(f"Failed to initialize project: {e}")
        return 1


def _get_template_madi(template: str) -> str:
    if template == "auth":
        return '''entity: User
fields:
    - name: string
    - email: string (unique)
    - password: string (secure)
    - createdAt: datetime (auto)

intent: register_user
route: "/api/signup"
method: POST
inputs: (name, email, password)

steps:
    find User by email as existing_user
    if existing_user:
        show error "Email already exists"
        stop process
    create User
    generate token
    return success with token

intent: login_user
route: "/api/login"
method: POST
inputs: (email, password)

steps:
    find User by email as user
    if user not found:
        show error "User not found"
        stop process
    if password does not match user.password:
        show error "Invalid credentials"
        stop process
    generate token
    return success with token
'''
    return '''entity: Item
fields:
    - title: string
    - description: string
    - completed: boolean
    - createdAt: datetime (auto)

intent: create_item
route: "/api/items"
method: POST
inputs: (title, description)

steps:
    create Item
    return success

intent: get_items
route: "/api/items"
method: GET

steps:
    return success
'''


def _get_env_template() -> str:
    return "PORT=3000\nNODE_ENV=development\nDATABASE_URL=postgresql://user:pass@localhost:5432/madidb\nJWT_SECRET=devsecret\n"


def _get_gitignore() -> str:
    return "node_modules/\n.venv/\noutput.js\ndist/\n.env\n*.log\n"
