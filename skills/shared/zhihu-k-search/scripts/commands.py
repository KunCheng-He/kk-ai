"""
命令实现模块。

封装各子命令的具体业务逻辑。
"""

from login_helper import ensure_authenticated, AuthenticationError
from zhihu_utils.api_handler import APIHandler
from zhihu_utils.data_models import SearchType
from zhihu_utils.url_parser import parse_url
from zhihu_utils.formatters import (
    print_search_results,
    save_search_json,
    print_answer,
    format_answer_markdown,
    print_question,
    format_question_markdown,
    print_article,
    format_article_markdown,
    save_markdown,
)


async def search_command(query: str, search_type: str, limit: int, output: str | None):
    """
    执行搜索命令。

    Args:
        query: 搜索关键词。
        search_type: 搜索类型。
        limit: 结果数量限制。
        output: 输出文件路径（可选）。
    """
    try:
        browser, context, page = await ensure_authenticated(headless=True)
    except AuthenticationError as e:
        print(f"错误: {e}")
        return

    try:
        handler = APIHandler(page)
        st = SearchType(search_type) if search_type else SearchType.ALL
        response = await handler.search(query, search_type=st, limit=limit)

        print_search_results(response)

        if output:
            save_search_json(response, output)

    finally:
        await browser.close()


async def detail_command(url: str, answer_limit: int, output: str | None):
    """
    执行详情获取命令。

    Args:
        url: 知乎链接。
        answer_limit: 获取回答数量（仅问题）。
        output: 输出文件路径（可选）。
    """
    try:
        browser, context, page = await ensure_authenticated(headless=True)
    except AuthenticationError as e:
        print(f"错误: {e}")
        return

    try:
        handler = APIHandler(page)
        parsed = parse_url(url)

        if not parsed["type"]:
            print(f"无法解析链接: {url}")
            return

        if parsed["type"] == "answer":
            await _handle_answer(handler, parsed, output)
        elif parsed["type"] == "question":
            await _handle_question(handler, parsed, answer_limit, output)
        elif parsed["type"] == "article":
            await _handle_article(handler, parsed, output)

    finally:
        await browser.close()


async def _handle_answer(handler: APIHandler, parsed: dict, output: str | None) -> None:
    """处理回答详情获取。"""
    answer_id = parsed["id"]
    question_id = parsed["question_id"]
    if answer_id is None or question_id is None:
        print("无法解析回答ID")
        return

    answer = await handler.get_answer(int(answer_id), int(question_id))
    if not answer:
        print("获取回答失败")
        return

    print_answer(answer)

    if output:
        md_content = format_answer_markdown(answer)
        save_markdown(md_content, output)


async def _handle_question(
    handler: APIHandler, parsed: dict, answer_limit: int, output: str | None
) -> None:
    """处理问题详情获取。"""
    question_id = parsed["id"]
    if question_id is None:
        print("无法解析问题ID")
        return

    data = await handler.get_question_with_answers(
        int(question_id), answer_limit=answer_limit
    )
    if not data:
        print("获取问题失败")
        return

    question = data["question"]
    answers = data["answers"]

    print_question(question, answers)

    if output:
        md_content = format_question_markdown(question, answers)
        save_markdown(md_content, output)


async def _handle_article(
    handler: APIHandler, parsed: dict, output: str | None
) -> None:
    """处理文章详情获取。"""
    article_id = parsed["id"]
    if article_id is None:
        print("无法解析文章ID")
        return

    article = await handler.get_article(article_id)
    if not article:
        print("获取文章失败")
        return

    print_article(article)

    if output:
        md_content = format_article_markdown(article)
        save_markdown(md_content, output)


async def login_command(check: bool = False) -> None:
    """
    执行登录命令。

    Args:
        check: 是否仅检查登录状态。
    """
    from login_helper import login_interactive

    if check:
        try:
            browser, context, page = await ensure_authenticated(headless=True)
            print("登录状态: 已认证")
            await browser.close()
        except AuthenticationError as e:
            print(f"登录状态: 未认证 - {e}")
    else:
        await login_interactive(headless=False)
