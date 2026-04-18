from typing import Optional, List
from pydantic import BaseModel


class User(BaseModel):
    user_id: str
    nickname: str
    avatar: Optional[str] = None
    desc: Optional[str] = None


class Note(BaseModel):
    note_id: str
    xsec_token: Optional[str] = None
    title: str
    desc: Optional[str] = None
    cover: Optional[str] = None
    author: User
    liked_count: int = 0
    comment_count: int = 0
    collect_count: int = 0
    share_count: int = 0
    tag_list: List[str] = []

    @property
    def url(self) -> str:
        if self.xsec_token:
            return f"https://www.xiaohongshu.com/explore/{self.note_id}?xsec_token={self.xsec_token}&xsec_source=pc_feed"
        return f"https://www.xiaohongshu.com/explore/{self.note_id}"


class NoteDetail(BaseModel):
    note_id: str
    title: str
    desc: Optional[str] = None
    cover: Optional[str] = None
    author: User
    liked_count: int = 0
    comment_count: int = 0
    collect_count: int = 0
    share_count: int = 0
    tag_list: List[str] = []
    create_time: int = 0
    update_time: int = 0
    location: Optional[str] = None
    image_list: List[str] = []

    @property
    def url(self) -> str:
        return f"https://www.xiaohongshu.com/explore/{self.note_id}"


class Comment(BaseModel):
    comment_id: str
    user: User
    content: str
    liked_count: int = 0
    create_time: int = 0
    reply_comment_id: Optional[str] = None


class NoteDetailWithComments(BaseModel):
    note: NoteDetail
    comment_list: List[Comment] = []


class SearchResult(BaseModel):
    items: List[Note]
    total: int = 0
    has_more: bool = False
