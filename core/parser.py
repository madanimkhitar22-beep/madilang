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
                self.result["steps"].append(line.strip())

        return self.result
