/**
 * 白山智算 (Baishan Intelligent Computing) 提供商扩展
 *
 * 注册白山智算作为 Pi 的自定义提供商，支持 OpenAI 兼容的 Chat Completions API。
 *
 * API 文档: https://ai.baishan.com/docs/docs/llm-api.html
 * 模型广场: https://ai.baishan.com/market/models
 * API 地址: https://api.edgefn.net/v1
 *
 * 使用方式：
 *   1. 设置环境变量: export BAISHAN_API_KEY="你的API Key"
 *      (API Key 获取: https://ai.baishan.com/key/index)
 *   2. 启动 pi 即可自动加载
 *   3. 使用 /model 切换模型，例如: /model baishan/deepseek-v3.2
 *
 * 价格说明：价格为每百万 Token (¥ CNY)，当前有充值 85 折活动 (截至 2026/7/9)。
 *   以下价格为原价，实际计费以控制台为准。
 */

import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

export default function (pi: ExtensionAPI) {
  pi.registerProvider("baishan", {
    name: "白山智算",
    baseUrl: "https://api.edgefn.net/v1",
    apiKey: "$BAISHAN_API_KEY",
    api: "openai-completions",
    models: [
      // ============ DeepSeek 系列 ============
      {
        id: "DeepSeek-V4-Pro",
        name: "DeepSeek V4 Pro (白山)",
        reasoning: true,
        input: ["text"],
        cost: { input: 12, output: 24, cacheRead: 1, cacheWrite: 1 },
        contextWindow: 1000000,
        maxTokens: 128000,
        compat: {
          supportsDeveloperRole: false,
          thinkingFormat: "deepseek",
        },
      },
      {
        id: "DeepSeek-V4-Flash",
        name: "DeepSeek V4 Flash (白山)",
        reasoning: true,
        input: ["text"],
        cost: { input: 1, output: 2, cacheRead: 0.2, cacheWrite: 0.2 },
        contextWindow: 1000000,
        maxTokens: 128000,
        compat: {
          supportsDeveloperRole: false,
          thinkingFormat: "deepseek",
        },
      },

      // ============ GLM 系列 ============
      {
        id: "GLM-5.1",
        name: "GLM 5.1 (白山)",
        reasoning: true,
        input: ["text"],
        cost: { input: 8, output: 28, cacheRead: 2, cacheWrite: 2 },
        contextWindow: 200000,
        maxTokens: 128000,
        compat: {
          supportsDeveloperRole: false,
        },
      },
      {
        id: "GLM-5",
        name: "GLM 5 (白山)",
        reasoning: true,
        input: ["text"],
        cost: { input: 6, output: 22, cacheRead: 1.5, cacheWrite: 1.5 },
        contextWindow: 200000,
        maxTokens: 128000,
        compat: {
          supportsDeveloperRole: false,
        },
      },
      {
        id: "GLM-4.7",
        name: "GLM 4.7 (白山)",
        reasoning: true,
        input: ["text"],
        cost: { input: 4, output: 16, cacheRead: 0, cacheWrite: 0 },
        contextWindow: 200000,
        maxTokens: 128000,
        compat: {
          supportsDeveloperRole: false,
        },
      },

      // ============ 其他 ============
      {
        id: "MiniMax-M2.5",
        name: "MiniMax M2.5 (白山)",
        reasoning: true,
        input: ["text"],
        cost: { input: 2.1, output: 8.4, cacheRead: 0, cacheWrite: 0 },
        contextWindow: 200000,
        maxTokens: 128000,
        compat: {
          supportsDeveloperRole: false,
        },
      },
    ],
  });
}
