import asyncio
import os
from abc import abstractmethod
from pathlib import Path
from typing import Callable, ClassVar, Self, TypeVar

from dotenv import load_dotenv
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

        loop = asyncio.get_event_loop()

        for startup in cls.STARTUP:
            f = loop.create_task(startup(config))

            if asyncio.iscoroutinefunction(startup):
                loop.run_until_complete(f)

        asyncio.set_event_loop(None)

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

        if Path(".env").exists():
            load_dotenv()

        for field in cls.model_fields.values():
            default_value = (
                field.default if not field.default_factory else field.default_factory()
            )
            if default_value == PydanticUndefined:
                default_value = None

            conf[field.alias] = os.environ.get(field.alias, default_value)

        return cls.model_validate(conf)
