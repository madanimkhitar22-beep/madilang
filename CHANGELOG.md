# 📜 Changelog

All notable changes to MadiLang are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0/).

---

## 🚀 [v0.4.0] — Sovereign Architecture Rewrite — 2026-06-14

> ✨ **"Code is no longer written. It is described."**  
> 🔐 **"Sovereignty is no longer optional. It is embedded."**

This release marks a **revolutionary milestone** in MadiLang's evolution.  
We have completely rewritten the architecture from the ground up to establish a **sovereign, extensible, and production-ready** foundation. Every component now embodies the Mkhitarian principles of intent-driven development, ethics-by-default, and mobile-first accessibility.

### 🌟 Highlights

- 🏗️ **Complete Architecture Rewrite**: Modular, scalable, and maintainable structure following industry standards (Front-end, Middle-end IR, Back-end generators).
- 🔐 **Sovereign Intent Signature**: Cryptographic binding of generated code to original human intent with verifiable provenance, timestamp, and ethics score.
- 🧩 **Plugin System**: Extensible architecture allowing ethics, security, and custom transformers without modifying core.
- 📱 **Mobile-First Optimization**: Lightweight, efficient, and fully functional on constrained environments like Termux/Android.
- 🛡️ **Ethics & Security by Default**: Built-in hooks for quantifiable ethics scoring and vulnerability detection.
- 🧪 **Comprehensive Test Suite**: Full coverage across Python 3.8–3.12 with integration, security, and mobile validation.
- 🤖 **VSCode Extension**: Syntax highlighting, snippets, and language configuration for professional developer experience.
- 🔄 **CI/CD Pipeline**: Automated quality, testing, security scanning, and integration checks on every commit.

---

### ✨ Added

#### 🔐 Sovereignty & Signature
- `madilang/ir/intent_signature.py`: Intent signature engine with HMAC-SHA256 cryptographic binding.
- Signature embedding in all generated artifacts with runtime verification helpers.
- `madi verify` command for signature validation.
- Developer identity and ethics score inclusion in signature metadata.

#### 🧩 Plugin System
- `madilang/plugins/base_plugin.py`: Abstract plugin architecture with lifecycle management and hook points.
- `madilang/plugins/ethics_hook.py`: Ethics validation plugin with quantifiable scoring (privacy, consent, transparency, accountability, fairness, security).
- `madilang/plugins/security_hook.py`: Security validation plugin detecting vulnerabilities (auth bypass, injection, data exposure).
- Hook points: `PRE_PARSE`, `POST_PARSE`, `PRE_ANALYSIS`, `POST_ANALYSIS`, `PRE_COMPILE`, `POST_COMPILE`, `PRE_GENERATE`, `POST_GENERATE`, `PRE_SIGN`, `POST_SIGN`.

#### 🏗️ Core Architecture
- `madilang/compiler/ast_nodes.py`: Rich AST with dataclasses, type safety, and sovereignty metadata.
- `madilang/compiler/parser.py`: Recursive descent parser with integrated scanner for memory efficiency.
- `madilang/compiler/analyzer.py`: Semantic analyzer with reference resolution, validation, and ethics enrichment.
- `madilang/ir/models.py`: Language-agnostic Intermediate Representation (IR) with opcode-based instructions.
- `madilang/ir/step_compiler.py`: AST-to-IR compiler with explicit transformation of implicit logic.

#### 🏗️ Code Generation
- `madilang/generators/base.py`: Abstract base generator with signature embedding and template support.
- `madilang/generators/nodejs/generator.py`: Production-ready Node.js/Express/Prisma generator.
- Automatic JWT authentication, bcrypt password hashing, input validation, and error handling.
- Prisma schema generation from entity definitions.
- `package.json` and `.env.example` generation for complete project setup.

#### 📚 Standard Library
- `madilang/stdlib/auth.py`: JWT engine, password hashing with bcrypt, API key generation, and audit logging.
- `madilang/stdlib/validators.py`: Comprehensive input validation with schema support, pattern validators, and custom rules.

#### 🖥️ CLI & Tools
- `madilang/cli/main.py`: Complete CLI with `init`, `run`, `build`, `verify`, `check` commands.
- `madilang/cli/logger.py`: Mobile-friendly colored logger with emoji indicators and audit support.
- `tools/vscode-madilang/`: VSCode extension with syntax highlighting, snippets, and configuration.

#### 🧪 Testing & CI
- `tests/test_basic.py`: Core functionality tests ensuring importability and initialization.
- `.github/workflows/test.yml`: CI pipeline with quality, testing matrix, integration, security, and mobile checks.
- Coverage reporting with Codecov integration.

#### 📖 Documentation
- `README.md`: Comprehensive guide with architecture, examples, mobile setup, and contribution guidelines.
- `CHANGELOG.md`: Detailed release notes and migration guide.
- Inline docstrings throughout codebase.

---

### 🔄 Changed

#### 🏗️ Architecture Migration
- Migrated from flat structure to modular package layout (`madilang/` core package).
- Replaced string-based AST with dataclass-based rich AST.
- Introduced IR layer for language-agnostic representation.
- Separated concerns: Parser → Analyzer → IR → Generator pipeline.

