
from abc import ABC, abstractmethod


class ModelProvider(ABC):
    """Interface for an AI model that generates software tests."""

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """
        Generate a response to a prompt.

        The response must be a JSON string.
        Concrete providers will implement this method.
        """
        raise NotImplementedError
