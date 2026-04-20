"""CLI 命令实现。"""

import asyncio
import json
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from douban_utils.api_handler import get_detail
from douban_utils.api_handler import search as do_search
from douban_utils.data_models import Book, Category, DetailWithComments, Movie, Music, SearchResponse

app = typer.Typer(help="豆瓣搜索与数据采集工具")
console = Console()


def parse_category(value: str) -> Category:
    """解析类目参数。"""
    value = value.lower()
    if value == "book":
        return Category.BOOK
    elif value == "movie":
        return Category.MOVIE
    elif value == "music":
        return Category.MUSIC
    else:
        raise typer.BadParameter(f"无效的类目: {value}，可选: book, movie, music")


@app.command()
def search(
    query: str = typer.Argument(..., help="搜索关键词"),
    category: str = typer.Option("book", "-c", "--category", help="类目: book, movie, music"),
    limit: int = typer.Option(10, "-l", "--limit", help="返回数量"),
    json_output: bool = typer.Option(True, "--json/--table", help="JSON 或表格格式输出"),
    output: Path | None = typer.Option(None, "-o", "--output", help="输出文件路径"),
):
    """搜索豆瓣内容。"""
    cat = parse_category(category)
    response = asyncio.run(do_search(query, cat, limit))

    if json_output:
        _print_json(response)
    else:
        _print_search_table(response)

    if output:
        output.write_text(response.model_dump_json(indent=2), encoding="utf-8")
        console.print(f"[green]结果已保存到: {output}[/green]")


@app.command()
def detail(
    subject_id: int = typer.Argument(..., help="条目 ID"),
    category: str = typer.Option("book", "-c", "--category", help="类目: book, movie, music"),
    comments: bool = typer.Option(False, "--comments", help="获取短评"),
    json_output: bool = typer.Option(True, "--json/--table", help="JSON 或表格格式输出"),
    output: Path | None = typer.Option(None, "-o", "--output", help="输出文件路径"),
):
    """获取条目详情。"""
    cat = parse_category(category)
    result = asyncio.run(get_detail(subject_id, cat, comments))

    if not result:
        console.print(f"[red]获取详情失败: {subject_id}[/red]")
        raise typer.Exit(1)

    if json_output:
        _print_json(result)
    else:
        _print_detail(result.detail)
        if comments and result.comments:
            _print_comments(result.comments)

    if output:
        output.write_text(result.model_dump_json(indent=2), encoding="utf-8")
        console.print(f"[green]结果已保存到: {output}[/green]")


def _print_json(data: SearchResponse | DetailWithComments) -> None:
    """输出紧凑 JSON。"""
    print(json.dumps(data.model_dump(mode="json"), ensure_ascii=False, separators=(",", ":")))


def _print_search_table(response: SearchResponse) -> None:
    """打印搜索结果表格。"""
    table = Table(title=f"搜索结果: {response.query} (共 {response.total} 条)")
    table.add_column("ID", style="cyan")
    table.add_column("标题", style="green")
    table.add_column("评分", justify="right")
    table.add_column("评价人数", justify="right")
    table.add_column("摘要")

    for item in response.results:
        rating = f"{item.rating_value}" if item.rating_value else "-"
        table.add_row(
            str(item.id),
            item.title,
            rating,
            str(item.rating_count),
            item.abstract[:30] + "..." if len(item.abstract) > 30 else item.abstract,
        )

    console.print(table)


def _print_detail(detail: Book | Movie | Music) -> None:
    """打印详情。"""
    if isinstance(detail, Book):
        _print_book(detail)
    elif isinstance(detail, Movie):
        _print_movie(detail)
    elif isinstance(detail, Music):
        _print_music(detail)