#### 🔧 Parser Improvements
- Replaced regex-based parsing with recursive descent parser.
- Added integrated scanner for single-pass efficiency.
- Improved error messages with source location tracking.
- Support for nested conditional blocks in steps.

#### 🛡️ Security Enhancements
- Moved `jwt_engine.py` to `stdlib/auth.py` with enhanced security features.
- Added password strength validation and secure password generation.
- Implemented API key engine with hashing and verification.
- Security plugin enforces secure patterns at compile time.

#### 📱 Mobile Optimization
- Lazy imports in `__init__.py` for reduced memory footprint.
- Lightweight logger without heavy dependencies.
- Single-pass parsing for efficiency on constrained devices.
- Verified compatibility with Termux/Android environment.

---

### ⚠️ Breaking Changes

#### 📦 Package Structure
- **Old**: `core/`, `generator/`, `cli.py`, `runner.py` at root.
- **New**: `madilang/` package with submodules (`compiler/`, `ir/`, `generators/`, `stdlib/`, `plugins/`, `cli/`).
- **Action**: Update imports to use `from madilang import ...` or `from madilang.compiler import ...`.

#### 🔧 CLI Commands
- **Old**: `python cli.py run file.madi`, `python runner.py file.madi`.
- **New**: `madi run file.madi`, `madi build file.madi`.
- **Action**: Install package via `pip install -e .` and use `madi` command.

#### 📝 Syntax Updates
- `route` values must be quoted if containing special characters: `route: "/api/path"`.
- Entity names are case-sensitive: `create User` not `create user`.
- `entity` field inside intents removed; entity is inferred or defined globally.
- **Action**: Update `.madi` files to match new syntax rules.

#### 🔐 Signature Changes
- Signature now embedded as JSON object with structured metadata.
- Includes ethics score, developer identity, and cryptographic hash.
- **Action**: Regenerate code to get new signature format.

---

### 🗑️ Removed

- `core/` directory — replaced by `madilang/compiler/` and `madilang/ir/`.
- `generator/` directory — replaced by `madilang/generators/`.
- `cli.py` — replaced by `madilang/cli/main.py` with `madi` command.
- `runner.py` — functionality merged into `madi run`.
- `jwt_engine.py` — replaced by `madilang/stdlib/auth.py`.
- `step_compiler.py` at root — replaced by `madilang/ir/step_compiler.py`.

---

### 🧭 Migration Guide

#### For Users

1. **Update Installation**:
   ```bash
   # Remove old files
   git pull origin main
   
   # Install new version
   pip install -e .
   ```

2. **Update Commands**:
   ```bash
   # Old
   python cli.py run app.madi
   
   # New
   madi run app.madi
   ```

3. **Update .madi Files**:
   ```madi
   # Old
   route: /api/path
   
   # New
   route: "/api/path"
   ```

#### For Developers

1. **Update Imports**:
   ```python
   # Old
   from core.parser import MadiParser
   
   # New
   from madilang.compiler.parser import MadiParser
   ```

2. **Use New API**:
   ```python
   from madilang import compile_madi
   
   code = compile_madi("intent: create_user ...")
   ```

3. **Write Plugins**:
   ```python
   from madilang.plugins.base_plugin import BasePlugin, register_plugin
   
   @register_plugin
   class MyPlugin(BasePlugin):
       @property
       def metadata(self):
           return PluginMetadata(name="my-plugin", ...)
   ```

---

## 📦 Previous Versions

### [v0.3.0] — Authentication & IR System — 2026-04-15

#### Added
- JWT authentication support in generated code.
- Basic IR representation for step compilation.
- Password hashing with bcrypt.
- Input validation generation.

#### Changed
- Improved parser error handling.
- Enhanced code generation templates.

### [v0.2.0] — Code Generation — 2026-03-01

#### Added
- Node.js/Express code generation.
- Prisma schema generation.
- Basic CLI with file execution.

#### Changed
- Refactored parser for better accuracy.
- Added step compiler for logic transformation.

### [v0.1.0] — Initial Release — 2026-02-01

#### Added
- Basic parser for `.madi` files.
- Entity and intent definitions.
- Simple code generation prototype.

---

## 🔮 Roadmap

### v0.5.0 (Planned)
- 🐍 Python/FastAPI generator.
- 🦀 Go/Fiber generator.
- 🧪 Auto-testing generator from intents.
- 📚 Live API documentation generation.
- 🩺 `madi doctor` command for environment diagnostics.

### v1.0.0 (Vision)
- 🌐 Multi-language parity (Node.js, Python, Go).
- 🔗 Pi Network integration for decentralized deployment.
- 🧠 Sovereign-Cognition-Engine deep integration.
- 📦 PyPI publication and stable API.
- 🌍 Community plugin ecosystem.

---

## 🤝 Acknowledgments

Special thanks to:
- **El Madani El Mkhitar** — Creator and visionary behind MadiLang and Mkhitarian Philosophy.
- **Community Contributors** — For testing, feedback, and support.
- **Open Source Projects** — PyJWT, bcrypt, Prisma, Express, and all dependencies that make this possible.

---

## 📄 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

