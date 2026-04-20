"""豆瓣搜索 CLI 入口。"""

import asyncio

from commands import app


def main():
    asyncio.run(app())


if __name__ == "__main__":
    main()
