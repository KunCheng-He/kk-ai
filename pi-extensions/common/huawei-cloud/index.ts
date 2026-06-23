/**
 * 华为云 ModelArts 提供商扩展
 *
 * 注册华为云作为 Pi 的自定义提供商，支持以下模型：
 *   - deepseek-v4-pro / deepseek-v4-flash
 *   - glm-5 / glm-5.1 / glm-5.2
 *
 * 使用方式：
 *   1. 设置环境变量: export HUAWEI_CLOUD_API_KEY="你的API Key"
 *   2. 启动 pi 即可自动加载
 *   3. 使用 /model 切换模型，例如: /model huawei-cloud/deepseek-v4-pro
 */

import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

export default function (pi: ExtensionAPI) {
  pi.registerProvider("huawei-cloud", {
    name: "华为云",
    baseUrl: "https://api.modelarts-maas.com/openai/v1",
    apiKey: "$HUAWEI_CLOUD_API_KEY",
    api: "openai-completions",
    models: [
      {
        id: "deepseek-v4-pro",
        name: "DeepSeek V4 Pro",
        reasoning: true,
        input: ["text"],
        cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
        contextWindow: 1000000,
        maxTokens: 128000,
        compat: {
          supportsDeveloperRole: false,
          thinkingFormat: "deepseek",
        },
      },
      {
        id: "deepseek-v4-flash",
        name: "DeepSeek V4 Flash",
        reasoning: true,
        input: ["text"],
        cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
        contextWindow: 1000000,
        maxTokens: 128000,
        compat: {
          supportsDeveloperRole: false,
          thinkingFormat: "deepseek",
        },
      },
      {
        id: "glm-5.1",
        name: "GLM 5.1",
        reasoning: true,
        input: ["text"],
        cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
        contextWindow: 200000,
        maxTokens: 128000,
        compat: {
          supportsDeveloperRole: false,
        },
      },
      {
        id: "glm-5",
        name: "GLM 5",
        reasoning: true,
        input: ["text"],
        cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
        contextWindow: 200000,
        maxTokens: 65536,
        compat: {
          supportsDeveloperRole: false,
        },
      },
      {
        id: "glm-5.2",
        name: "GLM 5.2",
        reasoning: true,
        input: ["text"],
        cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
        contextWindow: 1000000,
        maxTokens: 128000,
        compat: {
          supportsDeveloperRole: false,
        },
      },
    ],
  });
}
