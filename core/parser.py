class MadiParser:
    """
    أول نواة لـ MadiLang
    يحوّل النص إلى Intent Model بسيط
    """

    def __init__(self, source_code: str):
        self.lines = source_code.strip().split("\n")
        self.result = {
            "intent": None,
            "path": None,
            "method": "POST",
            "inputs": []
        }

    def parse(self):
        for line in self.lines:
            line = line.strip()

            if not line:
                continue

            # intent
            if line.startswith("intent:"):
                self.result["intent"] = line.split(":", 1)[1].strip()

            # path
            elif line.startswith("path:"):
                self.result["path"] = line.split(":", 1)[1].strip()

            # method
            elif line.startswith("method:"):
                self.result["method"] = line.split(":", 1)[1].strip()

            # inputs
            elif line.startswith("inputs:"):
                raw = line.split("(", 1)[1].rstrip(")")
                self.result["inputs"] = [i.strip() for i in raw.split(",")]

        return self.result
