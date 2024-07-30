"""This module contains the `MistralCallResponseChunk` class."""

from mistralai.models.chat_completion import ChatCompletionStreamResponse
from mistralai.models.common import UsageInfo

from ..base import BaseCallResponseChunk


class MistralCallResponseChunk(BaseCallResponseChunk[ChatCompletionStreamResponse]):
    '''A convenience wrapper around the Mistral `ChatCompletionChunk` streamed chunks.

    When calling the Mistral API using a function decorated with `mistral_call` and
    `stream` set to `True`, the stream will contain `MistralResponseChunk` instances with
    properties that allow for more convenient access to commonly used attributes.

    Example:

    ```python
    from mirascope.core.mistral import mistral_call

    @mistral_call(model="gpt-4o", stream=True)
    def recommend_book(genre: str):
        """Recommend a {genre} book."""

    stream = recommend_book("fantasy")  # response is an `MistralStream`
    for chunk in stream:
        print(chunk.content, end="", flush=True)
    #> Sure! I would recommend...
    ```
    '''

    @property
    def content(self) -> str:
        """Returns the content of the delta."""
        delta = self.chunk.choices[0].delta
        return delta.content if delta.content is not None else ""

    @property
    def finish_reasons(self) -> list[str]:
        """Returns the finish reasons of the response."""
        return [
            choice.finish_reason if choice.finish_reason else ""
            for choice in self.chunk.choices
        ]

    @property
    def model(self) -> str:
        """Returns the name of the response model."""
        return self.chunk.model

    @property
    def id(self) -> str:
        """Returns the id of the response."""
        return self.chunk.id

    @property
    def usage(self) -> UsageInfo | None:
        """Returns the usage of the chat completion."""
        return self.chunk.usage

    @property
    def input_tokens(self) -> int | None:
        """Returns the number of input tokens."""
        if self.usage:
            return self.usage.prompt_tokens
        return None

    @property
    def output_tokens(self) -> int | None:
        """Returns the number of output tokens."""
        if self.usage:
            return self.usage.completion_tokens
        return None