def _print_book(book: Book) -> None:
    """打印书籍详情。"""
    console.print(Panel(f"[bold green]{book.title}[/bold green]", title="书籍详情"))

    info_lines = []
    if book.subtitle:
        info_lines.append(f"副标题: {book.subtitle}")
    if book.author:
        info_lines.append(f"作者: {' / '.join(book.author)}")
    if book.publisher:
        info_lines.append(f"出版社: {book.publisher}")
    if book.producer:
        info_lines.append(f"出品方: {book.producer}")
    if book.publish_date:
        info_lines.append(f"出版年: {book.publish_date}")
    if book.pages:
        info_lines.append(f"页数: {book.pages}")
    if book.price:
        info_lines.append(f"定价: {book.price}")
    if book.binding:
        info_lines.append(f"装帧: {book.binding}")
    if book.isbn:
        info_lines.append(f"ISBN: {book.isbn}")

    if info_lines:
        console.print("\n".join(info_lines))

    if book.rating_value:
        console.print(f"\n[yellow]评分: {book.rating_value}[/yellow] ({book.rating_count} 人评价)")

    if book.summary:
        console.print(f"\n[bold]内容简介:[/bold]\n{book.summary[:500]}...")

    console.print(f"\n[cyan]{book.url}[/cyan]")


def _print_movie(movie: Movie) -> None:
    """打印电影详情。"""
    console.print(Panel(f"[bold green]{movie.title}[/bold green]", title="电影详情"))

    info_lines = []
    if movie.original_title:
        info_lines.append(f"原名: {movie.original_title}")
    if movie.director:
        info_lines.append(f"导演: {' / '.join(movie.director)}")
    if movie.writers:
        info_lines.append(f"编剧: {' / '.join(movie.writers)}")
    if movie.actors:
        info_lines.append(f"主演: {' / '.join(movie.actors)}")
    if movie.genres:
        info_lines.append(f"类型: {' / '.join(movie.genres)}")
    if movie.countries:
        info_lines.append(f"地区: {' / '.join(movie.countries)}")
    if movie.release_date:
        info_lines.append(f"上映: {movie.release_date}")
    if movie.runtime:
        info_lines.append(f"片长: {movie.runtime} 分钟")

    if info_lines:
        console.print("\n".join(info_lines))

    if movie.rating_value:
        console.print(
            f"\n[yellow]评分: {movie.rating_value}[/yellow] ({movie.rating_count} 人评价)"
        )

    if movie.summary:
        console.print(f"\n[bold]剧情简介:[/bold]\n{movie.summary[:500]}...")

    console.print(f"\n[cyan]{movie.url}[/cyan]")


def _print_music(music: Music) -> None:
    """打印音乐详情。"""
    console.print(Panel(f"[bold green]{music.title}[/bold green]", title="音乐详情"))

    info_lines = []
    if music.artist:
        info_lines.append(f"表演者: {music.artist}")
    if music.release_date:
        info_lines.append(f"发行时间: {music.release_date}")
    if music.genres:
        info_lines.append(f"流派: {' / '.join(music.genres)}")

    if info_lines:
        console.print("\n".join(info_lines))

    if music.rating_value:
        console.print(
            f"\n[yellow]评分: {music.rating_value}[/yellow] ({music.rating_count} 人评价)"
        )

    console.print(f"\n[cyan]{music.url}[/cyan]")


def _print_comments(comments: list) -> None:
    """打印短评。"""
    console.print(f"\n[bold]短评 ({len(comments)} 条):[/bold]")

    table = Table(show_header=True)
    table.add_column("用户", style="cyan", width=12)
    table.add_column("评分", justify="center", width=6)
    table.add_column("内容", width=50)
    table.add_column("有用", justify="right", width=6)

    for c in comments[:10]:
        rating = f"{'★' * c.rating}{'☆' * (5 - c.rating)}" if c.rating else "-"
        content = c.content[:50] + "..." if len(c.content) > 50 else c.content
        table.add_row(c.user_name, rating, content, str(c.votes))

    console.print(table)


if __name__ == "__main__":
    app()
