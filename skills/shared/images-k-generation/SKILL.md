---
name: image-generation
description: 图像生成技能。当用户需要生成图片、创建图像、AI绘画时使用此技能。触发场景包括：文生图、图生图、生成插画、生成海报、生成头像、生成背景图、AI作画等。即使用户没有明确说"生成图片"，但上下文暗示需要创建视觉内容时也应触发。
---

# Image Generation Skill

图像生成技能。当 Agent 需要生成图片时调用此技能。

## 快速开始

```bash
cd scripts && uv run python generate.py --provider <provider> --prompt "<prompt>"
```

## 可用提供商

| 提供商 | 说明 | 推荐尺寸 |
|--------|------|----------|
| volcengine | 火山引擎 - Seedream 5.0，支持图生图/组图 | 2048x2048, 2K, 4K |
| zhipu | 智谱AI - GLM-Image，快速生成 | 1280x1280 |
| aliyun | 阿里云百炼 - Qwen-Image，擅长文字渲染 | 2048x2048 |

## 命令参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--provider, -p` | 提供商 (volcengine/zhipu/aliyun) | 必填 |
| `--prompt` | 文本提示词 | 必填 |
| `--size` | 图片尺寸 | 1024x1024 |
| `--negative-prompt` | 反向提示词 | - |
| `--image` | 参考图片 URL（支持多个） | - |
| `--n` | 生成数量 | 1 |
| `--format` | 输出格式 (url/base64) | url |
| `--watermark` | 添加水印 | false |
| `--seed` | 随机种子 | - |
| `--output, -o` | base64 图片保存目录 | - |
| `--list-sizes` | 列出支持的尺寸 | - |

## 使用示例

### 文生图

```bash
uv run python generate.py --provider zhipu --prompt "一只可爱的橘猫坐在窗台上"
```

### 指定尺寸

```bash
uv run python generate.py --provider volcengine --prompt "山水画" --size 2048x2048
```

### 图生图

```bash
uv run python generate.py --provider volcengine --prompt "转换为油画风格" --image https://example.com/cat.jpg
```

### 查看支持的尺寸

```bash
uv run python generate.py --provider aliyun --list-sizes
```

## API Keys

API Key 存储在项目根目录 `.env` 文件中，脚本会自动读取。
