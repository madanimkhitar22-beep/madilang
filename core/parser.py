class MadiParser:
    def __init__(self, source_code: str):
        self.lines = source_code.strip().split("\n")
        self.results = []
        self.current = None
        self.in_steps = False

    def parse(self):
        for line in self.lines:
            line = line.strip()

            if not line:
                continue

            # NEW INTENT
            if line.startswith("intent:"):
                if self.current:
                    self.results.append(self.current)

                self.current = {
                    "entity": None,
                    "intent": line.split(":", 1)[1].strip(),
                    "path": None,
                    "method": "POST",
                    "inputs": [],
                    "steps": []
                }
                self.in_steps = False

            elif line.startswith("entity:"):
                self.current["entity"] = line.split(":", 1)[1].strip()

            elif line.startswith("route:"):
                self.current["path"] = line.split(":", 1)[1].strip()

            elif line.startswith("method:"):
                self.current["method"] = line.split(":", 1)[1].strip()

            elif line.startswith("inputs:"):
                raw = line.split("(", 1)[1].rstrip(")")
                self.current["inputs"] = [x.strip() for x in raw.split(",")]

            elif line.startswith("steps:"):
                self.in_steps = True

            elif self.in_steps:
                self.current["steps"].append(line.strip())

        if self.current:
            self.results.append(self.current)

        return self.results
