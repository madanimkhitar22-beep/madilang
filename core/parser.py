class MadiParser:
    def __init__(self, source_code: str):
        self.lines = source_code.strip().split("\n")
        self.result = {
            "entity": None,
            "intent": None,
            "path": None,
            "method": "POST",
            "inputs": [],
            "steps": []
        }
        self.in_steps = False

    def parse(self):
        for line in self.lines:
            line = line.strip()

            if not line:
                continue

            if line.startswith("entity:"):
                self.result["entity"] = line.split(":", 1)[1].strip()

            elif line.startswith("intent:"):
                self.result["intent"] = line.split(":", 1)[1].strip()

            elif line.startswith("path:"):
                self.result["path"] = line.split(":", 1)[1].strip()

            elif line.startswith("method:"):
                self.result["method"] = line.split(":", 1)[1].strip()

            elif line.startswith("inputs:"):
                raw = line.split("(", 1)[1].rstrip(")")
                self.result["inputs"] = [x.strip() for x in raw.split(",")]

            elif line.startswith("steps:"):
                self.in_steps = True

            elif self.in_steps:
                parsed = self.parse_step(line)
                self.result["steps"].append(parsed)

        return self.result


    def parse_step(self, line):
        import re
        line = line.strip()

        match = re.match(r'find (\w+) by (\w+) as (\w+)', line)
        if match:
            return {
                "type": "find",
                "entity": match.group(1),
                "field": match.group(2),
                "var": match.group(3)
            }

        match = re.match(r'if (\w+) not found', line)
        if match:
            return {
                "type": "if_not_found",
                "var": match.group(1)
            }

        match = re.match(r'if (\w+) exists', line)
        if match:
            return {
                "type": "if_exists",
                "field": match.group(1)
            }

        match = re.match(r'if password does not match (\w+)\.(\w+)', line)
        if match:
            return {
                "type": "password_mismatch",
                "var": match.group(1),
                "field": match.group(2)
            }

        if line.startswith("create user"):
            return {"type": "create_user"}

        match = re.match(r'show error "(.*?)"', line)
        if match:
            return {
                "type": "error",
                "message": match.group(1)
            }

        if line.startswith("return success"):
            return {"type": "success"}

        return {"type": "raw", "value": line}
