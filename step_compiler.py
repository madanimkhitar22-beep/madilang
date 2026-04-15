import re


class StepCompiler:
    def compile(self, steps):
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
        line = line.strip()

        # FIND
        match = re.match(r'find (\w+) by (\w+) as (\w+)', line)
        if match:
            return {
                "type": "find",
                "entity": match.group(1),
                "field": match.group(2),
                "as": match.group(3)
            }

        # IF NOT FOUND
        match = re.match(r'if (\w+) not found', line)
        if match:
            return {"type": "if_not_found", "var": match.group(1)}

        # IF EXISTS
        match = re.match(r'if (\w+) exists', line)
        if match:
            return {"type": "if_exists", "field": match.group(1)}

        # PASSWORD CHECK
        match = re.match(r'if password does not match (\w+)\.(\w+)', line)
        if match:
            return {
                "type": "password_mismatch",
                "var": match.group(1),
                "field": match.group(2)
            }

        # CREATE
        if line.startswith("create user"):
            return {"type": "create"}

        # LOGIN
        if line.startswith("login user"):
            return {"type": "login"}

        # JWT
        if "generate token" in line:
            return {"type": "generate_token"}

        if line.startswith("return success with token"):
            return {"type": "jwt_success"}

        # AUTH
        if "protect route" in line:
            return {"type": "auth_required"}

        # ROLE
        if "allow only" in line:
            role = line.split("only", 1)[1].strip()
            return {"type": "role_guard", "role": role}

        # SUCCESS
        if line.startswith("return success"):
            return {"type": "success"}

        # ERROR
        match = re.match(r'show error "(.*?)"', line)
        if match:
            return {"type": "error", "message": match.group(1)}

        return {"type": "raw", "value": line}
