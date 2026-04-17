"""
URL 解析模块。

解析知乎链接，提取类型和 ID 信息。
"""

import re


def parse_url(url: str) -> dict[str, str | int | None]:
    """
    解析知乎链接，提取类型和 ID。

    Args:
        url: 知乎链接（问题/回答/文章）。

    Returns:
        包含 type、id、question_id 的字典。
    """
    result: dict[str, str | int | None] = {
        "type": None,
        "id": None,
        "question_id": None,
    }

    question_answer = re.search(r"zhihu\.com/question/(\d+)/answer/(\d+)", url)
    if question_answer:
        result["type"] = "answer"
        result["question_id"] = int(question_answer.group(1))
        result["id"] = int(question_answer.group(2))
        return result

    question = re.search(r"zhihu\.com/question/(\d+)", url)
    if question:
        result["type"] = "question"
        result["id"] = int(question.group(1))
        return result

    article = re.search(r"zhuanlan\.zhihu\.com/p/(\d+)", url)
    if article:
        result["type"] = "article"
        result["id"] = article.group(1)
        return result

    return result
