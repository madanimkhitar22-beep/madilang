<!-- HEADER -->
<img width="100%" src="https://capsule-render.vercel.app/api?type=waving&color=0:0f0c29,50:302b63,100:24243e&height=200&section=header&text=MadiLang&fontSize=42&fontColor=00f2ff&animation=fadeIn&fontAlignY=38&desc=Intent-Driven%20Programming%20Language&descAlignY=58&descSize=18&descColor=a78bfa" />

<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=22&pause=1000&color=00F2FF&center=true&vCenter=true&width=700&lines=From+Intent+to+Execution;Human+Language+→+Real+Systems;Zero+Boilerplate+Architecture;Security+by+Default" />

<br/>

![Status](https://img.shields.io/badge/Status-Experimental-00f2ff?style=for-the-badge)
![Paradigm](https://img.shields.io/badge/Paradigm-Intent--Driven-6a0dad?style=for-the-badge)
![Security](https://img.shields.io/badge/Security-Built--In-0f0c29?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-a78bfa?style=for-the-badge)

</div>

---

# 🧠 What is MadiLang?

**MadiLang** is an experimental intent-driven programming language that transforms human-readable intent into fully functional software systems.

Instead of writing implementation details, developers describe **what they want**, and MadiLang generates the rest.

It can generate:

- Backend APIs  
- Databases  
- Validation logic  
- Authentication flows  
- Security layers  

---

# ⚙️ Core Philosophy

## Traditional Programming
You describe **how** to solve a problem.

## MadiLang
You describe **what you want**, and the system determines **how to build it**.

---

# 🔥 Example

## Input (MadiLang)

```madi
intent: create_new_user
route: /api/signup
inputs: (name, email, password)

steps:
    create user
    if email exists:
        stop process
```

## Output (Generated Backend - Node.js)

```ts
app.post('/api/signup', async (req, res) => {
  const { name, email, password } = req.body;

  if (!name || !email || !password) {
    return res.status(400).json({ error: 'Missing fields' });
  }

  const hashedPassword = await bcrypt.hash(password, 10);

  try {
    const user = await prisma.user.create({
      data: {
        name,
        email,
        password: hashedPassword
      }
    });

    return res.status(201).json({ success: true, user });
  } catch (error) {
    return res.status(400).json({ error: 'User already exists' });
  }
});
```

---

# 🧬 Architecture

```
Madi Source Code (.madi)
        ↓
Intent Parser (Core Engine)
        ↓
Abstract Syntax Tree (AST)
        ↓
Code Generators
   ├── Backend (Node.js / Rust)
   ├── Database (Prisma / SQL)
   ├── Security Layer (Hashing / Validation)
   └── API Layer (Express / Actix)
```

---

# 🔒 Key Features

## ⚡ Zero Boilerplate
No manual API setup, schema design, or validation logic.

## 🛡 Security by Default
- `password` → automatically hashed  
- `unique` → enforced constraint  
- timestamps → generated automatically  

## 🧠 Intent-Based Compilation
The compiler interprets meaning, not just syntax.

---

# 🛠 CLI Usage

```bash
madi run app.madi
madi build backend
madi generate database
```

---

# 📦 Project Structure

```
madilang/
 ├── core/
 │   ├── parser.py
 │   ├── ast.py
 │
 ├── generator/
 │   ├── backend.ts
 │   ├── database.prisma
 │
 ├── cli/
 │   ├── runner.py
 │
 ├── examples/
 │   ├── auth.madi
 │
 └── README.md
```

---

# 🌍 Vision

MadiLang aims to shift software development from:

**Implementation-centric programming → Intent-centric systems**

This reduces:

- Complexity  
- Boilerplate  
- Human error  
- Development time  

---

# ⚠️ Project Status

🚧 Early Experimental Stage (Pre-Alpha)

---

# 🚀 Roadmap

- [ ] Rust backend generator  
- [ ] AI-powered AST inference engine  
- [ ] VS Code extension (Guardian LSP)  
- [ ] Visual programming interface  
- [ ] Distributed compilation system  

---

# 🤝 Contribution

```bash
git clone https://github.com/your-repo/madilang
cd madilang
python core/main.py
```

---

# 🧭 Final Statement

> MadiLang is not just a programming language.  
> It is a new abstraction layer between human intent and machine execution.
