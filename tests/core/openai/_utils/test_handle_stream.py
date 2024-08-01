"""Tests the `openai._utils.handle_stream` module."""

import pytest
from openai.types.chat import ChatCompletionChunk
from openai.types.chat.chat_completion_chunk import (
    Choice,
    ChoiceDelta,
    ChoiceDeltaToolCall,
    ChoiceDeltaToolCallFunction,
)

from mirascope.core.openai._utils.handle_stream import (
    handle_stream,
    handle_stream_async,
)
from mirascope.core.openai.tool import OpenAITool


class FormatBook(OpenAITool):
    """Returns the title and author nicely formatted."""

    title: str
    author: str

    def call(self):
        """Dummy call."""


@pytest.fixture()
def mock_chunks() -> list[ChatCompletionChunk]:
    """Returns a list of mock `ChatCompletionChunk` instances."""

    new_tool_call = ChoiceDeltaToolCall(
        index=0,
        id="id",
        function=ChoiceDeltaToolCallFunction(
            arguments=None,
            name="FormatBook",
        ),
        type="function",
    )
    tool_call = ChoiceDeltaToolCall(
        index=0,
        id=None,
        function=ChoiceDeltaToolCallFunction(
            arguments='{"title": "The Name of the Wind", "author": "Patrick Rothfuss"}',
            name=None,
        ),
        type="function",
    )
    return [
        ChatCompletionChunk(
            id="id",
            choices=[
                Choice(delta=ChoiceDelta(content="content", tool_calls=None), index=0)
            ],
            created=0,
            model="gpt-4o",
            object="chat.completion.chunk",
        ),
        ChatCompletionChunk(
            id="id",
            choices=[
                Choice(
                    delta=ChoiceDelta(
                        content=None,
                        tool_calls=[new_tool_call],
                    ),
                    index=0,
                )
            ],
            created=0,
            model="gpt-4o",
            object="chat.completion.chunk",
        ),
        ChatCompletionChunk(
            id="id",
            choices=[
                Choice(
                    delta=ChoiceDelta(
                        content=None,
                        tool_calls=[tool_call],
                    ),
                    index=0,
                )
            ],
            created=0,
            model="gpt-4o",
            object="chat.completion.chunk",
        ),
        ChatCompletionChunk(
            id="id",
            choices=[
                Choice(
                    delta=ChoiceDelta(
                        content=None,
                        tool_calls=[new_tool_call],
                    ),
                    index=0,
                )
            ],
            created=0,
            model="gpt-4o",
            object="chat.completion.chunk",
        ),
        ChatCompletionChunk(
            id="id",
            choices=[
                Choice(
                    delta=ChoiceDelta(
                        content=None,
                        tool_calls=[tool_call],
                    ),
                    index=0,
                )
            ],
            created=0,
            model="gpt-4o",
            object="chat.completion.chunk",
        ),
        ChatCompletionChunk(
            id="id",
            choices=[
                Choice(
                    delta=ChoiceDelta(content=None, tool_calls=None),
                    finish_reason="tool_calls",
                    index=0,
                )
            ],
            created=0,
            model="gpt-4o",
            object="chat.completion.chunk",
        ),
    ]


def test_handle_stream(mock_chunks: list[ChatCompletionChunk]) -> None:
    """Tests the `handle_stream` function."""

    result = [
        t for t in handle_stream((c for c in mock_chunks), tool_types=[FormatBook])
    ]
    # Check we get three tuples back.
    # (chunk, None), (chunk, FormatBook), (chunk, FormatBook)
    assert len(result) == 3
    assert result[0][1] is None
    assert (
        (tool := result[1][1]) is not None
        and isinstance(tool, FormatBook)
        and tool.model_dump(exclude={"tool_call"})
        == {"title": "The Name of the Wind", "author": "Patrick Rothfuss"}
    )
    assert (
        (tool := result[2][1]) is not None
        and isinstance(tool, FormatBook)
        and tool.model_dump(exclude={"tool_call"})
        == {"title": "The Name of the Wind", "author": "Patrick Rothfuss"}
    )


@pytest.mark.asyncio
async def test_handle_stream_async(mock_chunks: list[ChatCompletionChunk]) -> None:
    """Tests the `handle_stream_async` function."""

    async def generator():
        for chunk in mock_chunks:
            yield chunk

    result = []
    async for t in handle_stream_async(generator(), tool_types=[FormatBook]):
        result.append(t)
    # Check we get three tuples back.
    # (chunk, None), (chunk, FormatBook), (chunk, FormatBook)
    assert len(result) == 3
    assert result[0][1] is None
    assert (
        (tool := result[1][1]) is not None
        and isinstance(tool, FormatBook)
        and tool.model_dump(exclude={"tool_call"})
        == {"title": "The Name of the Wind", "author": "Patrick Rothfuss"}
    )
    assert (
        (tool := result[2][1]) is not None
        and isinstance(tool, FormatBook)
        and tool.model_dump(exclude={"tool_call"})
        == {"title": "The Name of the Wind", "author": "Patrick Rothfuss"}
    )