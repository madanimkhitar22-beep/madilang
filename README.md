<!-- HERO HEADER -->
<p align="center">
  <img width="100%" src="https://capsule-render.vercel.app/api?type=waving&color=0:0f0c29,50:302b63,100:24243e&height=220&section=header&text=MadiLang&fontSize=44&fontColor=00f2ff&animation=fadeIn" />
</p>

<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=22&pause=900&color=00F2FF&center=true&vCenter=true&width=900&lines=Turn+Intent+into+Real+Backend+Systems;No+Boilerplate+Code+Required;AI-like+Programming+Without+AI;From+Human+Language+→+Production+APIs" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Status-Experimental-00f2ff?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Paradigm-Intent--Driven-6a0dad?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Type-Programming_Language-0f0c29?style=for-the-badge" />
  <img src="https://img.shields.io/badge/License-MIT-a78bfa?style=for-the-badge" />
</p>

---

# 🚀 What is MadiLang?

**MadiLang** is a next-generation **intent-driven programming language** that transforms human-readable instructions into fully working backend systems.

Instead of writing code, you describe **intent**, and MadiLang generates:

- REST APIs
- Authentication systems (JWT)
- Database operations
- Validation logic
- Security layers

> 💡 Think: *"What if backend development was written in human intent instead of code?"*

---

# ⚡ Why MadiLang Exists

Traditional backend development requires:

- Repetitive boilerplate
- Manual validation
- Authentication setup
- Rewriting similar logic across projects

### MadiLang changes this:

| Traditional Dev | MadiLang |
|----------------|----------|
| Write logic manually | Describe intent |
| Build auth system | Auto-generated |
| Define DB queries | Auto-generated |
| Handle validation | Built-in |

---

# 🔥 Example

## 🧾 Input (.madi)

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

## ⚙️ Output (Generated Backend)

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

# 🧠 Architecture

```
MadiLang Source (.madi)
        ↓
Parser Engine (Multi-Intent)
        ↓
Step Compiler (IR Layer)
        ↓
Code Generator
   ├── API Generator (Express.js)
   ├── Database Layer (Prisma)
   ├── Auth Engine (JWT)
   └── Middleware System
```

---

# 🔐 Key Features

### ⚡ Zero Boilerplate
No setup. No repetitive code. Just intent.

### 🛡 Built-in Security
- Password hashing automatically handled
- JWT generation built-in
- Route protection via middleware engine

### 🧠 Intent-Based Compilation
MadiLang understands meaning, not syntax.

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
 │   ├── auth.madi
 │
 └── README.md
```

---

# 🌍 Vision

MadiLang aims to redefine software development:

> From writing code → to describing intent

This reduces:
- Complexity
- Development time
- Human error
- Boilerplate overhead

---

# 🚧 Project Status

**Experimental / Pre-Alpha**

This project is actively evolving and is not production-ready yet.

---

# 🗺 Roadmap

- [x] Parser Engine
- [x] Step Compiler (IR)
- [x] JWT Authentication System
- [ ] Database Schema Generator
- [ ] AI Intent Optimization Engine
- [ ] VS Code Extension
- [ ] Visual Builder Interface

---

# 🤝 Contribute

```bash
git clone https://github.com/your-repo/madilang
cd madilang
python core/main.py
```

---

# ⭐ Why Star This Project?

If you believe in:

- Future of intent-based programming
- AI-like abstraction in software
- Removing boilerplate forever

⭐ Star the repo and join the journey.

---

# 🧭 Final Statement

> MadiLang is not just a programming language.  
> It is a new layer between human thinking and machine execution.
