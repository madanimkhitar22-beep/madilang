
<!--
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   🧠 MadiLang — Sovereign Intent-Driven Programming Language                 ║
║                                                                              ║
║   "Code is no longer written. It is described."                              ║
║   "Sovereignty is no longer optional. It is embedded."                       ║
║                                                                              ║
║   Built on Mkhitarian Ontology • Mobile-First • Ethics-by-Default            ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
-->

<div align="center">

# 🧠 MadiLang v0.6.0

### ✨ Code is no longer written. It is described. ✨

**MadiLang** transforms human-readable intent into production-ready, secure, and sovereign backend systems.
Describe what you want — MadiLang generates the rest with **cryptographic proof of origin** and **deterministic reproducibility**.

[![MadiLang CI](https://github.com/madanimkhitar22-beep/madilang/actions/workflows/test.yml/badge.svg)](https://github.com/madanimkhitar22-beep/madilang/actions/workflows/test.yml)
[![Python Versions](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue?logo=python&logoColor=white)](https://pypi.org/project/madilang/)
[![License](https://img.shields.io/badge/license-MIT-gold?logo=opensourceinitiative&logoColor=white)](LICENSE)
[![Release](https://img.shields.io/github/v/release/madanimkhitar22-beep/madilang?color=purple&logo=github&label=release)](https://github.com/madanimkhitar22-beep/madilang/releases)
[![Mobile-First](https://img.shields.io/badge/mobile--first-✓-brightgreen?logo=android&logoColor=white)](#-mobile-first-sovereignty)
[![Multi-Target](https://img.shields.io/badge/targets-Node.js%20%7C%20Python-blueviolet?logo=fastapi&logoColor=white)](#-multi-target-generation)
[![Sovereign Signature](https://img.shields.io/badge/sovereign-signature-🔐-gold?logo=shield&logoColor=white)](#-sovereign-intent-signature)
[![Ethics by Default](https://img.shields.io/badge/ethics-by--default-🛡️-purple?logo=heart&logoColor=white)](#-ethics--security-by-default)
[![Discussions](https://img.shields.io/github/discussions/madanimkhitar22-beep/madilang?color=blue&logo=github&label=discussions)](https://github.com/madanimkhitar22-beep/madilang/discussions)

---

### 🚀 Quick Links

[✨ Get Started](#-installation) • [📖 Wiki](https://github.com/madanimkhitar22-beep/madilang/wiki) • [🩺 madi doctor](#-madi-doctor) • [🧬 Philosophy](#-philosophy) • [🤝 Contribute](#-join-the-sovereign-movement) • [💬 Discussions](https://github.com/madanimkhitar22-beep/madilang/discussions)

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
| 🌐 **Targets** | Single language per project | **Multi-target** — Node.js + Python (FastAPI) |
| 🩺 **Diagnostics** | Manual debugging | **`madi doctor`** — instant environment health check |
| 🔄 **Reproducibility** | Environment-dependent builds | **Deterministic** — byte-for-byte identical outputs |

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
madi run auth.madi --target nodejs    # Node.js + Express
madi run auth.madi --target python    # Python + FastAPI
```

### 📤 Output: Sovereign Backend

<details>
<summary><strong>🟢 Node.js / Express Output</strong></summary>

```javascript
// ════════════════════════════════════════════════════════════════════
// 🔐 MadiLang Sovereign Intent Signature
// ════════════════════════════════════════════════════════════════════
const __MADI_SIGNATURE__ = {
  "developer": { "id": "madani004" },
  "intent": { "hash": "a3f8c2...", "fingerprint": "7d9e1b..." },
  "timestamp": { "iso": "2026-11-04T00:00:00Z" },
  "ethics": { "score": 0.95, "passed": true },
  "signature": { "algorithm": "SHA256-HMAC", "value": "..." }
};
// ════════════════════════════════════════════════════════════════════

app.post('/api/signup', validateInputs(['name','email','password']), async (req, res) => {
  const existing_user = await prisma.user.findUnique({ where: { email: req.body.email } });
  if (existing_user) return res.status(400).json({ error: "Email already exists" });

  const result = await prisma.user.create({
    data: { name: req.body.name, email: req.body.email, password: await bcrypt.hash(req.body.password, 10) }
  });

  const token = jwt.sign({ id: result.id }, process.env.JWT_SECRET, { expiresIn: '7d' });
  return res.status(200).json({ success: true, token });
});
```
</details>

<details>
<summary><strong>🐍 Python / FastAPI Output</strong></summary>

```python
# ════════════════════════════════════════════════════════════════════
# 🔐 MadiLang Sovereign Intent Signature
# ════════════════════════════════════════════════════════════════════
__MADI_SIGNATURE__ = {
    "developer": {"id": "madani004"},
    "intent": {"hash": "a3f8c2...", "fingerprint": "7d9e1b..."},
    "timestamp": {"iso": "2026-11-04T00:00:00Z"},
    "ethics": {"score": 0.95, "passed": True},
    "signature": {"algorithm": "SHA256-HMAC", "value": "..."}
}
# ════════════════════════════════════════════════════════════════════

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="MadiLang Sovereign Backend")

class RegisterUserInput(BaseModel):
    name: str
    email: str
    password: str

@app.post("/api/signup")
async def register_user(data: RegisterUserInput):
    existing = await db.user.find(email=data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    result = await db.user.create(name=data.name, email=data.email, password=hash_password(data.password))
    token = generate_token(result["id"])
    return {"success": True, "token": token}
```
</details>

> ✅ **Secure by default**: Password hashing, input validation, error handling, JWT generation.
> 🔐 **Sovereign by design**: Every file carries a verifiable signature binding it to the original intent.

---

## 🆕 What's New in v0.6.0

### 🏗️ `madi build` Command
Compile `.madi` source files to target code **without execution**. This is the foundational step for CI/CD pipelines and reproducible builds.
```bash
madi build src/main.madi --target python --output dist/
```

### 🔄 Deterministic & Reproducible Builds
Added `.gitattributes` to enforce `LF` line endings globally, guaranteeing byte-for-byte hash consistency across Windows, macOS, and Linux. Preparation for the upcoming `--reproducible` flag.

### 📜 Authoritative Specifications
- **`SPEC.md` v1.0**: Elevated from draft to authoritative specification, including explicit "Sovereign Guarantees" for cryptographic identity and escape hatches.
- **`ROADMAP.md` v1.0**: Restructured for professional clarity with strict exit criteria for each phase.

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
# 🧠 MadiLang v0.6.0 — Sovereign Intent Compiler

# 5. Diagnose environment
madi doctor

# 6. Initialize and build
madi init my-backend
cd my-backend
madi build src/main.madi --target python --output dist/
```

> 💡 **Democratizing development**: Build sovereign backends from anywhere, even a smartphone.

---

## 🏗️ Architecture v0.6.0

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
│  🏗️ CodeGenerator → Target Code                                                 │
│       ├── 🟢 Node.js / Express / Prisma                                         │
│       ├── 🐍 Python / FastAPI / Pydantic                                        │
│       └── 🦀 Go / Fiber (planned)                                               │
│       ↓                                                                         │
│  📤 Output + Embedded Signature + Hybrid Adapter + Runtime Verification         │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
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
madi verify dist/output.py
# ✅ Signature structure valid
# 👤 Developer: madani004
# 📅 Generated: 2026-11-04T00:00:00Z
# 🔖 Intent Hash: a3f8c2...
# 🛡️ Ethics Score: 0.95
```

---

## 🛡️ Ethics & Security by Default

| Check | Description |
|-------|-------------|
| 🔒 **Secure Fields** | Fields marked `(secure)` are automatically hashed with bcrypt |
| 🔐 **Auth Coverage** | Sensitive routes require authentication protection |
| 👤 **Role Guards** | Admin operations enforce role-based access control |
| 🚫 **Injection Prevention** | Input validation generated for all inputs |
| ⚠️ **Error Safety** | Generic error messages prevent data leakage |
| 🧠 **Ethics Scoring** | Privacy, consent, transparency, accountability, fairness |

```bash
madi check auth.madi
# ✅ Analysis passed
#    Entities: 1
#    Intents: 2
```

---

## 🚀 CLI Commands

```bash
# Initialize new project
madi init my-project

# Compile and run (Node.js or Python)
madi run src/main.madi --target nodejs
madi run src/main.madi --target python

# Build without running (NEW in v0.6.0)
madi build src/main.madi --target python --output dist/

# Verify sovereign signature
madi verify dist/output.py

# Analyze and validate source
madi check src/main.madi

# Diagnose environment
madi doctor

# Show version
madi --version
```

---

## 📦 Installation

### 🐍 From PyPI (Recommended)

```bash
pip install madilang
madi doctor  # Verify your environment
```

### 🔧 From Source

```bash
git clone https://github.com/madanimkhitar22-beep/madilang.git
cd madilang
pip install -e .
madi doctor
```

### 📋 Requirements

- Python 3.8+ (3.13 supported ✅)
- Node.js 18+ (for Node.js target)
- npm (for auto-dependency installation)

---

## 🧬 Philosophy

MadiLang is built on the **Mkhitarian Ontology**:

> **Human intent is the sovereign layer.**
> Code is merely the execution of will.
> Ethics and security are not features — they are foundations.

### 🔗 Related Projects

- [Mkhitarian Philosophy](https://github.com/madanimkhitar22-beep/Mekhitarian-Philosophy) — The philosophical foundation
- [Sovereign-DevKit](https://github.com/madanimkhitar22-beep/Sovereign-DevKit) — Security scanning toolkit

---

## 🤝 Join the Sovereign Movement

### 💬 Discussions
👉 [Join the Discussions](https://github.com/madanimkhitar22-beep/madilang/discussions)

### 📋 Development Setup

```bash
git clone https://github.com/madanimkhitar22-beep/madilang.git
cd madilang
pip install -e ".[dev]"
pytest tests/ -v
ruff check .
```

### 📜 Governance

- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Security Policy](SECURITY.md)
- [License](LICENSE) — MIT

---

## 📜 Changelog

See [CHANGELOG.md](CHANGELOG.md) for detailed release notes.

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

## 📄 Citation

```yaml
cff-version: 1.2.0
title: "MadiLang"
authors:
  - family-names: "El Mkhitar"
    given-names: "El Madani"
    email: "madani004@proton.me"
version: "0.6.0"
date-released: 2026-11-04
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
