# 提示词方法论

提供提示词结构、特异性和迭代的最佳实践。

## 目录
- [Structure](#structure)
- [Specificity policy](#specificity-policy)
- [Allowed and disallowed augmentation](#allowed-and-disallowed-augmentation)
- [Composition and layout](#composition-and-layout)
- [Constraints and invariants](#constraints-and-invariants)
- [Text in images](#text-in-images)
- [Input images and references](#input-images-and-references)
- [Iterate deliberately](#iterate-deliberately)
- [Use-case tips](#use-case-tips)

## Structure

- 使用一致的顺序：场景/背景 → 主体 → 关键细节 → 约束条件 → 输出意图。
- 包含用途说明（广告、UI 模型、信息图）以确定精致度。
- 复杂请求使用短标签行，而不是长段落。

## Specificity policy

这是核心原则：**根据用户提示词的特异性决定增强程度。**

- 如果用户提示词已经很详细具体，只需规范化/结构化，不要添加创意需求。
- 如果提示词比较泛化，可以添加有品位的细节，但只在实质性改善输出质量时才添加。
- `codex-samples.md` 中的示例是完整的提示词食谱，不是每次请求都应该添加的默认增强量。
- 对于照片写实需求，直接包含"photorealistic"，并加上具体的真实质感细节（如毛孔、皱纹、织物磨损、材质纹理等）。

## Allowed and disallowed augmentation

泛化提示词时允许的增强：
- 构图和取景提示
- 用途或精致度提示
- 实用的布局引导
- 支持请求的合理场景具体化

禁止添加：
- 未隐含的额外角色、道具或物体
- 未隐含的品牌配色、标语或叙事节奏
- 随意的方位摆放（除非上下文支持）

## Composition and layout

- 仅在实质性有帮助时指定取景和视角（特写、广角、俯视）及位置。
- 如果素材明显需要给 UI 或文案留空间，指出负空间。
- 除非用户或上下文支持，否则不做左右布局决策。
- 对于人物，描述身体取景、比例、眼神和物体互动（`全身可见`、`低头看书`、`双手自然握把`）。

## Constraints and invariants

- 明确说明什么不能改变（`保持背景不变`）。
- 对于编辑类请求，使用 `仅修改 X；保持 Y 不变` 并在每次迭代中重复。

## Text in images

- 将文字用引号或大写标出，并指定排版（字体风格、大小、颜色、位置）。
- 对于准确性要求高的生僻词，逐字母拼写。
- 要求逐字渲染，不添加额外字符。
- 对于小文字、密集信息图、数据密集型幻灯片，建议提高生成质量。

## Input images and references

- 不要假设每张提供的图片都是编辑目标。
- 按索引和角色标注每张图片（`图1：编辑目标`、`图2：风格参考`）。
- 如果用户提供图片用于风格、构图或氛围引导且未要求修改，视为带参考的生成。
- 如果用户要求保留现有图片但修改特定部分，视为编辑。
- 对于合成，描述图片如何交互（`将图2中的主体放入图1`）。

## Iterate deliberately

- 从干净的基础提示词开始，然后做小的单步修改。
- 迭代时重新说明关键约束条件。
- 优先一次做一个有针对性的跟进，而不是重写整个提示词。

## Use-case tips

### Generate（生成）

| Use Case | 提示策略 |
|----------|----------|
| photorealistic-natural | 用摄影语言（镜头、光线、取景）编写，要求真实质感，避免过度风格化 |
| product-mockup | 描述产品和材质，确保清晰轮廓和标签可读性 |
| ui-mockup | 先说明目标精细度（产品级或低保真线框图），聚焦布局和层级 |
| infographic-diagram | 定义受众和布局流向，明确标注各部分，要求逐字渲染 |
| logo-brand | 保持简洁可缩放，要求强剪影和平衡负空间，避免多余装饰 |
| ads-marketing | 像写创意简报：品牌定位、受众、氛围、场景、精确标语 |
| productivity-visual | 明确产物类型（幻灯片、图表、流程图），定义画布和层级，提供真实数据 |
| scientific-educational | 定义受众、教学目标、必要标注、科学约束、箭头和可读空白 |
| illustration-story | 定义分镜或场景节拍，保持每个动作具体 |
| stylized-concept | 指定风格线索、材质质感和渲染方式（3D、油画、粘土），不创造新故事元素 |
| historical-scene | 说明地点/日期和时代准确性要求，约束服装、道具和环境 |

### Edit（编辑）

| Use Case | 提示策略 |
|----------|----------|
| text-localization | 仅修改文字；保留布局、排版、间距和层级；无额外文字 |
| identity-preserve | 锁定身份（面部、身体、姿势、发型、表情）；仅修改指定元素 |
| precise-object-edit | 精确指定移除/替换内容；保留周围质感和光照 |
| lighting-weather | 仅修改环境条件（光照、阴影、氛围、降水）；保持几何和主体身份 |
| background-extraction | 请求在纯色平面背景上的清晰抠图；清晰轮廓；充足的留白；无阴影无光晕 |
| style-transfer | 指定要保留的风格线索（调色板、质感、笔触）和要修改的内容 |
| compositing | 按索引引用素材；指定移动内容和位置；匹配光照、透视和比例 |
| sketch-to-render | 保留布局、比例和透视；选择支持草图的材质和光照 |

## 参考

完整的提示词模板和示例见 `codex-samples.md`。本文档聚焦于原则、特异性和迭代模式。
