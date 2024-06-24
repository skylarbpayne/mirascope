"""This module contains the OpenAI `extract_decorator` function."""

from functools import wraps
from typing import Callable, ParamSpec, TypeVar

from openai import OpenAI
from pydantic import BaseModel

from ..base import _utils
from ._utils import setup_extract
from .call_params import OpenAICallParams
from .function_return import OpenAICallFunctionReturn
from .tool import OpenAITool

_P = ParamSpec("_P")
_ResponseModelT = TypeVar("_ResponseModelT", bound=BaseModel | _utils.BaseType)


def extract_decorator(
    fn: Callable[_P, OpenAICallFunctionReturn],
    model: str,
    response_model: type[_ResponseModelT],
    call_params: OpenAICallParams,
) -> Callable[_P, _ResponseModelT]:
    assert response_model is not None
    tool = _utils.setup_extract_tool(response_model, OpenAITool)

    @wraps(fn)
    def inner(*args: _P.args, **kwargs: _P.kwargs) -> _ResponseModelT:
        assert response_model is not None
        fn_args = _utils.get_fn_args(fn, args, kwargs)
        fn_return = fn(*args, **kwargs)
        json_mode, messages, call_kwargs = setup_extract(
            fn, fn_args, fn_return, tool, call_params
        )
        client = OpenAI()
        response = client.chat.completions.create(
            model=model, stream=False, messages=messages, **call_kwargs
        )

        if json_mode and (content := response.choices[0].message.content):
            json_output = content
        elif tool_calls := response.choices[0].message.tool_calls:
            json_output = tool_calls[0].function.arguments
        else:
            raise ValueError("No tool call or JSON object found in response.")

        output = _utils.extract_tool_return(response_model, json_output, False)
        if isinstance(response_model, BaseModel):
            output._response = response  # type: ignore
        return output

    return inner