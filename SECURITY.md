# 🔐 Security Policy

MadiLang is built on **Sovereignty and Security by Default**. We take security seriously and encourage responsible disclosure of any vulnerabilities.

## 📋 Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| v0.4.x  | ✅ Yes             |
| < v0.4  | ❌ No (Legacy)     |

## 🚨 Reporting a Vulnerability

If you discover a security issue, please **do not open a public issue**. Instead:

1. **Email**: Send details to [madani004@proton.me](mailto:madani004@proton.me) with subject `[SECURITY] MadiLang Vulnerability`.
2. **Encryption**: For sensitive reports, you may request a PGP key for encrypted communication.
3. **Response**: You will receive an acknowledgment within 48 hours.
4. **Resolution**: We aim to resolve critical issues within 7 days and provide a patch release.

### 📝 What to Include
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

## 🛡️ Built-in Security Features

MadiLang enforces security at compile time:
- 🔒 **Secure Field Handling**: Automatic hashing for `(secure)` fields.
- 🔐 **Authentication Coverage**: Sensitive routes require auth protection.
- 👤 **Role-Based Access**: Admin operations enforce role guards.
- 🚫 **Injection Prevention**: Input validation generated for all inputs.
- ⚠️ **Error Safety**: Generic error messages prevent data leakage.

## 🔍 Security Scanning

This repository uses automated security scanning:
- **Bandit**: Python static analysis for vulnerabilities.
- **pip-audit**: Dependency vulnerability checks.
- **GitHub CodeQL**: Advanced code scanning.

See the [Security Tab](../../security) for current alerts and insights.

## 🤝 Acknowledgments

We appreciate security researchers who help keep MadiLang safe. Contributors will be credited in release notes (with permission).

---

**🧠 Sovereignty includes responsibility. Thank you for helping us maintain a secure ecosystem.**
