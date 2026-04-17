"""
知乎搜索脚本主入口。

提供命令行接口，支持搜索、获取详情、登录等功能。
"""

import asyncio
import argparse

from commands import search_command, detail_command, login_command


async def main():
    """主入口函数，解析命令行参数并执行对应命令。"""
    parser = argparse.ArgumentParser(description="知乎搜索脚本")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    _setup_login_parser(subparsers)
    _setup_search_parser(subparsers)
    _setup_detail_parser(subparsers)

    args = parser.parse_args()

    if args.command == "login":
        await login_command(check=getattr(args, "check", False))
    elif args.command == "search":
        await search_command(args.query, args.type, args.limit, args.output)
    elif args.command == "detail":
        await detail_command(args.url, args.answer_limit, args.output)
    else:
        parser.print_help()


def _setup_login_parser(subparsers) -> None:
    """配置登录命令解析器。"""
    login_parser = subparsers.add_parser("login", help="交互式登录")
    login_parser.add_argument("--check", action="store_true", help="检查登录状态")


def _setup_search_parser(subparsers) -> None:
    """配置搜索命令解析器。"""
    search_parser = subparsers.add_parser("search", help="搜索知乎内容")
    search_parser.add_argument("query", help="搜索关键词")
    search_parser.add_argument(
        "--type",
        "-t",
        choices=["all", "question", "answer", "article", "people"],
        default="all",
        help="搜索类型",
    )
    search_parser.add_argument("--limit", "-l", type=int, default=10, help="结果数量")
    search_parser.add_argument("--output", "-o", help="输出文件路径 (JSON)")


def _setup_detail_parser(subparsers) -> None:
    """配置详情命令解析器。"""
    detail_parser = subparsers.add_parser("detail", help="获取帖子详情")
    detail_parser.add_argument("url", help="知乎链接 (问题/回答/文章)")
    detail_parser.add_argument(
        "--answer-limit", "-a", type=int, default=5, help="获取回答数量 (仅问题)"
    )
    detail_parser.add_argument("--output", "-o", help="输出文件路径 (Markdown)")


if __name__ == "__main__":
    asyncio.run(main())
