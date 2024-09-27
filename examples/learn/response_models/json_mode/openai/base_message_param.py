from mirascope.core import BaseMessageParam, openai
from pydantic import BaseModel


class Book(BaseModel):
    """An extracted book."""

    title: str
    author: str


@openai.call("gpt-4o-mini", response_model=Book, json_mode=True)
def extract_book(text: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Extract {text}")]


book = extract_book("The Name of the Wind by Patrick Rothfuss")
print(book)
# Output: title='The Name of the Wind' author='Patrick Rothfuss'
