import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class WechatConfig:
    appid: str
    secret: str

    @classmethod
    def from_env(cls) -> "WechatConfig":
        appid = os.getenv("WECHAT_GZH_APPID")
        secret = os.getenv("WECHAT_GZH_SECRET")

        if not appid:
            raise ValueError("环境变量 WECHAT_GZH_APPID 未设置")
        if not secret:
            raise ValueError("环境变量 WECHAT_GZH_SECRET 未设置")

        return cls(appid=appid, secret=secret)


class TokenCache:
    CACHE_DIR = Path.home() / ".cache" / "wechat-gzh-skill"
    CACHE_FILE = CACHE_DIR / "token.json"

    def __init__(self, appid: str):
        self.appid = appid
        self._ensure_cache_dir()

    def _ensure_cache_dir(self):
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)

    def get(self) -> Optional[str]:
        if not self.CACHE_FILE.exists():
            return None

        try:
            with open(self.CACHE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            if data.get("appid") != self.appid:
                return None

            expires_at = data.get("expires_at", 0)
            if time.time() >= expires_at:
                return None

            return data.get("access_token")
        except (json.JSONDecodeError, KeyError):
            return None

    def set(self, access_token: str, expires_in: int = 7200):
        expires_at = int(time.time()) + expires_in - 300

        data = {
            "appid": self.appid,
            "access_token": access_token,
            "expires_at": expires_at,
        }

        with open(self.CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def clear(self):
        if self.CACHE_FILE.exists():
            self.CACHE_FILE.unlink()


def load_config() -> WechatConfig:
    return WechatConfig.from_env()
