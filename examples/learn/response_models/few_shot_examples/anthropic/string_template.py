from mirascope.core import anthropic, prompt_template
from pydantic import BaseModel, ConfigDict, Field


class Book(BaseModel):
    title: str = Field(..., examples=["THE NAME OF THE WIND"])
    author: str = Field(..., examples=["Rothfuss, Patrick"])

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"title": "THE NAME OF THE WIND", "author": "Rothfuss, Patrick"}
            ]
        }
    )


@anthropic.call("claude-3-5-sonnet-20240620", response_model=Book, json_mode=True)
@prompt_template("Extract {text}. Match examples format.")
def extract_book(text: str): ...


book = extract_book("The Way of Kings by Brandon Sanderson")
print(book)
# Output: title='THE NAME OF THE WIND' author='Rothfuss, Patrick'
