"""Classes for interactings with LLMs through Chat APIs."""
from inspect import isclass
from typing import Callable, Generator, Optional, Type, Union

from openai import OpenAI

from ..prompts import Prompt
from .tools import OpenAITool
from .types import OpenAIChatCompletion, OpenAIChatCompletionChunk
from .utils import convert_function_to_openai_tool, get_openai_chat_messages


class OpenAIChat:
    """A convenience wrapper for the OpenAI Chat client."""

    def __init__(self, model: str = "gpt-3.5-turbo", api_key: Optional[str] = None):
        """Initializes an instance of `OpenAIChat."""
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def create(
        self,
        prompt: Prompt,
        tools: Optional[list[Union[Callable, Type[OpenAITool]]]] = None,
        **kwargs,
    ) -> OpenAIChatCompletion:
        """Makes a call to the model using `prompt`.

        Args:
            prompt: The `Prompt` to use for the call.
            tools: A list of `OpenAITool` types or `Callable` functions that the
                creation call can decide to use. If `tools` is provided, `tool_choice`
                will be set to `auto`.
            **kwargs: Additional keyword arguments to pass to the API call. You can
                find available keyword arguments here:
                https://platform.openai.com/docs/api-reference/chat/create

        Returns:
            A `OpenAIChatCompletion` instance.

        Raises:
            Re-raises any exceptions thrown by the openai chat completions create call.
        """
        if tools:
            openai_tools: list[type[OpenAITool]] = [
                tool if isclass(tool) else convert_function_to_openai_tool(tool)
                for tool in tools
            ]
            kwargs["tools"] = [tool.tool_schema() for tool in openai_tools]
            kwargs["tool_choice"] = "auto"

        try:
            return OpenAIChatCompletion(
                completion=self.client.chat.completions.create(
                    model=self.model,
                    messages=get_openai_chat_messages(prompt),
                    stream=False,
                    **kwargs,
                ),
                tool_types=openai_tools if tools else None,
            )
        except:
            raise

    def stream(
        self,
        prompt: Prompt,
        **kwargs,
    ) -> Generator[OpenAIChatCompletionChunk, None, None]:
        """Streams the response for a call to the model using `prompt`.

        Args:
            prompt: The `Prompt` to use for the call.
            **kwargs: Additional keyword arguments to pass to the API call. You can
                find available keyword arguments here:
                https://platform.openai.com/docs/api-reference/chat/create

        Yields:
            A `OpenAIChatCompletionChunk` for each chunk of the response.

        Raises:
            Re-raises any exceptions thrown by the openai chat completions create call.
        """
        completion_stream = self.client.chat.completions.create(
            model=self.model,
            messages=get_openai_chat_messages(prompt),
            stream=True,
            **kwargs,
        )

        for chunk in completion_stream:
            yield OpenAIChatCompletionChunk(chunk=chunk)
