import functools
import io
import json
import os
import struct
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

    _PNG_SIGNATURE = b'\x89PNG\r\n\x1a\n'
    _CRITICAL_CHUNKS = {b'IHDR', b'PLTE', b'IDAT', b'IEND'}
    _MAX_CHUNK_SIZE = 50 * 1024 * 1024  # 50MB sanity limit

    @classmethod
    def _clean_png(cls, data: bytes) -> bytes:
        if data[:8] != cls._PNG_SIGNATURE:
            return data

        cleaned = bytearray(data[:8])
        pos = 8

        while pos < len(data):
            if pos + 12 > len(data):
                break
            length = struct.unpack(">I", data[pos:pos+4])[0]
            chunk_type = data[pos+4:pos+8]

            # Reject impossibly large chunks (corrupted data)
            if length > cls._MAX_CHUNK_SIZE:
                break
            # Reject chunks that extend past EOF
            if pos + 12 + length > len(data):
                break

            if chunk_type in cls._CRITICAL_CHUNKS:
                cleaned.extend(data[pos:pos+12+length])
            pos += 12 + length

        # Ensure IEND terminator
        if len(cleaned) < 12 or bytes(cleaned[-12:-8]) != b'IEND':
            cleaned.extend(b'\x00\x00\x00\x00IEND\xae\x42\x60\x82')

        return bytes(cleaned)

    @classmethod
    def _read_image(cls, file_path: str) -> tuple[bytes, str, str]:
        with open(file_path, 'rb') as f:
            data = f.read()

        ext = Path(file_path).suffix.lower()
        if ext == '.png':
            cleaned = cls._clean_png(data)
            return cleaned, Path(file_path).name, 'image/png'
        elif ext in ('.jpg', '.jpeg'):
            return data, Path(file_path).name, 'image/jpeg'
        else:
            return data, Path(file_path).name, 'application/octet-stream'

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

        data, filename, mime = self._read_image(file_path)
        files = {"media": (filename, io.BytesIO(data), mime)}
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

        data, filename, mime = self._read_image(file_path)
        files = {"media": (filename, io.BytesIO(data), mime)}
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
