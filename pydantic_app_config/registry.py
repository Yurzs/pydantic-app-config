from typing import Any, Type, TypeVar, ClassVar, Self, Unpack

from pydantic import BaseModel, ConfigDict


T = TypeVar("T")


class Registry(BaseModel):
    _REGISTRY: ClassVar[dict[str, Type[Self]]] = {}

    def __init_subclass__(cls,  **kwargs: Unpack[ConfigDict]):
        if cls.__name__ in cls._REGISTRY:
            raise ValueError(f"Duplicate name: {cls.__name__}")

        super().__init_subclass__(**kwargs)
        cls._REGISTRY[cls.__name__] = cls
