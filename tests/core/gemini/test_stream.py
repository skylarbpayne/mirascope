"""Tests the `openai.stream` module."""

from google.ai.generativelanguage import (
    Candidate,
    Content,
    GenerateContentResponse,
    Part,
)
from google.generativeai.types import (  # type: ignore
    GenerateContentResponse as GenerateContentResponseType,
)

from mirascope.core.gemini.call_response import GeminiCallResponse
from mirascope.core.gemini.call_response_chunk import GeminiCallResponseChunk
from mirascope.core.gemini.stream import GeminiStream


def test_gemini_stream() -> None:
    """Tests the `GeminiStream` class."""
    assert GeminiStream._provider == "gemini"

    chunks = [
        GenerateContentResponseType.from_response(
            GenerateContentResponse(
                candidates=[
                    Candidate(
                        finish_reason=1,
                        content=Content(
                            parts=[Part(text="The author is ")], role="model"
                        ),
                    )
                ]
            )
        ),
        GenerateContentResponseType.from_response(
            GenerateContentResponse(
                candidates=[
                    Candidate(
                        finish_reason=1,
                        content=Content(
                            parts=[Part(text="Patrick Rothfuss")], role="model"
                        ),
                    )
                ]
            )
        ),
    ]
    stream = GeminiStream(
        stream=((GeminiCallResponseChunk(chunk=chunk), None) for chunk in chunks),
        metadata={},
        tool_types=None,
        call_response_type=GeminiCallResponse,
        model="gemini-flash-1.5",
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[{"role": "user", "parts": ["Who is the author?"]}],
        call_params={},
        call_kwargs={},
    )
    assert stream.cost is None
    for _ in stream:
        pass
    assert stream.cost is None
    assert stream.message_param == {
        "role": "model",
        "parts": [{"type": "text", "text": "The author is Patrick Rothfuss"}],
    }
