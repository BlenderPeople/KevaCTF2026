from typing import Any


class StreamModes:
    def __init__(self):
        self.res_SUM = 0
        self.res_MAX = 0
        self.res_SEL = 0

    def SUM(self, data: dict[str, Any]) -> None:
        self.res_SUM += sum(data.get("list_bytes"))

    def MAX(self, data: dict[str, Any]) -> None:
        self.res_MAX = max(self.res_MAX, len(data.get("list_bytes")))

    def SEL(self, data: dict[str, Any]) -> None:
        self.res_SEL += 1 if (data.get("elem_type") in data.get("selected_types")) else 0

    def answer(self) -> int:
        return self.res_SUM + self.res_MAX + self.res_SEL
