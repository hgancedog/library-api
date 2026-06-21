import re
from dataclasses import dataclass

_EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self):
        if not _EMAIL_RE.match(self.value):
            raise ValueError("Invalid email format")
        object.__setattr__(self, "value", self.value.lower())
