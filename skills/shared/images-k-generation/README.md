# Image Generation Skill

图像生成技能，提供统一的命令行接口，支持火山引擎、智谱AI、阿里云百炼三个提供商。

## 快速开始

```bash
cd scripts && uv run python generate.py --provider <provider> --prompt "<prompt>"
```

## 环境配置

1. 复制环境变量模板：

```bash
cp .env.example .env
```

2. 编辑 `.env` 文件，填入实际的 API Key：

```bash
volcengine_api_key=your_volcengine_api_key
zhipu_api_key=your_zhipu_api_key
aliyun_api_key=your_aliyun_api_key
```

### API Key 获取地址

| 提供商 | 获取地址 |
|--------|----------|
| 火山引擎 | https://console.volcengine.com/ark |
| 智谱AI | https://open.bigmodel.cn/ |
| 阿里云百炼 | https://bailian.console.aliyun.com/ |

## 可用提供商

| 提供商 | 模型 | 特点 | 推荐尺寸 |
|--------|------|------|----------|
| volcengine | Seedream 5.0 | 支持图生图/组图，高分辨率 | 2048x2048, 2K, 4K |
| zhipu | GLM-Image | 生成速度快 | 1024x1024, 1280x1280 |
| aliyun | Qwen-Image | 擅长文字渲染 | 2048x2048 |

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

## 注意事项

- **尺寸校验**：使用不支持的尺寸会报错并提示支持的尺寸列表
- **base64 格式**：volcengine 不支持 base64 格式，会自动降级为 url 并给出警告
- **网络代理**：如遇网络问题，可配置 `HTTP_PROXY` 和 `HTTPS_PROXY` 环境变量

## 项目结构

```text
images-k-generation/
├── SKILL.md           # Skill 定义文件
├── README.md          # 本文件
├── AGENTS.md          # AI Agent 开发指南
├── .env.example       # 环境变量模板
├── .env               # 环境变量文件（不纳入版本控制）
├── .gitignore
├── upstream.json      # 上游信息
└── scripts/           # 代码目录
    ├── pyproject.toml
    ├── generate.py    # CLI 入口
    └── providers/     # 提供商实现
        ├── __init__.py
        ├── base.py
        └── providers.py
```
