"""
图像生成提供商实现

包含火山引擎、智谱AI、阿里云百炼三个提供商的具体实现
"""

import httpx

from .base import BaseProvider, GenerateParams, ImageResult


class VolcengineProvider(BaseProvider):
    """火山引擎图像生成提供商

    使用 Seedream 5.0 模型，支持文生图、图生图、组图生成
    支持 2K/4K 高分辨率输出
    """

    name = "volcengine"
    api_key_env = "volcengine_api_key"
    api_url = "https://ark.cn-beijing.volces.com/api/v3/images/generations"
    model = "doubao-seedream-5-0-260128"

    def generate(self, params: GenerateParams, api_key: str) -> list[ImageResult]:
        payload = {
            "model": self.model,
            "prompt": params.prompt,
            "size": params.size,
            "response_format": params.response_format,
            "watermark": params.watermark,
            "sequential_image_generation": "disabled",
        }

        if params.image:
            payload["image"] = params.image

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

        with httpx.Client(timeout=120) as client:
            response = client.post(self.api_url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

        results = []
        for item in data.get("data", []):
            if params.response_format == "url":
                results.append(ImageResult(url=item.get("url")))
            else:
                results.append(ImageResult(base64=item.get("b64_json")))

        return results

    def get_supported_sizes(self) -> list[str]:
        return [
            "2048x2048",
            "2304x1728",
            "1728x2304",
            "2848x1600",
            "1600x2848",
            "2496x1664",
            "1664x2496",
            "3136x1344",
            "4096x4096",
            "3520x4704",
            "4704x3520",
            "5504x3040",
            "3040x5504",
            "3328x4992",
            "4992x3328",
            "6240x2656",
            "2K",
            "4K",
        ]


class ZhipuProvider(BaseProvider):
    """智谱AI图像生成提供商

    使用 GLM-Image 模型，生成速度快，支持多种尺寸
    """

    name = "zhipu"
    api_key_env = "zhipu_api_key"
    api_url = "https://open.bigmodel.cn/api/paas/v4/images/generations"
    model = "glm-image"

    def generate(self, params: GenerateParams, api_key: str) -> list[ImageResult]:
        payload = {
            "model": self.model,
            "prompt": params.prompt,
            "size": params.size,
            "watermark_enabled": params.watermark,
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

        with httpx.Client(timeout=120) as client:
            response = client.post(self.api_url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

        results = []
        for item in data.get("data", []):
            results.append(ImageResult(url=item.get("url")))

        return results

    def get_supported_sizes(self) -> list[str]:
        return [
            "1280x1280",
            "1568x1056",
            "1056x1568",
            "1472x1088",
            "1088x1472",
            "1728x960",
            "960x1728",
            "1024x1024",
            "768x1344",
            "864x1152",
            "1344x768",
            "1152x864",
            "1440x720",
            "720x1440",
        ]


class AliyunProvider(BaseProvider):
    """阿里云百炼图像生成提供商

    使用 Qwen-Image 模型，擅长复杂文本渲染和多样化艺术风格
    """

    name = "aliyun"
    api_key_env = "aliyun_api_key"
    api_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
    model = "qwen-image-2.0-pro"

    def generate(self, params: GenerateParams, api_key: str) -> list[ImageResult]:
        size = params.size.replace("x", "*")

        payload = {
            "model": self.model,
            "input": {
                "messages": [
                    {
                        "role": "user",
                        "content": [{"text": params.prompt}],
                    }
                ]
            },
            "parameters": {
                "size": size,
                "n": params.n,
                "watermark": params.watermark,
                "prompt_extend": True,
            },
        }

        if params.negative_prompt:
            payload["parameters"]["negative_prompt"] = params.negative_prompt

        if params.seed is not None:
            payload["parameters"]["seed"] = params.seed

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

        with httpx.Client(timeout=120) as client:
            response = client.post(self.api_url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

        results = []
        for choice in data.get("output", {}).get("choices", []):
            for content in choice.get("message", {}).get("content", []):
                if "image" in content:
                    results.append(ImageResult(url=content["image"]))

        return results

    def get_supported_sizes(self) -> list[str]:
        return [
            "2048x2048",
            "2688x1536",
            "1536x2688",
            "2368x1728",
            "1728x2368",
            "1664x928",
            "1472x1104",
            "1328x1328",
            "1104x1472",
            "928x1664",
        ]
