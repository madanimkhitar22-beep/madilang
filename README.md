<!-- HEADER -->
<p align="center">
  <img width="100%" src="https://capsule-render.vercel.app/api?type=waving&color=0:0f0c29,50:302b63,100:24243e&height=220&section=header&text=MadiLang&fontSize=44&fontColor=00f2ff&animation=fadeIn" />
</p>

<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=22&pause=900&color=00F2FF&center=true&vCenter=true&width=900&lines=Intent+→+Execution;Human+Language+→+Real+Backend;Zero+Boilerplate;Security+by+Default" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Status-Experimental-00f2ff?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Version-v0.3-6a0dad?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Paradigm-Intent--Driven-0f0c29?style=for-the-badge" />
  <img src="https://img.shields.io/badge/License-MIT-a78bfa?style=for-the-badge" />
</p>

---

# 🧠 What is MadiLang?

**MadiLang** is an experimental **intent-driven programming language** that transforms human-readable intent into real backend systems.

Instead of writing code, you describe **what you want**, and the system generates everything.

---

# 🚀 What Can It Generate?

- REST APIs (Express.js)
- Database operations (Prisma)
- Authentication (JWT)
- Password security (bcrypt)
- Validation logic

---

# ⚡ Core Idea

| Traditional Programming | MadiLang |
|------------------------|----------|
| Write *how*            | Describe *what* |
| Manual logic           | Auto-generated |
| Repetitive code        | Zero boilerplate |

---

# 🔥 Example

## Input (.madi)

```madi
entity: User
intent: register_user
route: /api/signup
method: POST
inputs: (name, email, password)

steps:
    if email exists:
        show error "Email already exists"

    create user

    return success with token
```

---

## Output (Generated Backend)

```ts
app.post('/api/signup', async (req, res) => {
  const { name, email, password } = req.body;

  if (!name || !email || !password) {
    return res.status(400).json({ error: "Missing fields" });
  }

  const exists = await prisma.user.findUnique({
    where: { email }
  });

  if (exists) {
    return res.status(400).json({ error: "Email already exists" });
  }

  const user = await prisma.user.create({
    data: {
      name,
      email,
      password: await bcrypt.hash(password, 10)
    }
  });

  const token = jwt.sign(
    { id: user.id },
    process.env.JWT_SECRET || "dev_secret",
    { expiresIn: "7d" }
  );

  return res.json({
    success: true,
    token
  });
});
```

---

# 🧬 Architecture

```
Madi Source Code (.madi)
        ↓
Parser Engine
        ↓
Step Compiler (IR)
        ↓
API Generator
        ↓
Production-ready backend
```

---

# 🔒 Key Features

## ⚡ Zero Boilerplate
No setup. No repetitive coding.

## 🛡 Security by Default
- Password hashing
- JWT authentication
- Input validation

## 🧠 Intent-Based Compilation
The system understands meaning, not just syntax.

---

# 🛠 CLI Usage

```bash
madi run app.madi
madi build backend
madi compile project
```

---

# 📦 Project Structure

```
madilang/
 ├── core/
 │   ├── parser.py
 │   ├── step_compiler.py
 │
 ├── generator/
 │   ├── api_generator.py
 │
 ├── cli/
 │   ├── runner.py
 │
 ├── examples/
 │   ├── auth/
 │   │   ├── register.madi
 │   │   ├── login.madi
 │
 └── README.md
```

---

# 📦 Current Version

**MadiLang v0.3 (Active Development)**

## ✅ Completed
- Parser Engine
- Step Compiler (IR)
- API Generator (Node.js)
- JWT Authentication
- CLI Tool

## 🚧 In Progress
- Multi-Intent Engine
- Middleware Engine

## 🔜 Coming Next
- Auto Testing Generator
- Live API Docs
- Plugin System

---

# 🌍 Vision

MadiLang aims to redefine programming:

> From writing code → to describing intent

---

# ⭐ Why Follow This Project?

This project is evolving in public.

- v0.1 → Parsing
- v0.2 → Code Generation
- v0.3 → Auth + IR System
- v0.4 → Testing + Docs (next)

Follow the journey of a new programming paradigm.

---

# 🧠 Philosophy

> Code is no longer written.  
> It is described.

---

# ⚠️ Status

🚧 Experimental / Pre-Alpha  
Not production-ready yet.

---

# 🤝 Contribute

```bash
git clone https://github.com/your-repo/madilang
cd madilang
python core/main.py
```

---

# 🧭 Final Statement

> MadiLang is not just a programming language.  
> It is a new layer between human intent and machine execution.
