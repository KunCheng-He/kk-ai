from typing import Optional, List, Dict, Any
from playwright.async_api import BrowserContext, Page, Route, Request
from xhs_utils.data_models import (
    SearchResult,
    Note,
    User,
    NoteDetail,
    Comment,
    NoteDetailWithComments,
)


class XHSApiHandler:
    def __init__(self, context: Optional[BrowserContext]):
        self.context = context
        self.page: Optional[Page] = None
        self.search_data: List[Dict[str, Any]] = []

    async def _intercept_api(self, route: Route, request: Request):
        response = await route.fetch()
        try:
            data = await response.json()
            if "items" in data or ("data" in data and "items" in data.get("data", {})):
                self.search_data.append(data)
        except Exception:
            pass
        await route.continue_()

    async def search(self, keyword: str, limit: int = 20) -> SearchResult:
        if not self.context:
            raise ValueError("Browser context is not available")

        self.page = await self.context.new_page()
        self.search_data = []

        await self.page.route("**/api/sns/web/v1/search/notes*", self._intercept_api)

        search_url = (
            f"https://www.xiaohongshu.com/search_result?keyword={keyword}&type=51"
        )
        await self.page.goto(search_url)
        await self.page.wait_for_timeout(3000)

        for _ in range(3):
            await self.page.mouse.wheel(0, 500)
            await self.page.wait_for_timeout(1000)

        items = []

        for data in self.search_data:
            result_items = (
                data.get("data", {}).get("items", [])
                if "data" in data
                else data.get("items", [])
            )
            for item in result_items:
                note_card = item.get("note_card", {})
                if note_card:
                    try:
                        user_info = note_card.get("user", {})
                        interact_info = note_card.get("interact_info", {})
                        cover_info = note_card.get("cover", {})

                        author = User(
                            user_id=user_info.get("user_id", ""),
                            nickname=user_info.get("nickname", "")
                            or user_info.get("nick_name", ""),
                            avatar=user_info.get("avatar", ""),
                        )

                        note = Note(
                            note_id=item.get("note_id", "") or item.get("id", ""),
                            xsec_token=item.get("xsec_token", ""),
                            title=note_card.get("display_title", ""),
                            cover=cover_info.get("url_default", "")
                            or cover_info.get("url", ""),
                            liked_count=int(interact_info.get("liked_count", 0) or 0),
                            comment_count=int(
                                interact_info.get("comment_count", 0) or 0
                            ),
                            collect_count=int(
                                interact_info.get("collected_count", 0) or 0
                            ),
                            share_count=int(interact_info.get("shared_count", 0) or 0),
                            author=author,
                        )
                        items.append(note)
                    except Exception:
                        pass

        await self.page.close()
        return SearchResult(
            items=items[:limit], total=len(items), has_more=len(items) > limit
        )

    async def _intercept_note_detail(self, route: Route, request: Request):
        response = await route.fetch()
        try:
            data = await response.json()
            if "data" in data:
                self.note_detail_data = data["data"]
        except Exception:
            pass
        await route.continue_()

    async def _intercept_comments(self, route: Route, request: Request):
        response = await route.fetch()
        try:
            data = await response.json()
            if "data" in data and "comments" in data["data"]:
                self.comments_data = data["data"]["comments"]
        except Exception:
            pass
        await route.continue_()

    async def get_note_detail(
        self, note_id: str, xsec_token: Optional[str] = None
    ) -> NoteDetailWithComments:
        if not self.context:
            raise ValueError("Browser context is not available")

        self.page = await self.context.new_page()
        self.note_detail_data = None
        self.comments_data = []

        detail_url = f"https://www.xiaohongshu.com/explore/{note_id}"
        if xsec_token:
            detail_url += f"?xsec_token={xsec_token}&xsec_source=pc_feed"

        await self.page.route(
            "**/api/sns/web/v2/comment/page*", self._intercept_comments
        )

        await self.page.goto(detail_url)
        await self.page.wait_for_timeout(3000)

        viewport = await self.page.evaluate(
            "() => ({ width: window.innerWidth, height: window.innerHeight })"
        )
        comment_x = viewport["width"] * 0.75
        comment_y = viewport["height"] * 0.5

        await self.page.mouse.move(comment_x, comment_y)

        for _ in range(5):
            await self.page.mouse.wheel(0, 300)
            await self.page.wait_for_timeout(800)

        note_data = await self.page.evaluate(
            """() => {
                const state = window.__INITIAL_STATE__;
                if (!state || !state.note || !state.note.noteDetailMap) return null;
                const noteDetailMap = state.note.noteDetailMap;
                const keys = Object.keys(noteDetailMap);
                if (!keys.length) return null;
                const firstKey = keys[0];
                const detail = noteDetailMap[firstKey];
                if (!detail || !detail.note) return null;
                const note = detail.note;
                const interactInfo = note.interact_info || {};
                return {
                    title: note.title || '',
                    desc: note.desc || '',
                    user: note.user ? {
                        user_id: note.user.user_id || note.user.userId || '',
                        nickname: note.user.nickname || note.user.nick_name || '',
                        avatar: note.user.avatar || note.user.image || ''
                    } : null,
                    liked_count: interactInfo.liked_count || note.liked_count || 0,
                    comment_count: interactInfo.comment_count || note.comment_count || 0,
                    collected_count: interactInfo.collected_count || note.collected_count || 0,
                    shared_count: interactInfo.shared_count || note.shared_count || 0,
                    time: note.time || 0,
                    cover: note.cover ? (note.cover.url_default || note.cover.url || note.cover) : null,
                    image_list: (note.image_list || []).map(img => {
                        if (typeof img === 'string') return img;
                        return img.url_default || img.url || img.info_list?.[0]?.url || '';
                    }),
                    tag_list: (note.tag_list || []).map(tag => tag.name || tag)
                };
            }"""
        )

        if note_data:
            try:
                user_info = note_data.get("user", {})
                author = User(
                    user_id=user_info.get("user_id", ""),
                    nickname=user_info.get("nickname", ""),
                    avatar=user_info.get("avatar", ""),
                )

                cover = note_data.get("cover")
                if isinstance(cover, dict):
                    cover = cover.get("url_default") or cover.get("url")

                note_detail = NoteDetail(
                    note_id=note_id,
                    title=note_data.get("title", ""),
                    desc=note_data.get("desc", ""),
                    cover=cover,
                    liked_count=int(note_data.get("liked_count", 0) or 0),
                    comment_count=int(note_data.get("comment_count", 0) or 0),
                    collect_count=int(note_data.get("collected_count", 0) or 0),
                    share_count=int(note_data.get("shared_count", 0) or 0),
                    tag_list=note_data.get("tag_list", []),
                    create_time=note_data.get("time", 0) or 0,
                    update_time=note_data.get("update_time", 0) or 0,
                    location=note_data.get("location"),
                    image_list=note_data.get("image_list", []),
                    author=author,
                )
            except Exception:
                note_detail = None
        else:
            note_detail = None

        comments = []
        if self.comments_data:
            for comment_item in self.comments_data:
                try:
                    user_info = comment_item.get("user_info", {})
                    comment = Comment(
                        comment_id=comment_item.get("id", ""),
                        user=User(
                            user_id=user_info.get("user_id", "")
                            or user_info.get("userId", ""),
                            nickname=user_info.get("nickname", "")
                            or user_info.get("nick_name", ""),
                            avatar=user_info.get("avatar", "")
                            or user_info.get("image", ""),
                        ),
                        content=comment_item.get("content", ""),
                        liked_count=int(comment_item.get("like_count", 0) or 0),
                        create_time=comment_item.get("create_time", 0) or 0,
                        reply_comment_id=comment_item.get("reply_comment_id"),
                    )
                    comments.append(comment)
                except Exception:
                    pass

        await self.page.close()
        return NoteDetailWithComments(
            note=note_detail
            or NoteDetail(
                note_id=note_id,
                title="",
                author=User(user_id="", nickname="Unknown"),
            ),
            comment_list=comments,
        )
