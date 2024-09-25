from mirascope.core import BaseDynamicConfig, BaseMessageParam, groq


@groq.call("llama-3.1-8b-instant")
def recommend_book(genre: str) -> BaseDynamicConfig:
    return {
        "messages": [
            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
        ],
        "call_params": {"max_tokens": 512},
        "metadata": {"tags": {"version:0001"}},
    }


print(recommend_book("fantasy"))