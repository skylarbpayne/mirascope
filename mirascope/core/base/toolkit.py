"""The module for defining the toolkit class for LLM call tools."""

from __future__ import annotations

import inspect
from abc import ABC
from typing import Callable, ClassVar, NamedTuple

from pydantic import BaseModel, ConfigDict
from typing_extensions import ParamSpec, Concatenate

from . import BaseTool
from ._utils import convert_function_to_base_tool, get_template_variables

_TOOLKIT_TOOL_METHOD_MARKER: str = "__toolkit_tool_method__"

P = ParamSpec("P")


def toolkit_tool(
    method: Callable[Concatenate[BaseToolKit, P], str],
) -> Callable[Concatenate[BaseToolKit, P], str]:
    # Mark the method as a toolkit tool
    setattr(method, _TOOLKIT_TOOL_METHOD_MARKER, True)

    return method


class ToolKitToolMethod(NamedTuple):
    method: Callable[..., str]
    template_vars: list[str]
    template: str


class BaseToolKit(BaseModel, ABC):
    """A class for defining tools for LLM call tools."""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    _toolkit_tool_methods: ClassVar[list[ToolKitToolMethod]]
    _namespace: ClassVar[str | None] = None

    def create_tools(self) -> list[type[BaseTool]]:
        """The method to create the tools."""
        return [
            convert_function_to_base_tool(
                method, BaseTool, template.format(self=self), self._namespace
            )
            for method, template_vars, template in self._toolkit_tool_methods
        ]

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs):
        cls._toolkit_tool_methods = []
        for attr in cls.__dict__.values():
            if not getattr(attr, _TOOLKIT_TOOL_METHOD_MARKER, False):
                continue
            # Validate the toolkit_tool_method
            if (template := attr.__doc__) is None:
                raise ValueError("The toolkit_tool method must have a docstring")

            dedented_template = inspect.cleandoc(template)
            template_vars = get_template_variables(dedented_template)

            for var in template_vars:
                if not var.startswith("self."):
                    raise ValueError(
                        "The toolkit_tool method must use self. prefix in template variables "
                        "when creating tools dynamically"
                    )

                self_var = var[5:]

                # Expecting pydantic model fields or class attribute and property
                if self_var in cls.model_fields or hasattr(cls, self_var):
                    continue
                raise ValueError(
                    f"The toolkit_tool method template variable {var} is not found in the class"
                )

            cls._toolkit_tool_methods.append(
                ToolKitToolMethod(attr, template_vars, dedented_template)
            )
        if not cls._toolkit_tool_methods:
            raise ValueError("No toolkit_tool method found")
