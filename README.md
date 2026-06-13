
# 🧠 MadiLang v0.4.0 — Sovereign Intent-Driven Programming Language

<div align="center">

[![MadiLang CI](https://github.com/madanimkhitar22-beep/madilang/actions/workflows/test.yml/badge.svg)](https://github.com/madanimkhitar22-beep/madilang/actions/workflows/test.yml)
[![Python Versions](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue)](https://pypi.org/project/madilang/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Mobile-First](https://img.shields.io/badge/mobile--first-✓-brightgreen)](#-mobile-first-development)
[![Sovereign Signature](https://img.shields.io/badge/sovereign-signature-🔐-gold)](#-sovereign-intent-signature)
[![Ethics by Default](https://img.shields.io/badge/ethics-by--default-🛡️-purple)](#-ethics--security-by-default)

### ✨ Code is no longer written. It is described. ✨

**MadiLang** transforms human-readable intent into production-ready, secure, and sovereign backend systems.  
Describe what you want — MadiLang generates the rest with cryptographic proof of origin.

[🚀 Quick Start](#-quick-start) • [📖 Documentation](docs/) • [🧬 Philosophy](#-philosophy) • [🤝 Contribute](#-contributing)

</div>

---

## 🌟 What Makes MadiLang Unique?

| Feature | Traditional Development | MadiLang |
|---------|------------------------|----------|
| 🧠 **Abstraction** | Write implementation details | Describe **intent** |
| 🔐 **Sovereignty** | Manual audit trails | **Cryptographic intent signature** embedded in every artifact |
| 🛡️ **Security** | Add security as afterthought | **Security & ethics by default** |
| 📱 **Accessibility** | Requires full IDE/PC | **Mobile-first** — develop on Termux/phone |
| ⚡ **Boilerplate** | Repetitive setup code | **Zero boilerplate** — generated automatically |
| 🔗 **Extensibility** | Modify core or fork | **Plugin system** — extend without touching core |
| 🌐 **Targets** | Single language per project | **Multi-target** — Node.js, Python, Go (planned) |

---

## 💡 Example: From Intent to Production API

### 📝 Input (`auth.madi`)

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

### 📤 Output (Auto-Generated Node.js + Express + Prisma)

```javascript
// 🔐 MadiLang Sovereign Intent Signature
const __MADI_SIGNATURE__ = {
  "developer": { "id": "madani004" },
  "intent": { "hash": "a3f8c2...", "fingerprint": "7d9e1b..." },
  "timestamp": { "iso": "2026-06-14T12:00:00Z" },
  "ethics": { "score": 0.95, "passed": true },
  "signature": { "algorithm": "SHA256-HMAC", "value": "..." }
};

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
        password: await bcrypt.hash(req.body.password, 10)
      }
    });
    
    const token = jwt.sign({ id: result.id }, process.env.JWT_SECRET, { expiresIn: '7d' });
    return res.status(200).json({ success: true, token });
    
  } catch (error) {
    res.status(500).json({ error: "Internal server error" });
  }
});
```

> ✅ **Secure by default**: Password hashing, input validation, error handling, and JWT generation are automatic.  
> 🔐 **Sovereign by design**: Every generated file carries a verifiable signature binding it to the original intent.

---

## 📱 Mobile-First Development

MadiLang is designed to run **anywhere Python runs** — including your smartphone.

### 🤖 Termux Setup (Android)

```bash
# 1. Install dependencies
pkg update && pkg install python nodejs git

# 2. Clone repository
git clone https://github.com/madanimkhitar22-beep/madilang.git
cd madilang

# 3. Install in editable mode (for development)
pip install -e .

# 4. Verify installation
madi --version
# 🧠 MadiLang v0.4.0 — Sovereign Intent Compiler

# 5. Initialize and run your first project
madi init my-backend
cd my-backend
madi run src/main.madi
```

### 🍎 iOS (via Pythonista or similar)

```bash
pip install madilang
madi run your_file.madi
```

> 💡 **No heavy IDE required**. Write `.madi` files in any text editor and compile instantly.

---

## 🏗️ Architecture v0.4.0

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            MadiLang Compiler Pipeline                                          │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                │
│  📝 Source (.madi)                                                                            │
│       ↓                                                                                        │
│  🔍 Parser (Recursive Descent) → AST                                                         │
│       ↓                                                                                        │
│  📋 Analyzer (Semantic Validation + Ethics Enrichment)                                        │
│       ↓                                                                                        │
│  🔐 IntentSignature (Sovereign Binding + Cryptographic Hash)                                  │
│       ↓                                                                                        │
│  ⚙️ StepCompiler → IR (Language-Agnostic Intermediate Representation)                        │
│       ↓                                                                                        │
│  🧩 Plugin Hooks (Ethics, Security, Custom Transformers)                                      │
│       ↓                                                                                        │
│  🏗️ CodeGenerator → Target Code (Node.js, Python, Go...)                                     │
│       ↓                                                                                        │
│  📤 Output + Embedded Signature + Runtime Verification                                        │
│                                                                                                │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 📁 Project Structure

```
madilang/
├── madilang/              # Core package
│   ├── compiler/          # Parser, AST, Analyzer
│   ├── ir/               # Intermediate Representation + Signature Engine
│   ├── generators/       # Code generators (Node.js, Python, Go)
│   ├── stdlib/           # Standard library (Auth, Validation)
│   ├── plugins/          # Plugin system (Ethics, Security hooks)
│   └── cli/              # Command-line interface
├── tests/                # Comprehensive test suite
├── examples/             # Ready-to-run examples
├── tools/                # VSCode extension, dev tools
└── .github/workflows/    # CI/CD pipeline
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

MadiLang enforces **ethical and secure patterns** at compile time:

### ✅ Automatic Security Checks

- 🔒 **Secure field handling**: Fields marked `(secure)` are automatically hashed
- 🔐 **Authentication coverage**: Sensitive routes require auth protection
- 👤 **Role-based access**: Admin operations enforce role guards
- 🚫 **Injection prevention**: Input validation generated for all inputs
- ⚠️ **Error safety**: Generic error messages prevent data leakage

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
        # Add custom audit code to generated output
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

### 🐍 From PyPI (Coming Soon)

```bash
pip install madilang
```

### 🔧 From Source

```bash
git clone https://github.com/madanimkhitar22-beep/madilang.git
cd madilang
pip install -e .
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

- [Mkhitarist Philosophy](https://github.com/madanimkhitar22-beep/Mekhitarian-Philosophy) — The philosophical foundation
- [Sovereign-Cognition-Engine](https://github.com/madanimkhitar22-beep/-Sovereign-Cognition-Engine) — Ethics evaluation engine
- [Sovereign-DevKit](https://github.com/madanimkhitar22-beep/Sovereign-DevKit) — Security scanning toolkit

---

## 🤝 Contributing

We welcome contributions from developers worldwide!

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

## 📄 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

```
MIT License

Copyright © 2026 El Madani El Mkhitar

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

---

## 👤 Author

**El Madani El Mkhitar**  
📧 [madani004](madani004@gmail.com)  
🌐 [GitHub Profile](https://github.com/madanimkhitar22-beep)

> *"Building sovereign tools for a decentralized future, one intent at a time."*

---

<div align="center">

### 🌟 If MadiLang resonates with your vision, please star the repository!

[![Star on GitHub](https://img.shields.io/github/stars/madanimkhitar22-beep/madilang?style=social)](https://github.com/madanimkhitar22-beep/madilang)

---

**🧠 Code is no longer written. It is described.**  
**🔐 Sovereignty is no longer optional. It is embedded.**

</div>


