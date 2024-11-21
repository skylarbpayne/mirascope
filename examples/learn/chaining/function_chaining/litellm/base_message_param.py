from mirascope.core import BaseMessageParam, litellm


@litellm.call("gpt-4o-mini")
def summarize(text: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Summarize this text: {text}")]


@litellm.call("gpt-4o-mini")
def translate(text: str, language: str) -> list[BaseMessageParam]:
    return [
        BaseMessageParam(
            role="user",
            content=f"Translate this text to {language}: {text}",
        )
    ]


summary = summarize("Long English text here...")
translation = translate(summary.content, "french")
print(translation.content)