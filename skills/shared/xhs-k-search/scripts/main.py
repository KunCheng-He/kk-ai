"""小红书搜索脚本主入口。提供命令行接口，支持搜索、获取详情、登录等功能。"""

import asyncio
import argparse

from commands import search_command, detail_command, login_command


async def main():
    parser = argparse.ArgumentParser(description="小红书搜索脚本")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    _setup_login_parser(subparsers)
    _setup_search_parser(subparsers)
    _setup_detail_parser(subparsers)

    args = parser.parse_args()

    cdp_url = getattr(args, "cdp_url", "http://localhost:9222")

    if args.command == "login":
        await login_command(check=getattr(args, "check", False))
    elif args.command == "search":
        await search_command(
            args.keyword,
            args.limit,
            args.output,
            args.save,
            use_cdp=not args.no_cdp,
            cdp_url=cdp_url,
        )
    elif args.command == "detail":
        await detail_command(
            args.note_id,
            args.xsec_token,
            args.output,
            args.save,
            use_cdp=not args.no_cdp,
            cdp_url=cdp_url,
        )
    else:
        parser.print_help()


def _add_cdp_args(subparser) -> None:
    subparser.add_argument(
        "--no-cdp",
        action="store_true",
        help="使用 Launch 模式（自启 Chromium），而不是默认的 CDP 模式",
    )
    subparser.add_argument(
        "--cdp-url",
        default="http://localhost:9222",
        help="CDP 调试端点 URL（默认: http://localhost:9222）",
    )


def _setup_login_parser(subparsers) -> None:
    login_parser = subparsers.add_parser("login", help="交互式登录")
    login_parser.add_argument("--check", action="store_true", help="检查登录状态")


def _setup_search_parser(subparsers) -> None:
    search_parser = subparsers.add_parser("search", help="搜索小红书内容")
    search_parser.add_argument("keyword", help="搜索关键词")
    search_parser.add_argument("--limit", "-l", type=int, default=20, help="结果数量，默认 20")
    search_parser.add_argument(
        "--output", "-o", help="输出文件路径 (JSON)，不指定则使用 --save 存入 /tmp"
    )
    search_parser.add_argument(
        "--save", "-s", action="store_true", help="保存结果到 /tmp/xhs-cache"
    )
    _add_cdp_args(search_parser)


def _setup_detail_parser(subparsers) -> None:
    detail_parser = subparsers.add_parser("detail", help="获取帖子详情")
    detail_parser.add_argument("note_id", help="帖子 ID")
    detail_parser.add_argument("--xsec-token", help="帖子 xsec_token")
    detail_parser.add_argument(
        "--output", "-o", help="输出文件路径 (JSON)，不指定则使用 --save 存入 /tmp"
    )
    detail_parser.add_argument(
        "--save", "-s", action="store_true", help="保存结果到 /tmp/xhs-cache"
    )
    _add_cdp_args(detail_parser)


if __name__ == "__main__":
    asyncio.run(main())
