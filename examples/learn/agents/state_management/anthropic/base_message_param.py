from mirascope.core import BaseMessageParam, anthropic
from pydantic import BaseModel


class Librarian(BaseModel):
    history: list[anthropic.AnthropicMessageParam] = []

    @anthropic.call("claude-3-5-sonnet-20240620")
    def _call(self, query: str) -> list[anthropic.AnthropicMessageParam]:
        return [
            BaseMessageParam(role="system", content="You are a librarian"),
            *self.history,
            BaseMessageParam(role="user", content=query),
        ]

    def run(self) -> None:
        while True:
            query = input("(User): ")
            if query in ["exit", "quit"]:
                break
            print("(Assistant): ", end="", flush=True)
            response = self._call(query)
            print(response.content)
            self.history += [
                BaseMessageParam(role="user", content=query),
                response.message_param,
            ]


Librarian().run()