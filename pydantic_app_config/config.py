import os
from abc import abstractmethod
from typing import Callable, ClassVar, Self, TypeVar

from pydantic import BaseModel
from pydantic_core._pydantic_core import PydanticUndefined


T = TypeVar("T")


class AppConfig(BaseModel):
    """Application configuration."""

    STARTUP: ClassVar[list[Callable[[Self], None]]] = []

    @classmethod
    def load(cls) -> Self:
        """Load configuration."""

        config = cls._load()

        for startup in cls.STARTUP:
            startup(config)

        return config

    @classmethod
    @abstractmethod
    def _load(cls) -> Self:
        pass


class EnvAppConfig(AppConfig):
    """Configuration from environment variables."""

    @classmethod
    def _load(cls) -> Self:
        """Load configuration from environment variables."""

        conf = {}

        for field in cls.model_fields.values():
            default_value = (
                field.default if not field.default_factory else field.default_factory()
            )
            if default_value == PydanticUndefined:
                default_value = None

            conf[field.alias] = os.environ.get(field.alias, default_value)

        return cls.model_validate(conf)
