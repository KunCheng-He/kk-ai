# 负向提示词库

负向提示词（negative prompt）是独立于正向描述的**抑制通道**：告诉模型"这些视觉特征不要出现在画面里"。

核心认知：负向词不是"反向许愿"，而是**降低某类特征的出现概率**。写得越贴近要压制的**同类缺陷**，压制越有效；但若负向词描述的是正向想要的画面，就会反噬（见规则 4）。

## 目录

- [四条基本规则](#四条基本规则)
- [通用负面词分类](#通用负面词分类)
- [场景预设组合](#场景预设组合)
- [模型承载方式对照](#模型承载方式对照)
- [各模型写法](#各模型写法)
- [两段式完整示例](#两段式完整示例)

## 四条基本规则

### 1. 负向通道内写特征标签，不写否定前缀

负向通道本身就是否定语义，再叠加否定词会削弱甚至反转效果。

> 这条只约束**标签式负向通道**（SD/Flux/MJ）。DALL·E、Gemini 这类只能走正向句的模型，用完整否定句反而更清楚，见下文「DALL·E 3 / GPT Image / Gemini」。

| ✗ 错误 | ✓ 正确 |
|--------|--------|
| `no watermark` | `watermark, signature, logo` |
| `没有多余的指头` | `extra fingers, mutated hands` |
| `不要模糊` | `blurry, out of focus, lowres` |

### 2. 按缺陷类别分组，从重到轻

画质缺陷 → 解剖/结构 → 文字水印 → 风格污染 → 场景污染。同类词相邻，便于模型把它们聚成同一条语义方向。

### 3. 数量与承载通道匹配

| 承载方式 | 建议数量 | 理由 |
|----------|----------|------|
| 独立负向输入框（SD/SDXL/ComfyUI 等） | 10–25 个 | 通道独立，容量大 |
| Flux（蒸馏引导模型） | 3–6 个画质词作兜底 | 负向通常近乎无效，长列表无收益 |
| `--no` 参数（Midjourney） | 3–6 项（经验建议） | 参数越长，正向语义被稀释 |
| 内联约束句（DALL·E / GPT Image / Gemini） | 0 个独立列表 | 改写为正向约束或句末短句 |

### 4. 与正向提示词做冲突检查

负向词和正向描述打架时，负向词常常赢，结果是画面被"洗掉"。

- 正向要 `极简、留白` → 负向不能写 `detailed, intricate`
- 正向要 `胶片颗粒感` → 负向不能写 `grainy, noisy`
- 正向要 `浅景深虚化` → 负向不能写 `blurry, bokeh`（这是想要的虚化，不是缺陷）
- 正向要 `低饱和复古` → 负向不能写 `desaturated, muted colors`
- 正向要 `高饱和霓虹/新海诚` → 负向不能写 `oversaturated`（高饱和正是要的效果）

> 校验方法：逐条把负向词念一遍，若它在描述**你想要的画面**，删掉它。

## 通用负面词分类

以下为英文标签（SD 系模型对英文标签的响应优于中文），中文等价词用于 DALL·E / Gemini 等自然语言模型。

### 画质与渲染缺陷

```
low quality, worst quality, normal quality, lowres, blurry, out of focus,
jpeg artifacts, compression artifacts, pixelated, banding, noise,
oversaturated, underexposed, overexposed, flat lighting, dull colors,
oversharpened, halo, chromatic aberration
```

中文：低质量、最差画质、低分辨率、模糊、失焦、JPEG 压缩伪影、色带、噪点、过饱和、欠曝、过曝、平淡光线、色彩发灰、过度锐化

### 人物解剖与结构

```
bad anatomy, bad proportions, deformed, disfigured, malformed limbs,
extra limbs, missing limbs, extra arms, extra legs, floating limbs,
long neck, twisted torso, fused limbs, fused fingers,
extra fingers, fewer fingers, mutated hands, poorly drawn hands,
asymmetric eyes, cross-eyed, misplaced ears
```

中文：解剖结构错误、比例失调、畸形、肢体多余或缺失、手指数量错误、手指粘连、手部绘制粗糙、眼睛不对称、胸腔与颈部衔接错位

### 面部与身份（编辑场景重点）

```
changed face, altered facial features, different identity, aged up,
aged down, different hairstyle, different skin tone, waxy skin,
plastic skin, over-smoothed skin, airbrushed, doll-like face
```

中文：面部被改变、五官改变、身份漂移、被显老/显小、发型改变、肤色改变、塑料感皮肤、过度磨皮

### 手部专项

```
extra fingers, missing fingers, six fingers, fused fingers,
mutated hands, malformed hands, wrong finger count, unnatural finger joints
```

> 手部是最高频缺陷。若画面中手部占比大，在正向提示词里也补一句手部描述（`双手自然交叠，五指清晰可辨`），比单靠负向压制更有效。

### 文字、水印与版式

```
text, letters, words, caption, watermark, signature, logo, username,
timestamp, ui overlay, border, frame, speech bubble,
gibberish text, misspelled words, garbled characters,
bad kerning, uneven letter spacing, blurry text, cut off text
```

中文：文字、字母、水印、签名、logo、时间戳、UI 覆盖层、边框、乱码文字、错别字、字距不匀、文字被裁切

> **不需要文字的场景**务必写；**需要文字的场景**（海报、信息图）则不要写 `text`，只写 `gibberish text, misspelled words, extra words`。

### 风格污染（防止串味）

按目标风格反向选取：

| 目标风格 | 负向词 |
|----------|--------|
| 写实摄影 | `3d render, cartoon, anime, illustration, painting, sketch, cgi, plastic, airbrushed, doll-like` |
| 2D 动漫 | `photorealistic, 3d render, photography, cgi, realistic skin texture, photograph` |
| 平面设计/矢量 | `3d render, photo, photorealistic, gradient mesh, texture noise` |
| 极简/高端 | `cluttered, busy, ornate, grunge, chaotic, multiple focal points` |
| 复古/胶片 | `hdr, ultra-sharp, digital clean, modern, oversaturated` |
| 3D 渲染 | `flat illustration, 2d, line art, vector, sketch, painting` |

### 场景与道具污染

```
extra people, crowd, stranger in background, extra objects, duplicate objects,
clutter, messy background, busy background, distracting elements,
props not mentioned, seasonal mismatch, anachronistic objects
```

中文：多余人物、背景路人、道具重复、杂物堆叠、背景杂乱、未描述的道具、季节错配、时代错误物件

> 古风/历史题材额外加 `modern objects, modern clothing, plastic, zipper`。

### 编辑与修图专用（保持不变量）

```
changed composition, changed background, changed lighting direction,
changed camera angle, re-rendered texture, added elements,
removed elements, changed aspect ratio, style drift
```

> 编辑场景的负向词是对 `仅修改 X；保持 Y 不变` 的第二道保险，两者要同时使用。

## 场景预设组合

直接组合使用，再按具体需求增删。

> 预设是起点，不是终点。套用前先做冲突检查——例如需要浅景深时删掉 `blurry, out of focus`，需要胶片颗粒时删掉 `grainy, noisy`，需要文字时删掉 `text`。

### 写实人像

```
lowres, blurry, worst quality, low quality, bad anatomy, bad hands,
extra fingers, mutated hands, plastic skin, over-smoothed skin,
cartoon, anime, 3d render, cgi, watermark, text, signature, logo,
oversaturated, deformed face, asymmetric eyes
```

### 产品/电商

```
extra objects, duplicate product, cluttered background, reflections of photographer,
text, watermark, distorted shape, warped label,
inconsistent lighting, floating shadows, wrong perspective, lowres, blurry
```

> 产品包装自带的 logo 不要写进负向，否则会被抹掉；只在"无品牌纯色样机"时加 `logo`。
>
> 需要标签文字清晰可读时删掉 `text`；需要背景虚化时删掉 `blurry`。

### 海报/版式

```
gibberish text, misspelled words, extra words, cut off text, overlapping text,
bad kerning, low contrast text, cluttered layout, misaligned elements,
watermark, frame, border, lowres, blurry
```

> 注意：有文字需求时**不要**在负向里写 `text`。

### 动漫/插画

```
photorealistic, 3d render, photography, realistic skin texture, cgi,
extra fingers, bad anatomy, deformed hands, off-model character,
inconsistent outfit, watermark, blurred lineart,
messy lineart, lowres
```

> 若不要画师签名/作者标识，加 `signature, artist name`。

### 建筑/室内

```
distorted perspective, tilted vertical lines, warped geometry, impossible architecture,
floating objects, missing shadows, cluttered furniture,
text, watermark, lowres, blurry, overexposed windows
```

> 若不要人物，加 `people, crowd, human figures`。

### 食物/餐饮

```
unappetizing, plastic-looking food, artificial colors, melted mess,
dirty plate, messy table, extra utensils, text, watermark,
lowres, blurry, oversaturated, gray food
```

### 编辑/换装/修图（图生图）

```
changed face, changed identity, different hairstyle, different skin tone,
changed background, changed composition, changed lighting direction,
changed camera angle, changed secondary objects,
style drift, re-rendered texture
```

> **按编辑类型取用**：换装/换色时把 `changed secondary objects` 换成 `changed clothing color`；`precise-object-edit` / `compositing` 本身就要增删元素，此时**不要**加 `added objects, removed objects`（会拦住你要做的修改），只保留与本次编辑无关的不变量。

## 模型承载方式对照

| 模型/平台 | 负向承载 | 说明 |
|-----------|----------|------|
| Stable Diffusion 1.5 / SDXL / SD3 | 独立 `negative prompt` 输入框 | 标签式，英文短语，支持权重 `(term:1.3)` |
| Flux.1（dev/schnell） | 名义上有 negative 输入，实际近乎无效 | guidance 蒸馏模型（CFG≈1），实质约束必须写进正向；负向仅留 3–6 个画质词作弱兜底 |
| ComfyUI / WebUI / Forge | 同 SD 系 | 节点里的 `negative` 即独立通道 |
| Midjourney / Niji | `--no item1, item2` | 无独立负向框；3–6 项（经验建议），用名词词组，不用句子 |
| DALL·E 3 / GPT Image | 无独立通道 | 否定词遵守度不稳定；把"不要"改写成正向约束句，或句末补一句自然语言约束（不用 `no X` 标签式写法） |
| Gemini / Nano Banana | 无独立通道 | 用自然语言约束句，不要罗列标签 |
| 即梦 / 可灵 / Seedream / 通义万相 | 多数有独立负向输入框 | 按标签式负向处理；中文标签亦可；权重语法以平台文档为准 |

> **CFG 说明**：负向词依赖无分类器引导（CFG > 1）生效。`CFG = 1` 或 turbo/lightning 步数极少的模型上，负向词基本无效，应把约束写进正向描述（Flux 这类 guidance 蒸馏模型可留 3–6 个画质词作弱兜底）。

## 各模型写法

### Stable Diffusion / SDXL / ComfyUI

独立成段，逗号分隔，画质词放最前：

```
low quality, worst quality, lowres, blurry, bad anatomy, bad hands,
extra fingers, mutated hands, watermark, signature, text, logo,
oversaturated, jpeg artifacts
```

需要强调时加权重：`(worst quality:1.4), (bad hands:1.3), watermark`

### Flux

负向只保留画质词，其余约束移入正向：

```
low quality, blurry, jpeg artifacts, watermark, text
```

正向里补充：`画面清晰锐利，细节丰富，不含任何文字或水印`

### Midjourney / Niji

用参数追加，不写在正文里：

```
/imagine <正向提示词> --no text, watermark, extra fingers, blurry
```

正向末尾可叠加风格参数：`--ar 4:5 --stylize 250 --v 6.1`

### DALL·E 3 / GPT Image / Gemini

**转换表**——把负向意图翻译成正向约束：

| 想避免 | 不要写 | 改写为 |
|--------|--------|--------|
| 文字 | `no text` | 纯画面，画面中不含任何文字、字母或标识 |
| 水印 | `no watermark` | 干净的完整画面，无任何签名或标识痕迹 |
| 多余手指 | 不用写 | 双手自然垂放，五指清晰可辨 |
| 模糊 | `not blurry` | 焦点锐利，边缘清晰，细节可辨 |
| 卡通感 | `not cartoon` | 真实摄影质感，皮肤保留毛孔与细纹 |
| 杂乱背景 | `no clutter` | 背景干净留白，视觉焦点集中在主体 |

若仍需要强约束，可在正向提示词末尾追加一行短句，而不是长列表：

```
...完整描述...。画面中不出现文字、水印或标识。
```

### 即梦 / 可灵 / Seedream / 通义万相

多为独立负向框，按标签式负向处理，中英文标签皆可：

```
低质量, 模糊, 变形, 多余手指, 水印, 文字, 过曝
```

## 两段式完整示例

### 示例 1：写实人像（SD 系）

**正向**

```
一张 4:5 竖版人像，35 岁亚洲男性作家坐在窗边的旧木桌前写作。
午后侧逆光从左侧窗户进入，在脸部形成柔和明暗过渡，浅景深虚化背景书架。
米色亚麻衬衫有细微褶皱，胡茬清晰，皮肤可见毛孔与细纹。
真实摄影质感，50mm 镜头，f/2.0，胶片颗粒感，低饱和暖调。
```

**负向**

```
low quality, worst quality, lowres, bad anatomy, bad hands,
extra fingers, mutated hands, plastic skin, over-smoothed skin,
cartoon, anime, 3d render, cgi, watermark, text, signature,
oversaturated, deformed face
```

> **注意**：这里**故意不写** `blurry, out of focus, grainy`——正向要求的是浅景深虚化与胶片颗粒，写了就会把想要的效果一起压掉。冲突检查的实际应用。

**适配**：Midjourney 把正文里的"4:5 竖版"删掉（比例交给参数），负向改写为 `--no text, watermark, extra fingers, deformed face --ar 4:5`；DALL·E 删除负向段，把"皮肤可见毛孔与细纹"留在正向，句末补一句"画面中不出现文字或水印"。

### 示例 2：产品海报（版式含文字）

**正向**

```
商业产品海报，4:5 竖版。一瓶哑光黑色洗发水瓶居中立于白色台面，
柔和影棚光，右前方主光，瓶身左侧有细窄高光，地面轻微倒影。
背景为浅灰到白的柔和渐变。顶部大标题"清透一夏"，粗体无衬线，
底部一行小字"轻盈控油 · 500ml"。极简排版，大量留白。
```

**负向**

```
gibberish text, misspelled words, extra words, cut off text, overlapping text,
bad kerning, cluttered layout, extra objects, duplicate product, warped label,
watermark, lowres, blurry
```

**适配**：负向里**不写** `text`（画面需要文字），只写文字缺陷词。Flux 场景把负向缩到 3–6 个画质词，其余约束（"排版干净，文字居中不重叠"）移入正向。

### 示例 3：编辑/换装（图生图）

**正向**

```
图1：编辑目标。仅将人物的外套替换为图中米白色针织开衫，
保持面部身份、发型、姿势、身体比例、背景、光线方向与相机角度完全不变。
开衫保留织纹质感，与原有光线的明暗关系匹配。
```

**负向**

```
changed face, changed identity, different hairstyle, changed background,
changed composition, changed camera angle, changed lighting direction,
added objects, removed objects, re-rendered texture, style drift
```

**适配**：编辑场景负向词要与正向的"保持 Y 不变"逐条对应，形成双重锁定。

## 参考

- 正向词表与风格族系：`style-keywords.md`
- 特异性策略与增强边界：`codex-prompting.md`
- 完整模板与更多样例：`codex-samples.md`

> 部分分类与写法参考自公开提示词库的整理（如 [prompt.doingfb.com](https://prompt.doingfb.com/) 的样例结构），并结合多模型实测经验归纳。
