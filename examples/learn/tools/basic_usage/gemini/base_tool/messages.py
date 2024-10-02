from mirascope.core import BaseTool, Messages, gemini
from pydantic import Field


class GetBookAuthor(BaseTool):
    """Returns the author of the book with the given title."""

    title: str = Field(..., description="The title of the book.")

    def call(self) -> str:
        if self.title == "The Name of the Wind":
            return "Patrick Rothfuss"
        elif self.title == "Mistborn: The Final Empire":
            return "Brandon Sanderson"
        else:
            return "Unknown"


@gemini.call("gemini-1.5-flash", tools=[GetBookAuthor])
def identify_author(book: str) -> Messages.Type:
    return Messages.User(f"Who wrote {book}?")


response = identify_author("The Name of the Wind")
if tool := response.tool:
    print(tool.call())
    print(f"Original tool call: {tool.tool_call}")
else:
    print(response.content)
