#!/usr/bin/env python3
"""
图像生成 CLI 工具

提供统一的命令行接口，支持火山引擎、智谱AI、阿里云百炼三个提供商

使用示例:
    uv run python generate.py --provider zhipu --prompt "一只可爱的橘猫"
    uv run python generate.py --provider volcengine --prompt "山水画" --size 2048x2048
    uv run python generate.py --provider aliyun --list-sizes
"""

import argparse
import base64
import os
import sys
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))

from providers import (
    AliyunProvider,
    GenerateParams,
    ImageResult,
    VolcengineProvider,
    ZhipuProvider,
)

PROVIDERS = {
    "volcengine": VolcengineProvider,
    "zhipu": ZhipuProvider,
    "aliyun": AliyunProvider,
}


def load_api_key(provider_name: str) -> str:
    """从 .env 文件加载指定提供商的 API Key

    Args:
        provider_name: 提供商名称

    Returns:
        API Key 字符串

    Raises:
        ValueError: API Key 未找到
    """
    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(env_path)

    provider = PROVIDERS[provider_name]
    api_key = os.getenv(provider.api_key_env)

    if not api_key:
        raise ValueError(f"API key not found: {provider.api_key_env}")

    return api_key


def save_base64_image(base64_data: str, output_dir: Path, index: int) -> str:
    """将 base64 编码的图片保存到文件

    Args:
        base64_data: base64 编码的图片数据
        output_dir: 输出目录
        index: 图片序号

    Returns:
        保存的文件路径
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    file_path = output_dir / f"generated_{index}.png"

    image_data = base64.b64decode(base64_data)
    file_path.write_bytes(image_data)

    return str(file_path)


def generate(
    provider: Literal["volcengine", "zhipu", "aliyun"],
    prompt: str,
    size: str = "1024x1024",
    negative_prompt: str | None = None,
    image: str | list[str] | None = None,
    n: int = 1,
    response_format: Literal["url", "base64"] = "url",
    watermark: bool = False,
    seed: int | None = None,
    output_dir: str | None = None,
) -> list[ImageResult]:
    """生成图像

    Args:
        provider: 图像生成提供商
        prompt: 文本提示词
        size: 图像尺寸
        negative_prompt: 反向提示词
        image: 参考图片 URL
        n: 生成数量
        response_format: 响应格式
        watermark: 是否添加水印
        seed: 随机种子
        output_dir: base64 图片保存目录

    Returns:
        生成结果列表
    """
    api_key = load_api_key(provider)
    provider_cls = PROVIDERS[provider]
    provider_instance = provider_cls()

    params = GenerateParams(
        prompt=prompt,
        size=size,
        negative_prompt=negative_prompt,
        image=image,
        n=n,
        response_format=response_format,
        watermark=watermark,
        seed=seed,
    )

    results = provider_instance.generate(params, api_key)

    if output_dir and response_format == "base64":
        output_path = Path(output_dir)
        for i, result in enumerate(results):
            if result.base64:
                result.file_path = save_base64_image(result.base64, output_path, i)

    return results


def main():
    parser = argparse.ArgumentParser(description="Generate images using AI providers")
    parser.add_argument(
        "--provider",
        "-p",
        required=True,
        choices=PROVIDERS.keys(),
        help="Image generation provider",
    )
    parser.add_argument("--prompt", help="Text prompt for image generation")
    parser.add_argument(
        "--size", default="1024x1024", help="Image size (e.g., 1024x1024, 2048x2048)"
    )
    parser.add_argument(
        "--negative-prompt", help="Negative prompt (avoid these elements)"
    )
    parser.add_argument(
        "--image", nargs="+", help="Reference image URL(s) for image-to-image"
    )
    parser.add_argument("--n", type=int, default=1, help="Number of images to generate")
    parser.add_argument(
        "--format", choices=["url", "base64"], default="url", help="Response format"
    )
    parser.add_argument(
        "--watermark", action="store_true", help="Add watermark to generated image"
    )
    parser.add_argument("--seed", type=int, help="Random seed for reproducibility")
    parser.add_argument("--output", "-o", help="Output directory for base64 images")
    parser.add_argument(
        "--list-sizes", action="store_true", help="List supported sizes for provider"
    )

    args = parser.parse_args()

    if args.list_sizes:
        provider = PROVIDERS[args.provider]()
        print(f"Supported sizes for {args.provider}:")
        for size in provider.get_supported_sizes():
            print(f"  {size}")
        return

    if not args.prompt:
        parser.error("--prompt is required when not using --list-sizes")

    ref_image = args.image[0] if args.image and len(args.image) == 1 else args.image

    results = generate(
        provider=args.provider,
        prompt=args.prompt,
        size=args.size,
        negative_prompt=args.negative_prompt,
        image=ref_image,
        n=args.n,
        response_format=args.format,
        watermark=args.watermark,
        seed=args.seed,
        output_dir=args.output,
    )

    for i, result in enumerate(results):
        if result.url:
            print(f"Image {i + 1} URL: {result.url}")
        if result.file_path:
            print(f"Image {i + 1} saved to: {result.file_path}")


if __name__ == "__main__":
    main()
