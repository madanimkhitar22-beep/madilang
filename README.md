<!--
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                                            ║
║   🧠 MadiLang — Sovereign Intent-Driven Programming Language                               ║
║                                                                                            ║
║   "Code is no longer written. It is described."                                            ║
║   "Sovereignty is no longer optional. It is embedded."                                     ║
║                                                                                            ║
║   Built on Mkhitarian Ontology • Mobile-First • Ethics-by-Default                          ║
║                                                                                            ║
╚══════════════════════════════════════════════════════════════════════════════╝
-->

<div align="center">

<!-- 🖼️ Banner Placeholder: Upload your legendary 1280x640 banner in Settings → Social Preview -->
<!-- The banner features: Obsidian black, cyber purple, royal gold gradients, 
     glowing brain/crown logo, and the sovereign tagline. -->

# 🧠 MadiLang v0.4.0

### ✨ Code is no longer written. It is described. ✨

**MadiLang** transforms human-readable intent into production-ready, secure, and sovereign backend systems.  
Describe what you want — MadiLang generates the rest with **cryptographic proof of origin**.

[![MadiLang CI](https://github.com/madanimkhitar22-beep/madilang/actions/workflows/test.yml/badge.svg)](https://github.com/madanimkhitar22-beep/madilang/actions/workflows/test.yml)
[![Python Versions](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue?logo=python&logoColor=white)](https://pypi.org/project/madilang/)
[![License](https://img.shields.io/badge/license-MIT-gold?logo=opensourceinitiative&logoColor=white)](LICENSE)
[![Release](https://img.shields.io/github/v/release/madanimkhitar22-beep/madilang?color=purple&logo=github&label=release)](https://github.com/madanimkhitar22-beep/madilang/releases)
[![Mobile-First](https://img.shields.io/badge/mobile--first-✓-brightgreen?logo=android&logoColor=white)](#-mobile-first-sovereignty)
[![Sovereign Signature](https://img.shields.io/badge/sovereign-signature-🔐-gold?logo=shield&logoColor=white)](#-sovereign-intent-signature)
[![Ethics by Default](https://img.shields.io/badge/ethics-by--default-🛡️-purple?logo=heart&logoColor=white)](#-ethics--security-by-default)
[![Discussions](https://img.shields.io/github/discussions/madanimkhitar22-beep/madilang?color=blue&logo=github&label=discussions)](https://github.com/madanimkhitar22-beep/madilang/discussions)

---

### 🚀 Quick Links

[✨ Get Started](#-quick-start) • [📖 Wiki](https://github.com/madanimkhitar22-beep/madilang/wiki) • [🧬 Philosophy](#-philosophy) • [🤝 Contribute](#-join-the-sovereign-movement) • [💬 Discussions](https://github.com/madanimkhitar22-beep/madilang/discussions)

</div>

---

## 🌟 The Sovereign Difference

In a world of boilerplate, complexity, and hidden logic, MadiLang restores **clarity, sovereignty, and trust**.

| Dimension | Traditional Development | MadiLang |
|:---------:|:----------------------:|:--------:|
| 🧠 **Abstraction** | Write implementation details | **Describe intent** |
| 🔐 **Provenance** | Manual audit trails | **Cryptographic signature** in every artifact |
| 🛡️ **Security** | Add as afterthought | **Security & ethics by default** |
| 📱 **Accessibility** | Requires full IDE/PC | **Mobile-first** — develop on Termux/phone |
| ⚡ **Boilerplate** | Repetitive setup code | **Zero boilerplate** — generated automatically |
| 🔗 **Extensibility** | Modify core or fork | **Plugin system** — extend without touching core |
| 🌐 **Targets** | Single language per project | **Multi-target** — Node.js, Python, Go (planned) |
| 🧪 **Quality** | Manual testing | **Auto-generated tests** & CI/CD pipeline |

> 💎 **MadiLang is not just a tool. It's a declaration: Human intent is the sovereign layer.**

---

## 🔥 Live Example: From Intent to Production API

### 📝 Describe Your Intent (`auth.madi`)

```madi
entity: User
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
```

### 🚀 Generate & Run

```bash
madi run auth.madi
```

### 📤 Output: Sovereign Backend (Node.js + Express + Prisma)

```javascript
// ════════════════════════════════════════════════════════════════════
// 🔐 MadiLang Sovereign Intent Signature
// ════════════════════════════════════════════════════════════════════
const __MADI_SIGNATURE__ = {
  "developer": { "id": "madani004" },
  "intent": { "hash": "a3f8c2...", "fingerprint": "7d9e1b..." },
  "timestamp": { "iso": "2026-06-14T12:00:00Z" },
  "ethics": { "score": 0.95, "passed": true },
  "signature": { "algorithm": "SHA256-HMAC", "value": "..." }
};
// ════════════════════════════════════════════════════════════════════

app.post('/api/signup', validateInputs(['name','email','password']), async (req, res) => {
  try {
    const existing_user = await prisma.user.findUnique({ where: { email: req.body.email } });
    
    if (existing_user) {
      return res.status(400).json({ error: "Email already exists" });
    }
    
    const result = await prisma.user.create({
      data: {
        name: req.body.name,
        email: req.body.email,
        password: await bcrypt.hash(req.body.password, 10)  // 🔒 Auto-hashed
      }
    });
    
    const token = jwt.sign({ id: result.id }, process.env.JWT_SECRET, { expiresIn: '7d' });
    return res.status(200).json({ success: true, token });
    
  } catch (error) {
    res.status(500).json({ error: "Internal server error" });
  }
});
```

> ✅ **Secure by default**: Password hashing, input validation, error handling, JWT generation.  
> 🔐 **Sovereign by design**: Every file carries a verifiable signature binding it to the original intent.

---

## 📱 Mobile-First Sovereignty

MadiLang is designed to run **anywhere Python runs** — including your smartphone.  
**No heavy IDE. No powerful PC. Just intent and sovereignty.**

### 🤖 Termux Setup (Android)

```bash
# 1. Install dependencies
pkg update && pkg install python nodejs git

# 2. Clone repository
git clone https://github.com/madanimkhitar22-beep/madilang.git
cd madilang

# 3. Install in editable mode
pip install -e .

# 4. Verify installation
madi --version
# 🧠 MadiLang v0.4.0 — Sovereign Intent Compiler

# 5. Initialize and run
madi init my-backend
cd my-backend
madi run src/main.madi
```

### 🍎 iOS (via Pythonista or similar)

```bash
pip install madilang
madi run your_file.madi
```

> 💡 **Democratizing development**: Build sovereign backends from anywhere, even a smartphone.

---

## 🏗️ Architecture v0.4.0

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    🧠 MadiLang Sovereign Compiler Pipeline                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  📝 Source (.madi)                                                              │
│       ↓                                                                         │
│  🔍 Parser (Recursive Descent) → AST                                            │
│       ↓                                                                         │
│  📋 Analyzer (Semantic Validation + Ethics Enrichment)                          │
│       ↓                                                                         │
│  🔐 IntentSignature (Cryptographic Binding + Provenance)                        │
│       ↓                                                                         │
│  ⚙️ StepCompiler → IR (Language-Agnostic Intermediate Representation)           │
│       ↓                                                                         │
│  🧩 Plugin Hooks (Ethics, Security, Custom Transformers)                        │
│       ↓                                                                         │
│  🏗️ CodeGenerator → Target Code (Node.js, Python, Go...)                       │
│       ↓                                                                         │
│  📤 Output + Embedded Signature + Runtime Verification                          │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 📁 Project Structure

```
madilang/
├── madilang/              # 🧠 Core sovereign package
│   ├── compiler/          # 🔍 Parser, AST, Analyzer
│   ├── ir/               # ⚙️ IR + Signature Engine
│   ├── generators/       # 🏗️ Code generators (Node.js, Python, Go)
│   ├── stdlib/           # 📚 Auth, Validation, Security
│   ├── plugins/          # 🧩 Plugin system (Ethics, Security hooks)
│   └── cli/              # 🖥️ Command-line interface
├── tests/                # 🧪 Comprehensive test suite
├── examples/             # 💡 Ready-to-run examples
├── tools/                # 🤖 VSCode extension, dev tools
└── .github/workflows/    # 🔄 CI/CD pipeline
```

---

## 🔐 Sovereign Intent Signature

Every artifact generated by MadiLang carries a **cryptographic signature** that proves:

- 👤 **Who** authored the original intent
- 📝 **What** the intent was (source hash)
- 📅 **When** it was generated
- 🛡️ **Whether** it passed ethical review
- ✅ **Integrity** — any modification breaks verification

### 🔍 Verify Signature

```bash
madi verify output.js
# ✅ Signature structure valid
# 👤 Developer: madani004
# 📅 Generated: 2026-06-14T12:00:00Z
# 🔖 Intent Hash: a3f8c2...
# 🛡️ Ethics Score: 0.95
```

### 🧪 Runtime Verification

Generated code includes runtime verification helpers:

```javascript
const verification = __verifyMadiSignature__();
if (!verification.valid) {
  throw new Error("Sovereign signature verification failed!");
}
```

---

## 🛡️ Ethics & Security by Default

MadiLang enforces **ethical and secure patterns** at compile time.

### ✅ Automatic Security Checks

| Check | Description |
|-------|-------------|
| 🔒 **Secure Fields** | Fields marked `(secure)` are automatically hashed with bcrypt |
| 🔐 **Auth Coverage** | Sensitive routes require authentication protection |
| 👤 **Role Guards** | Admin operations enforce role-based access control |
| 🚫 **Injection Prevention** | Input validation generated for all inputs |
| ⚠️ **Error Safety** | Generic error messages prevent data leakage |

### 🧠 Ethics Scoring

The built-in ethics plugin evaluates:

- 📊 **Privacy**: Handling of sensitive data
- 🤝 **Consent**: Explicit user consent requirements
- 🔍 **Transparency**: Clear intent and data usage
- 📝 **Accountability**: Audit trails and responsibility
- ⚖️ **Fairness**: Non-discriminatory logic patterns

```bash
madi check auth.madi
# 🛡️ Ethics Score: [██████████] 0.95 ✅ PASS
```

---

## 🧩 Plugin System

Extend MadiLang without modifying the core:

```python
from madilang.plugins.base_plugin import BasePlugin, PluginHook, register_plugin

@register_plugin
class CustomAuditPlugin(BasePlugin):
    @property
    def metadata(self):
        return PluginMetadata(
            name="custom-audit",
            version="1.0.0",
            description="Custom audit logging",
            author="Your Name",
            hooks=[PluginHook.POST_GENERATE],
        )
    
    def post_generate(self, context):
        context.generated_code += "\n// Custom audit hook injected\n"
        return context.generated_code
```

### 📦 Available Plugins

| Plugin | Description |
|--------|-------------|
| `ethics-hook` | Quantifiable ethics scoring and validation |
| `security-hook` | Vulnerability detection and secure pattern enforcement |
| `sovereign-devkit` | Integration with external security scanner (optional) |
| `cognition-engine` | Integration with Sovereign-Cognition-Engine (optional) |

---

## 🚀 CLI Commands

```bash
# Initialize new project
madi init my-project

# Compile and run
madi run src/main.madi

# Build without running
madi build src/main.madi --target nodejs --output dist/

# Verify signature
madi verify dist/output.js

# Analyze and validate
madi check src/main.madi

# Show version
madi --version
```

---

## 📦 Installation

### 🔧 From Source

```bash
git clone https://github.com/madanimkhitar22-beep/madilang.git
cd madilang
pip install -e .
```

### 🐍 From PyPI (Coming Soon)

```bash
pip install madilang
```

### 📋 Requirements

- Python 3.8+
- Node.js 18+ (for running generated code)
- PostgreSQL (for Prisma integration)

---

## 🧬 Philosophy

MadiLang is built on the **Mkhitarian Ontology**:

> **Human intent is the sovereign layer.**  
> Code is merely the execution of will.  
> Ethics and security are not features — they are foundations.

### Core Principles

- 🧠 **Clarity over complexity**: Describe what you want, not how to do it
- 🎯 **Intent over scale**: Focus on purpose, not boilerplate
- 🔐 **Sovereignty over convenience**: Maintain control and provenance
- 🛡️ **Ethics by default**: Moral considerations embedded in the toolchain
- 📱 **Accessibility for all**: Develop from anywhere, even a smartphone

### 🔗 Related Projects

- [Mkhitarian Philosophy](https://github.com/madanimkhitar22-beep/Mekhitarian-Philosophy) — The philosophical foundation
- [Sovereign-Cognition-Engine](https://github.com/madanimkhitar22-beep/-Sovereign-Cognition-Engine) — Ethics evaluation engine
- [Sovereign-DevKit](https://github.com/madanimkhitar22-beep/Sovereign-DevKit) — Security scanning toolkit

---

## 🤝 Join the Sovereign Movement

We welcome contributors, thinkers, and builders from around the world!

### 💬 Discussions

Have questions? Ideas? Want to share your MadiLang projects?  
👉 [Join the Discussions](https://github.com/madanimkhitar22-beep/madilang/discussions)

### 📋 Development Setup

```bash
# Fork and clone
git clone https://github.com/your-username/madilang.git
cd madilang

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Run linting
ruff check .
black --check .

# Build package
python -m build
```

### 🧭 Contribution Guidelines

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### ✅ Checklist

- [ ] Tests pass (`pytest tests/`)
- [ ] Linting passes (`ruff check .`, `black --check .`)
- [ ] Documentation updated
- [ ] Examples added if applicable

### 📜 Governance

- [Code of Conduct](CODE_OF_CONDUCT.md) — Our community standards
- [Security Policy](SECURITY.md) — Responsible disclosure guidelines
- [License](LICENSE) — MIT License

---

## 📜 Changelog

See [CHANGELOG.md](CHANGELOG.md) for detailed release notes.

### 🚀 v0.4.0 Highlights

- ✨ Complete architecture rewrite with modular design
- 🔐 Sovereign Intent Signature system
- 🧩 Plugin system for extensibility
- 📱 Mobile-first optimization
- 🛡️ Ethics and security hooks
- 🧪 Comprehensive test suite
- 🤖 VSCode extension with syntax highlighting and snippets
- 🔄 CI/CD pipeline with quality, security, and integration checks

---

## 🔮 Roadmap

### v0.5.0 (Planned)

- 🐍 Python/FastAPI generator
- 🦀 Go/Fiber generator
- 🧪 Auto-testing generator from intents
- 📚 Live API documentation generation
- 🩺 `madi doctor` command for environment diagnostics

### v1.0.0 (Vision)

- 🌐 Multi-language parity (Node.js, Python, Go)
- 🔗 Pi Network integration for decentralized deployment
- 🧠 Sovereign-Cognition-Engine deep integration
- 📦 PyPI publication and stable API
- 🌍 Community plugin ecosystem

---

## 📄 Citation

If you use MadiLang in your work, please cite it:

```yaml
cff-version: 1.2.0
title: "MadiLang"
authors:
  - family-names: "El Mkhitar"
    given-names: "El Madani"
    email: "madani004@proton.me"
version: "0.4.0"
date-released: 2026-06-14
license: "MIT"
repository-code: "https://github.com/madanimkhitar22-beep/madilang"
```

---

## 👤 Author

**El Madani El Mkhitar**  
📧 [madani004@proton.me](mailto:madani004@proton.me)  
🌐 [GitHub Profile](https://github.com/madanimkhitar22-beep)

> *"Building sovereign tools for a decentralized future, one intent at a time."*

---

<div align="center">

### 🌟 If MadiLang resonates with your vision, please star the repository!

[![Star on GitHub](https://img.shields.io/github/stars/madanimkhitar22-beep/madilang?style=social)](https://github.com/madanimkhitar22-beep/madilang)

---

**🧠 Code is no longer written. It is described.**  
**🔐 Sovereignty is no longer optional. It is embedded.**  
**🌍 The future of development is sovereign, ethical, and accessible to all.**

</div>
