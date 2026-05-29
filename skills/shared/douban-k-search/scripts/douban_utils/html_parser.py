"""HTML 解析器。"""

import re

from bs4 import BeautifulSoup

from douban_utils.data_models import Book, Comment, Movie, Music, Rating


def parse_book_detail(html: str, subject_id: int) -> Book | None:
    """解析书籍详情页面。

    Args:
        html: 页面 HTML。
        subject_id: 条目 ID。

    Returns:
        书籍详情，解析失败返回 None。
    """
    soup = BeautifulSoup(html, "html.parser")

    try:
        info_div = soup.find("div", id="info")
        if not info_div:
            return None

        info_text = info_div.get_text()

        title = _extract_title(soup)
        subtitle = _extract_field(info_text, "副标题")
        author = _extract_list_field(info_text, "作者")
        publisher = _extract_field(info_text, "出版社")
        producer = _extract_field(info_text, "出品方")
        publish_date = _extract_field(info_text, "出版年")
        isbn = _extract_field(info_text, "ISBN")
        pages = _parse_int(_extract_field(info_text, "页数"))
        price = _extract_field(info_text, "定价")
        binding = _extract_field(info_text, "装帧")
        series = _extract_field(info_text, "丛书")

        rating_value, rating_count = _extract_rating(soup)
        rating_distribution = _extract_rating_distribution(soup)

        summary = _extract_content(soup, "内容简介")
        author_intro = _extract_content(soup, "作者简介")

        return Book(
            id=subject_id,
            title=title,
            subtitle=subtitle,
            author=author,
            publisher=publisher,
            producer=producer,
            publish_date=publish_date,
            isbn=isbn,
            pages=pages,
            price=price,
            binding=binding,
            series=series,
            rating_value=rating_value,
            rating_count=rating_count,
            rating_distribution=rating_distribution,
            summary=summary,
            author_intro=author_intro,
            url=f"https://book.douban.com/subject/{subject_id}/",
        )
    except Exception:
        return None


def parse_movie_detail(html: str, subject_id: int) -> Movie | None:
    """解析电影详情页面。

    Args:
        html: 页面 HTML。
        subject_id: 条目 ID。

    Returns:
        电影详情，解析失败返回 None。
    """
    soup = BeautifulSoup(html, "html.parser")

    try:
        info_div = soup.find("div", id="info")
        if not info_div:
            return None

        info_text = info_div.get_text()

        title = _extract_title(soup)
        original_title = _extract_field(info_text, "原名")

        director = _extract_list_field(info_text, "导演")
        writers = _extract_list_field(info_text, "编剧")
        actors = _extract_list_field(info_text, "主演")

        genres = _extract_list_field(info_text, "类型")
        countries = _extract_list_field(info_text, "制片国家/地区")
        languages = _extract_list_field(info_text, "语言")

        release_date = _extract_field(info_text, "上映日期")
        runtime = _parse_runtime(info_text)

        rating_value, rating_count = _extract_rating(soup)
        rating_distribution = _extract_rating_distribution(soup)

        summary = _extract_content(soup, "剧情简介")

        return Movie(
            id=subject_id,
            title=title,
            original_title=original_title,
            director=director,
            writers=writers,
            actors=actors,
            genres=genres,
            countries=countries,
            languages=languages,
            release_date=release_date,
            runtime=runtime,
            rating_value=rating_value,
            rating_count=rating_count,
            rating_distribution=rating_distribution,
            summary=summary,
            url=f"https://movie.douban.com/subject/{subject_id}/",
        )
    except Exception:
        return None


def parse_music_detail(html: str, subject_id: int) -> Music | None:
    """解析音乐详情页面。

    Args:
        html: 页面 HTML。
        subject_id: 条目 ID。

    Returns:
        音乐详情，解析失败返回 None。
    """
    soup = BeautifulSoup(html, "html.parser")

    try:
        info_div = soup.find("div", id="info")
        if not info_div:
            return None

        info_text = info_div.get_text()

        title = _extract_title(soup)
        artist = _extract_field(info_text, "表演者")
        release_date = _extract_field(info_text, "发行时间")
        genres = _extract_list_field(info_text, "流派")

        rating_value, rating_count = _extract_rating(soup)
        rating_distribution = _extract_rating_distribution(soup)

        return Music(
            id=subject_id,
            title=title,
            artist=artist,
            release_date=release_date,
            genres=genres,
            rating_value=rating_value,
            rating_count=rating_count,
            rating_distribution=rating_distribution,
            url=f"https://music.douban.com/subject/{subject_id}/",
        )
    except Exception:
        return None


