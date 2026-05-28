"""命令实现模块。封装各子命令的具体业务逻辑。"""

import json
import os
import tempfile
from datetime import datetime

from login_helper import ensure_authenticated, AuthenticationError
from xhs_utils.api_handler import XHSApiHandler


async def search_command(
    keyword: str,
    limit: int = 20,
    output: str | None = None,
    save: bool = False,
    use_cdp: bool = True,
    cdp_url: str = "http://localhost:9222",
):
    """执行小红书搜索命令。"""
    try:
        browser, context, page = await ensure_authenticated(
            headless=True, use_cdp=use_cdp, cdp_url=cdp_url
        )
    except AuthenticationError as e:
        print(f"错误: {e}")
        return

    try:
        handler = XHSApiHandler(context)
        results = await handler.search(keyword, limit=limit)
        _print_search_results(keyword, results)

        if output or save:
            _save_search_json(keyword, results, output)

    finally:
        if use_cdp:
            await _close_page_safe(page)
        await browser.close()


async def detail_command(
    note_id: str,
    xsec_token: str | None = None,
    output: str | None = None,
    save: bool = False,
    use_cdp: bool = True,
    cdp_url: str = "http://localhost:9222",
):
    """获取帖子详情和评论。"""
    try:
        # 帖子详情不能无头（反爬限制），CDP 模式下浏览器本身是有头的
        headless = False if not use_cdp else True
        browser, context, page = await ensure_authenticated(
            headless=False, use_cdp=use_cdp, cdp_url=cdp_url
        )
    except AuthenticationError as e:
        print(f"错误: {e}")
        return

    try:
        handler = XHSApiHandler(context)
        result = await handler.get_note_detail(note_id, xsec_token)
        _print_note_detail(result)

        if output or save:
            _save_note_detail(result, output)

    finally:
        if use_cdp:
            await _close_page_safe(page)
        await browser.close()


async def login_command(check: bool = False) -> None:
    """执行登录命令。"""
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


async def _close_page_safe(page) -> None:
    try:
        await page.close()
    except Exception:
        pass


def _print_search_results(keyword: str, results) -> None:
    """终端打印搜索结果。"""
    print(f"\n搜索: {keyword}")
    print(f"找到 {results.total} 篇相关帖子\n")

    if not results.items:
        print("未找到相关结果。")
        return

    for i, note in enumerate(results.items, 1):
        print(f"[{i}] {note.title}")
        print(f"    作者: {note.author.nickname}")
        print(f"    点赞: {note.liked_count}  评论: {note.comment_count}  收藏: {note.collect_count}")
        print(f"    链接: {note.url}")
        print()

    if results.has_more:
        print("(还有更多结果，可增加 --limit 获取)")


def _print_note_detail(result) -> None:
    """终端打印帖子详情。"""
    note = result.note

    print(f"\n{'=' * 50}")
    print(f"标题: {note.title}")
    print(f"作者: {note.author.nickname}")
    if note.desc:
        print(f"\n正文:\n{note.desc[:500]}{'...' if len(note.desc) > 500 else ''}")

    print(f"\n互动数据:")
    print(f"  点赞: {note.liked_count}  评论: {note.comment_count}  收藏: {note.collect_count}  分享: {note.share_count}")

    if note.tag_list:
        print(f"\n标签: {' '.join(f'#{tag}' for tag in note.tag_list)}")

    if note.image_list:
        print(f"\n图片 ({len(note.image_list)} 张):")
        for i, img in enumerate(note.image_list[:5], 1):
            print(f"  [{i}] {img}")
        if len(note.image_list) > 5:
            print(f"  ... 还有 {len(note.image_list) - 5} 张")

    if note.create_time:
        import datetime as dt
        ts = note.create_time
        if ts > 1000000000000:
            ts = ts / 1000
        try:
            t = dt.datetime.fromtimestamp(ts)
        except (ValueError, OSError):
            t = None
        if t:
            print(f"\n发布时间: {t.strftime('%Y-%m-%d %H:%M')}")

    if result.comment_list:
        print(f"\n热门评论 ({len(result.comment_list)} 条):")
        for i, comment in enumerate(result.comment_list[:10], 1):
            print(f"\n  [{i}] {comment.user.nickname}")
            print(f"      {comment.content[:200]}")
            print(f"      点赞: {comment.liked_count}")


def _get_cache_dir() -> str:
    cache_dir = os.path.join(tempfile.gettempdir(), "xhs-cache")
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir


def _save_search_json(keyword: str, results, output: str | None = None) -> str:
    if output is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_keyword = "".join(c for c in keyword if c.isalnum() or c in " _-")[:30]
        output = os.path.join(_get_cache_dir(), f"{safe_keyword}_{timestamp}.json")

    data = results.model_dump()
    with open(output, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n结果已保存至: {output}")
    return output


def _save_note_detail(result, output: str | None = None) -> str:
    if output is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        note_id = result.note.note_id
        output = os.path.join(_get_cache_dir(), f"{note_id}_{timestamp}.json")

    data = result.model_dump()
    with open(output, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n结果已保存至: {output}")
    return output
