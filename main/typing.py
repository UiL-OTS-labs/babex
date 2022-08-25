from typing import Protocol


class StrLike(Protocol):
    def __str__(self) -> str:
        ...
