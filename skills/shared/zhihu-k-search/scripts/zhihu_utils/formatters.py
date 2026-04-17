"""
输出格式化模块。

提供终端输出和 Markdown 格式化功能。
"""

import json
import re

from zhihu_utils.data_models import (
    SearchResult,
    Answer,
    Question,
    Article,
    SearchResponse,
)


def html_to_markdown(text: str) -> str:
    """
    将 HTML 内容转换为 Markdown 格式。

    Args:
        text: HTML 文本。

    Returns:
        Markdown 文本。
    """
    img_pattern = r'<img[^>]+src=["\']([^"\']+)["\'][^>]*alt=["\']([^"\']*)["\'][^>]*>'
    text = re.sub(img_pattern, r"![\2](\1)", text)
    img_pattern_no_alt = r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>'
    text = re.sub(img_pattern_no_alt, r"![](\1)", text)
    text = re.sub(r"<br\s*/?>", "\n", text)
    text = re.sub(r"</p>", "\n", text)
    text = re.sub(r"<strong[^>]*>([^<]+)</strong>", r"**\1**", text)
    text = re.sub(r"<b[^>]*>([^<]+)</b>", r"**\1**", text)
    text = re.sub(r"<em[^>]*>([^<]+)</em>", r"*\1*", text)
    text = re.sub(r"<i[^>]*>([^<]+)</i>", r"*\1*", text)
    text = re.sub(r"<code[^>]*>([^<]+)</code>", r"`\1`", text)
    text = re.sub(r"<pre[^>]*>([^<]+)</pre>", r"```\n\1\n```", text)
    text = re.sub(
        r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>([^<]+)</a>', r"[\2](\1)", text
    )
    text = re.sub(r"<li[^>]*>", "- ", text)
    text = re.sub(r"</li>", "", text)
    text = re.sub(r"<h[1-6][^>]*>", "\n## ", text)
    text = re.sub(r"</h[1-6]>", "\n", text)
    text = re.sub(r"<blockquote[^>]*>", "\n> ", text)
    text = re.sub(r"</blockquote>", "\n", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def print_search_results(response: SearchResponse) -> None:
    """
    在终端打印搜索结果。

    Args:
        response: 搜索响应对象。
    """
    print(f"\n搜索: {response.query}")
    print(f"找到 {len(response.results)} 条结果\n")

    for i, result in enumerate(response.results, 1):
        print(f"[{i}] {result.title}")
        print(f"    类型: {result.type}")
        if result.author:
            print(f"    作者: {result.author}")
        if result.vote_count > 0:
            print(f"    赞同: {result.vote_count}")
        print(f"    链接: {result.url}")
        if result.excerpt:
            print(f"    摘要: {result.excerpt[:100]}...")
        print()


def save_search_json(response: SearchResponse, output: str) -> None:
    """
    将搜索结果保存为 JSON 文件。

    Args:
        response: 搜索响应对象。
        output: 输出文件路径。
    """
    with open(output, "w", encoding="utf-8") as f:
        json.dump(response.model_dump(), f, ensure_ascii=False, indent=2)
    print(f"结果已保存至: {output}")


def print_answer(answer: Answer) -> None:
    """
    在终端打印回答详情。

    Args:
        answer: 回答对象。
    """
    print(f"\n问题: {answer.question_title}")
    print(f"作者: {answer.author_name}")
    print(f"赞同: {answer.vote_count}  评论: {answer.comment_count}")
    print(f"链接: {answer.url}")
    print("\n" + "=" * 50 + "\n")
    content = html_to_markdown(answer.content)
    print(content[:2000] + "..." if len(content) > 2000 else content)


def format_answer_markdown(answer: Answer) -> str:
    """
    将回答格式化为 Markdown。

    Args:
        answer: 回答对象。

    Returns:
        Markdown 文本。
    """
    md = f"# {answer.question_title}\n\n"
    md += f"**作者**: {answer.author_name}\n"
    md += f"**赞同**: {answer.vote_count}  **评论**: {answer.comment_count}\n"
    md += f"**链接**: {answer.url}\n\n"
    md += "---\n\n"
    md += html_to_markdown(answer.content)
    return md


def print_question(question: Question, answers: list[Answer]) -> None:
    """
    在终端打印问题及回答列表。

    Args:
        question: 问题对象。
        answers: 回答列表。
    """
    print(f"\n问题: {question.title}")
    print(f"回答数: {question.answer_count}  关注数: {question.follower_count}")
    print(f"链接: {question.url}")
    if question.detail:
        print(f"\n问题详情:\n{html_to_markdown(question.detail)[:500]}")

    print(f"\n共 {len(answers)} 个回答:\n")
    for i, ans in enumerate(answers, 1):
        print(f"[{i}] {ans.author_name}")
        print(f"    赞同: {ans.vote_count}  评论: {ans.comment_count}")
        excerpt = html_to_markdown(ans.excerpt or ans.content)[:200]
        print(f"    {excerpt}...")
        print()


def format_question_markdown(question: Question, answers: list[Answer]) -> str:
    """
    将问题及回答格式化为 Markdown。

    Args:
        question: 问题对象。
        answers: 回答列表。

    Returns:
        Markdown 文本。
    """
    md = f"# {question.title}\n\n"
    md += (
        f"**回答数**: {question.answer_count}  **关注数**: {question.follower_count}\n"
    )
    md += f"**链接**: {question.url}\n\n"
    if question.detail:
        md += "## 问题详情\n\n"
        md += html_to_markdown(question.detail) + "\n\n"
    md += f"## 回答 (共 {len(answers)} 个)\n\n"
    for i, ans in enumerate(answers, 1):
        md += f"### 回答 {i}: {ans.author_name}\n\n"
        md += f"**赞同**: {ans.vote_count}  **评论**: {ans.comment_count}\n\n"
        md += html_to_markdown(ans.content) + "\n\n"
        md += "---\n\n"
    return md


def print_article(article: Article) -> None:
    """
    在终端打印文章详情。

    Args:
        article: 文章对象。
    """
    print(f"\n文章: {article.title}")
    print(f"作者: {article.author_name}")
    print(f"赞同: {article.vote_count}  评论: {article.comment_count}")
    print(f"链接: {article.url}")
    print("\n" + "=" * 50 + "\n")
    content = html_to_markdown(article.content)
    print(content[:2000] + "..." if len(content) > 2000 else content)


def format_article_markdown(article: Article) -> str:
    """
    将文章格式化为 Markdown。

    Args:
        article: 文章对象。

    Returns:
        Markdown 文本。
    """
    md = f"# {article.title}\n\n"
    md += f"**作者**: {article.author_name}\n"
    md += f"**赞同**: {article.vote_count}  **评论**: {article.comment_count}\n"
    md += f"**链接**: {article.url}\n\n"
    md += "---\n\n"
    md += html_to_markdown(article.content)
    return md


def save_markdown(content: str, output: str) -> None:
    """
    将 Markdown 内容保存到文件。

    Args:
        content: Markdown 文本。
        output: 输出文件路径。
    """
    with open(output, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"\n结果已保存至: {output}")
