# 📜 Changelog

All notable changes to MadiLang are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0/).

---

## 🚀 [v0.6.0] — Deterministic Builds & Sovereign Specifications — 2026-11-04

> 🛡️ **"Sovereignty is proven by reproducibility."**
> 📜 **"The specification is the law; the code is the witness."**

This release establishes the foundation for 100% reproducible builds, completes the `madi build` command pipeline, and elevates project documentation to authoritative, production-grade standards.

### 🌟 Highlights

- 🏗️ **`madi build` Completed**: Fully functional compilation to target code without execution, laying the groundwork for the `--reproducible` flag.
- 🛡️ **Cross-Platform Determinism**: Added `.gitattributes` to enforce `LF` line endings globally, guaranteeing byte-for-byte hash consistency across Windows, macOS, and Linux.
- 📜 **Authoritative Specifications**: `SPEC.md` elevated to v1.0 with explicit "Sovereign Guarantees", and `ROADMAP.md` restructured for professional clarity.
- 🔧 **IR Pipeline Stabilized**: Fixed critical signature mismatches in `step_compiler.py` to align perfectly with `models.py` dataclass definitions.

---

### ✨ Added

#### 🏗️ Build Command
- `madilang/cli/commands/build_cmd.py`: New command module that parses, analyzes, compiles to IR, signs, and generates target code **without** invoking the runtime server.
- Integrated `sign_madi_program` correctly within the build pipeline to attach sovereign metadata before file generation.

#### 🛡️ Infrastructure
- `.gitattributes`: Enforces `text=auto eol=lf` for all source files (`.py`, `.madi`, `.md`, `.toml`, etc.), preventing CRLF/LF hash mismatches in CI/CD and local environments.

#### 📜 Documentation
- `SPEC.md` v1.0: Removed open questions; added Section 10 "Sovereign Guarantees & Design Decisions" explicitly defining cryptographic identity, escape hatch protocols, and reproducibility contracts.
- `ROADMAP.md` v1.0: Consolidated Phase 0 achievements, renumbered phases, and established strict "Exit criteria" for each milestone.

---

### 🔄 Changed

#### 🏗️ Architecture
- `madilang/ir/step_compiler.py`: Corrected IR instruction instantiation to match actual class signatures (e.g., `IRFindInstruction` now correctly uses `entity_name`, `query_field`, `assign_to`; `IRCreateInstruction` uses `entity`, `data`, `result`).
- `madilang/__init__.py`: Bumped `__version__` to `"0.6. "`, updated status banner, and added `madi build` to CLI usage examples.
- `pyproject.toml`: Bumped version to `"0.6.0"`, updated description to highlight "Deterministic & Reproducible builds", and added relevant keywords.

---

### 🐛 Fixed

- Resolved `ImportError` and `TypeError` in the IR compilation pipeline caused by mismatched parameter names between `step_compiler.py` and `models.py`.
- Ensured `madi build` gracefully handles the `MADI_SIGNATURE_SECRET` development fallback warning without crashing.

---

## 🚀 [v0.5.4] — Registry Stability & Documentation Cleanup — 2026-07-04

> 📦 **"Clean docs, clean registry, clean history."**

- 📝 **README.md**: Fully cleaned, synchronized, and formatted for v0.5.3/0.5.4 parity.
- 🧹 **Repository Hygiene**: Removed `my-backend/` development artifacts from version control and added to `.gitignore`.
- 📦 **PyPI**: Confirmed stable publication of `madilang==0.5.4`.

---

## 🚀 [v0.5.0] — Multi-Target Sovereignty & Diagnostics — 2026-06-21

> 🐍 **"Sovereignty speaks every language."**
> 🩺 **"Trust is verified, not assumed."**

This release transformed MadiLang from a single-target tool into a **multi-target sovereign platform**. With Python/FastAPI support, instant environment diagnostics, and a modular CLI architecture, MadiLang now delivers production-ready backends across ecosystems while maintaining cryptographic proof of origin.

### 🌟 Highlights

- 🐍 **Python/FastAPI Generator**: Full async backend generation with Pydantic models, automatic validation, and Uvicorn server setup.
- 🩺 **`madi doctor` Command**: Comprehensive environment diagnostics checking Python, Node.js, npm, network, secrets, and permissions.
- 🛡️ **Sovereign Hybrid Adapter**: Intelligent database fallback ensuring generated code runs everywhere without configuration hell.
- 🏗️ **Modular CLI Architecture**: Lazy-loaded command modules for faster startup and cleaner codebase.
- ✅ **10/10 CI Checks**: All tests passing across Python 3.8–3.13 including mobile validation.
- 📱 **Mobile-First Verified**: Full development cycle tested on Termux/Android.

*(Note: Full v0.5.0 and v0.4.0 details remain preserved in the repository history.)*

---

## 🏛️ [v0.4.0] — Sovereign Architecture Rewrite — 2026-06-14

> ✨ **"Code is no longer written. It is described."**
> 🔐 **"Sovereignty is no longer optional. it is embedded."**

Complete architecture rewrite establishing sovereign, extensible, and production-ready foundation.

### 🌟 Highlights
- 🏗️ Complete Architecture Rewrite (Front-end → IR → Back-end pipeline)
- 🔐 Sovereign Intent Signature with HMAC-SHA256 cryptographic binding
- 🧩 Plugin System with ethics and security hooks
- 📱 Mobile-First Optimization for Termux/Android
- 🛡️ Ethics & Security by Default
- 🧪 Comprehensive Test Suite (Python 3.8–3.12)
- 🤖 VSCode Extension with syntax highlighting
- 🔄 CI/CD Pipeline with 10 automated checks

---

## 🔮 Roadmap

### v0.7.0 (Next)
- 🔄 **Reproducibility Flag**: `madi build --reproducible` producing byte-identical outputs with `.sig` sidecar files.
- 🔐 **Cryptographic Maturity**: Transition from HMAC-SHA256 to Ed25519 for non-repudiable signatures.
- 🛡️ **Security Hook**: Wire `security_hook` with deep data-flow analysis (beyond keyword matching).
- 📚 **Auto-Documentation**: OpenAPI/Swagger generation directly from `.madi` intents.

### v1.0.0 (Vision)
- 🦀 **Go/Fiber Generator**: Multi-language parity.
- 🎨 **Full LSP Support**: VSCode extension with real-time diagnostics and autocomplete.
- 🌍 **Ecosystem**: Community plugin registry and decentralized deployment integrations.
- ✅ **Definition of Done**: Two stable targets, 100% reproducible builds, verified cryptographic chain, and a working escape hatch.

---

## 🤝 Acknowledgments

Special thanks to:
- **El Madani El Mkhitar** — Creator and visionary behind MadiLang and Mkhitarian Philosophy.
- **Community Contributors** — For testing, feedback, and support.
- **Open Source Projects** — PyJWT, bcrypt, Prisma, Express, FastAPI, Pydantic, and all dependencies that make this possible.

---

## 📄 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.