def parse_comments(html: str) -> list[Comment]:
    """解析短评页面。

    Args:
        html: 页面 HTML。

    Returns:
        短评列表。
    """
    soup = BeautifulSoup(html, "html.parser")
    comments = []

    comment_items = soup.select("li.comment-item, div.comment-item")

    for item in comment_items:
        try:
            comment_id = item.get("data-cid", "")
            if not comment_id:
                comment_id = item.get("data-id", "")

            user_link = item.select_one(".comment-info a")
            user_name = user_link.get_text(strip=True) if user_link else ""
            user_url = user_link.get("href") if user_link else None

            rating = None
            rating_span = item.select_one(
                "span.user-stars, span.allstar50, span.allstar40, "
                "span.allstar30, span.allstar20, span.allstar10"
            )
            if rating_span:
                rating_class = rating_span.get("class", [])
                for cls in rating_class:
                    if cls.startswith("allstar"):
                        rating = int(cls.replace("allstar", "")) // 10
                        break

            content_span = item.select_one("span.short")
            content = content_span.get_text(strip=True) if content_span else ""

            votes_span = item.select_one("span.vote-count, span.votes")
            votes = 0
            if votes_span:
                votes_text = votes_span.get_text(strip=True)
                try:
                    votes = int(votes_text)
                except ValueError:
                    pass

            time_elem = item.select_one("span.comment-time")
            created_at = None
            if time_elem:
                created_at = time_elem.get("title") or time_elem.get_text(strip=True)

            comments.append(
                Comment(
                    id=str(comment_id),
                    user_name=user_name,
                    user_url=user_url,
                    rating=rating,
                    content=content,
                    votes=votes,
                    created_at=created_at,
                )
            )
        except Exception:
            continue

    return comments


def _extract_title(soup: BeautifulSoup) -> str:
    """提取标题。"""
    title_span = soup.select_one("h1 span[property='v:itemreviewed']")
    if title_span:
        return title_span.get_text(strip=True)

    h1 = soup.find("h1")
    if h1:
        return h1.get_text(strip=True)

    return ""


def _extract_field(text: str, label: str) -> str | None:
    """提取单个字段。"""
    lookahead = (
        "作者|出版社|出品方|出版年|页数|定价|装帧|丛书|ISBN|"
        "副标题|原名|导演|编剧|主演|类型|制片国家|语言|"
        "上映日期|片长|表演者|发行时间|流派|又名"
    )
    pattern = rf"{label}[:\s]*(.+?)(?=\n|$|{lookahead})"
    match = re.search(pattern, text)
    if match:
        value = match.group(1).strip()
        value = re.sub(r"\s+", " ", value)
        return value if value else None
    return None


def _extract_list_field(text: str, label: str) -> list[str]:
    """提取列表字段。"""
    lookahead = (
        "作者|出版社|出品方|出版年|页数|定价|装帧|丛书|ISBN|"
        "副标题|原名|导演|编剧|主演|类型|制片国家|语言|"
        "上映日期|片长|表演者|发行时间|流派|又名"
    )
    pattern = rf"{label}[:\s]*(.+?)(?=\n|$|{lookahead})"
    match = re.search(pattern, text)
    if match:
        value = match.group(1).strip()
        items = re.split(r"[/\s]+", value)
        return [item.strip() for item in items if item.strip()]
    return []


def _extract_rating(soup: BeautifulSoup) -> tuple[float | None, int]:
    """提取评分。"""
    rating_value = None
    rating_count = 0

    rating_num = soup.select_one("strong.rating_num")
    if rating_num:
        try:
            rating_value = float(rating_num.get_text(strip=True))
        except ValueError:
            pass

    rating_people = soup.select_one("span.rating_people span")
    if rating_people:
        try:
            rating_count = int(rating_people.get_text(strip=True))
        except ValueError:
            pass

    return rating_value, rating_count


def _extract_rating_distribution(soup: BeautifulSoup) -> Rating | None:
    """提取评分分布。"""
    rating_per = soup.select("span.rating_per")
    if len(rating_per) < 5:
        return None

    try:

        def parse_percent(text: str) -> float:
            return float(text.replace("%", "").strip())

        return Rating(
            stars_5=parse_percent(rating_per[0].get_text(strip=True)),
            stars_4=parse_percent(rating_per[1].get_text(strip=True)),
            stars_3=parse_percent(rating_per[2].get_text(strip=True)),
            stars_2=parse_percent(rating_per[3].get_text(strip=True)),
            stars_1=parse_percent(rating_per[4].get_text(strip=True)),
        )
    except (ValueError, IndexError):
        return None


def _extract_content(soup: BeautifulSoup, heading: str) -> str:
    """提取内容区块（简介等）。"""
    for h2 in soup.find_all("h2"):
        if heading in h2.get_text():
            content_div = h2.find_next_sibling("div", class_="indent")
            if content_div:
                for hidden in content_div.find_all(class_="hidden"):
                    hidden.decompose()
                return content_div.get_text(strip=True)
    return ""


def _parse_int(value: str | None) -> int | None:
    """解析整数。"""
    if not value:
        return None
    match = re.search(r"\d+", value)
    return int(match.group()) if match else None


def _parse_runtime(text: str) -> int | None:
    """解析片长。"""
    pattern = r"片长[:\s]*(\d+)"
    match = re.search(pattern, text)
    if match:
        return int(match.group(1))
    return None
