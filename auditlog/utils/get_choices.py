from enum import Enum
from typing import Tuple, Type, Any, TypeVar

E = TypeVar('E', bound=Enum)


def get_choices_from_enum(enum: Type[E]) -> Tuple[Tuple[Any, Any]]:
    """
    This function transforms an enum's possible values into a choices
    tuple to be used in Django's choices attribute for fields.
    """
    return tuple(((tag.name, tag.value) for tag in enum))


