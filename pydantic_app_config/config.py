import asyncio
import os
from abc import abstractmethod
from pathlib import Path
from typing import Awaitable, Callable, ClassVar, Self, TypeVar

from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict

from pydantic_app_config.registry import Registry


T = TypeVar("T")


class AppConfig(BaseModel):
    """Application configuration."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    STARTUP: ClassVar[list[Callable[[Self], None | Awaitable[None]]]] = []

    @classmethod
    async def load(cls) -> Self:
        """Load configuration."""

        config = await cls._load()

        for startup in cls.STARTUP:
            result = startup(config)

            if asyncio.iscoroutine(result):
                await result

        return config

    @classmethod
    @abstractmethod
    def _load(cls) -> Self:
        pass


class EnvAppConfig(AppConfig, Registry):
    """Configuration from environment variables."""

    @classmethod
    def _load(cls) -> Self:
        """Load configuration from environment variables."""

        if Path(".env").exists():
            load_dotenv()

        return cls.model_validate(os.environ)
