"""
图像生成提供商基类定义
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal


@dataclass
class ImageResult:
    """图像生成结果"""

    url: str | None = None
    base64: str | None = None
    file_path: str | None = None


@dataclass
class GenerateParams:
    """图像生成参数

    Attributes:
        prompt: 正向提示词，描述期望生成的图像内容
        size: 图像尺寸，格式为 "宽x高"，如 "1024x1024"
        negative_prompt: 反向提示词，描述不希望出现的元素
        image: 参考图片 URL，支持单张或多张，用于图生图
        n: 生成图像数量
        response_format: 响应格式，url 返回临时链接，base64 返回编码数据
        watermark: 是否添加水印
        seed: 随机种子，用于复现结果
    """

    prompt: str
    size: str = "1024x1024"
    negative_prompt: str | None = None
    image: str | list[str] | None = None
    n: int = 1
    response_format: Literal["url", "base64"] = "url"
    watermark: bool = False
    seed: int | None = None


class BaseProvider(ABC):
    """图像生成提供商基类

    所有提供商需要实现 generate 和 get_supported_sizes 方法
    """

    name: str
    api_key_env: str

    @abstractmethod
    def generate(self, params: GenerateParams, api_key: str) -> list[ImageResult]:
        """生成图像

        Args:
            params: 生成参数
            api_key: API 密钥

        Returns:
            生成结果列表
        """
        pass

    @abstractmethod
    def get_supported_sizes(self) -> list[str]:
        """获取支持的图像尺寸列表"""
        pass
