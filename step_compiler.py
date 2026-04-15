import re


class StepCompiler:
    """
    Step Compiler for MadiLang

    Converts high-level natural language steps into
    structured Intermediate Representation (IR)
    usable by the APIGenerator layer.
    """

    def compile(self, steps):
        """
        Convert list of MadiLang steps into IR instructions
        """
        compiled = []

        for step in steps:
            step = step.strip()

            if not step:
                continue

            parsed = self.parse_step(step)

            if parsed:
                compiled.append(parsed)

        return compiled

    def parse_step(self, line):
        """
        Parse a single MadiLang step into IR object
        """

        line = line.strip()

        # =========================
        # 🔍 FIND ENTITY
        # =========================
        match = re.match(r'find (\w+) by (\w+) as (\w+)', line)
        if match:
            return {
                "type": "find",
                "entity": match.group(1),
                "field": match.group(2),
                "as": match.group(3)
            }

        # =========================
        # ❗ IF EXISTS
        # =========================
        match = re.match(r'if (\w+) exists', line)
        if match:
            return {
                "type": "if_exists",
                "var": match.group(1)
            }

        # =========================
        # ❗ IF NOT FOUND
        # =========================
        match = re.match(r'if (\w+) not found', line)
        if match:
            return {
                "type": "if_not_found",
                "var": match.group(1)
            }

        # =========================
        # 🔐 PASSWORD MISMATCH
        # =========================
        match = re.match(r'if password does not match (\w+)\.(\w+)', line)
        if match:
            return {
                "type": "password_mismatch",
                "var": match.group(1),
                "field": match.group(2)
            }

        # =========================
        # 🔐 VERIFY PASSWORD (explicit)
        # =========================
        if line.startswith("verify password"):
            return {
                "type": "verify_password"
            }

        # =========================
        # 🧱 CREATE USER
        # =========================
        if line.startswith("create user"):
            return {
                "type": "create"
            }

        # =========================
        # 🔐 LOGIN USER (optional abstraction)
        # =========================
        if line.startswith("login user"):
            return {
                "type": "login"
            }

        # =========================
        # 🔐 GENERATE TOKEN
        # =========================
        if "generate token" in line:
            return {
                "type": "generate_token"
            }

        # =========================
        # 🔐 JWT SUCCESS
        # =========================
        if line.startswith("return success with token"):
            return {
                "type": "jwt_success"
            }

        # =========================
        # 🔐 PROTECT ROUTE
        # =========================
        if line.startswith("protect route"):
            return {
                "type": "protect_route"
            }

        # =========================
        # ❌ ERROR MESSAGE
        # =========================
        match = re.match(r'show error "(.*?)"', line)
        if match:
            return {
                "type": "error",
                "message": match.group(1)
            }

        # =========================
        # ✅ SUCCESS
        # =========================
        if line.startswith("return success"):
            return {
                "type": "success"
            }

        # =========================
        # 🧩 RAW FALLBACK
        # =========================
        return {
            "type": "raw",
            "value": line
        }
