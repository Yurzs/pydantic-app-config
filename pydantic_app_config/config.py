import asyncio
import os
from abc import abstractmethod
from pathlib import Path
from typing import Callable, ClassVar, Self, TypeVar

from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict


T = TypeVar("T")


class AppConfig(BaseModel):
    """Application configuration."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    STARTUP: ClassVar[list[Callable[[Self], None]]] = []

    @classmethod
    def load(cls) -> Self:
        """Load configuration."""

        config = cls._load()

        try:
            loop = asyncio.get_running_loop()
            runner = loop.create_task
        except RuntimeError:
            loop = asyncio.new_event_loop()
            runner = loop.run_until_complete

        for startup in cls.STARTUP:
            f = startup(config)

            if asyncio.iscoroutinefunction(startup):
                runner(f)

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

        if Path(".env").exists():
            load_dotenv()

        return cls.model_validate(os.environ)
