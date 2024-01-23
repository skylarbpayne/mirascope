"""Classes for using tools with Chat APIs."""
from __future__ import annotations

import json
from typing import Callable, Optional, Type, TypeVar, cast

from openai.types.chat import ChatCompletionMessageToolCall, ChatCompletionToolParam
from pydantic import BaseModel


class OpenAITool(BaseModel):
    """A base class for more easily using tools with the OpenAI Chat client."""

    @property
    def fn(self) -> Optional[Callable]:
        """Returns the function that the tool describes."""
        return None

    @classmethod
    def tool_schema(cls) -> ChatCompletionToolParam:
        """Constructs a tool schema for use with the OpenAI Chat client.

        Returns:
            The constructed `ChatCompletionToolParam` schema.

        Raises:
            ValueError: if the class doesn't have
        """
        model_schema = cls.model_json_schema()
        if "description" not in model_schema:
            raise ValueError("Tool must have a docstring description.")

        fn = {
            "name": model_schema["title"],
            "description": model_schema["description"],
        }
        if model_schema["properties"]:
            fn["parameters"] = {
                "type": "object",
                "properties": {
                    prop: {
                        key: value
                        for key, value in prop_schema.items()
                        if key != "default" and key != "title"
                    }
                    for prop, prop_schema in model_schema["properties"].items()
                },
                "required": model_schema["required"],
            }

        return cast(ChatCompletionToolParam, {"type": "function", "function": fn})

    @classmethod
    def from_tool_call(cls, tool_call: ChatCompletionMessageToolCall) -> OpenAITool:
        """Returns an instance of the tool constructed from a tool call response."""
        return cls(**json.loads(tool_call.function.arguments))


T = TypeVar("T", bound=OpenAITool)


def openai_tool_fn(fn: Callable) -> Callable:
    """A decorator for adding a function to a tool class.

    Adding this decorator will add an `fn` property to the tool class that returns the
    function that the tool describes. This is convenient for calling the function given
    an instance of the tool.

    Args:
        fn: The function to add to the tool class.

    Returns:
        The decorated tool class.
    """

    def decorator(cls: Type[T]) -> Type[T]:
        """A decorator for adding a function to a tool class."""
        setattr(cls, "fn", property(lambda self: fn))
        return cls

    return decorator
