import functools
import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import requests

from config import TokenCache, WechatConfig


def retry(max_retries: int = 3, delay: float = 1.0):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except WechatAPIError as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        time.sleep(delay)
            raise last_error
        return wrapper
    return decorator


class WechatAPIError(Exception):
    def __init__(self, errcode: int, errmsg: str):
        self.errcode = errcode
        self.errmsg = errmsg
        super().__init__(f"[{errcode}] {errmsg}")


@dataclass
class UploadResult:
    media_id: str
    url: str


@dataclass
class DraftResult:
    media_id: str


class WechatAPI:
    BASE_URL = "https://api.weixin.qq.com/cgi-bin"

    def __init__(self, config: WechatConfig):
        self.config = config
        self.token_cache = TokenCache(config.appid)
        self._access_token: Optional[str] = None

    def get_access_token(self) -> str:
        cached = self.token_cache.get()
        if cached:
            return cached

        url = f"{self.BASE_URL}/token"
        params = {
            "grant_type": "client_credential",
            "appid": self.config.appid,
            "secret": self.config.secret,
        }

        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()

        if "errcode" in data and data["errcode"] != 0:
            raise WechatAPIError(data["errcode"], data.get("errmsg", "获取 access_token 失败"))

        access_token = data["access_token"]
        expires_in = data.get("expires_in", 7200)
        self.token_cache.set(access_token, expires_in)

        return access_token

    @retry(max_retries=3, delay=1.0)
    def upload_image(self, file_path: str) -> UploadResult:
        access_token = self.get_access_token()
        url = f"{self.BASE_URL}/media/uploadimg"
        params = {"access_token": access_token}

        with open(file_path, "rb") as f:
            files = {"media": f}
            resp = requests.post(url, params=params, files=files, timeout=30)

        data = resp.json()

        if "errcode" in data and data["errcode"] != 0:
            raise WechatAPIError(data["errcode"], data.get("errmsg", "上传图片失败"))

        return UploadResult(
            media_id=data.get("media_id", ""),
            url=data["url"]
        )

    @retry(max_retries=3, delay=1.0)
    def upload_material(self, file_path: str) -> UploadResult:
        access_token = self.get_access_token()
        url = f"{self.BASE_URL}/material/add_material"
        params = {
            "access_token": access_token,
            "type": "image"
        }

        with open(file_path, "rb") as f:
            files = {"media": f}
            resp = requests.post(url, params=params, files=files, timeout=30)

        data = resp.json()

        if "errcode" in data and data["errcode"] != 0:
            raise WechatAPIError(data["errcode"], data.get("errmsg", "上传素材失败"))

        return UploadResult(
            media_id=data["media_id"],
            url=data.get("url", "")
        )

    @retry(max_retries=3, delay=1.0)
    def create_draft(
        self,
        title: str,
        content: str,
        thumb_media_id: str,
        author: str = "",
        digest: str = "",
        content_source_url: str = "",
    ) -> DraftResult:
        access_token = self.get_access_token()
        url = f"{self.BASE_URL}/draft/add"
        params = {"access_token": access_token}

        article = {
            "title": title,
            "content": content,
            "thumb_media_id": thumb_media_id,
        }

        if author:
            article["author"] = author
        if digest:
            article["digest"] = digest
        if content_source_url:
            article["content_source_url"] = content_source_url

        payload = {"articles": [article]}

        headers = {"Content-Type": "application/json"}
        json_data = json.dumps(payload, ensure_ascii=False)
        resp = requests.post(url, params=params, data=json_data.encode("utf-8"), headers=headers, timeout=30)
        data = resp.json()

        if "errcode" in data and data["errcode"] != 0:
            raise WechatAPIError(data["errcode"], data.get("errmsg", "创建草稿失败"))

        return DraftResult(media_id=data["media_id"])

    def clear_token_cache(self):
        self.token_cache.clear()
