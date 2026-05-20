# 创意玩法

## 模板

### 撕纸/拼贴效果

使用 YAML 结构化格式效果最好：

```
task: "edit-image: add [效果描述]"

base_image: [参考图描述]

preserve_everything:
- [需要保留的元素列表]

rules:
- Only modify the [效果区域] areas.
- Do not change [不允许改变的部分].

effects:
- effect: "[效果名称]"
  placement: "[效果位置]"
  description:
  - [效果的具体描述]

interior_style:
  mode: "[风格]"
  style_settings:
    [风格参数]
```

可选 interior_style 模式：`line-art`、`sumi-e`、`figure-render`、`colored-pencil`、`watercolor`、`pencil-drawing`

### 次元穿越

```
生成一张超现实的次元穿越场景，[角色名]从[游戏/动漫世界]中跃出进入[目标世界]，光影效果震撼，视觉冲击力极强。[原始世界]侧保持[原始风格描述]，[目标世界]侧保持[目标风格描述]，两个世界在穿越点自然融合
```

> **技巧**："从X中跃出"是核心动态指令。对比两个世界的风格差异效果更明显。

### 九宫格大头贴

```
生成[人物名]的九宫格大头贴照片，背景是在拍大头贴的房间内，一只手拿着这张九宫格照片，每个宫格都是不同的动作和表情，有[情绪1]也有[情绪2]，凸显出[性格特点]
```

> **技巧**："一只手拿着这张九宫格照片"创造递归趣味。

### 四宫格可爱照片

```
传照片人物形象还原，精准保留发型、面部细节和表情，明亮清新青春时尚人像，纵向拼贴画格式。她穿着[服装描述]，[装饰描述]，背景是[背景描述]。整体图像采用柔和影棚灯光，高清细节，清新剪贴簿美学，韩系时尚画报风格，色彩鲜艳。
```

## 示例

### 撕纸效果

> task: "edit-image: add widened torn-paper layered effect"
>
> base_image: [参考图]
> preserve_everything:
> - character identity
> - facial features and expression
> - hairstyle and anatomy
> - outfit design and colors
> - background, lighting, composition
> - overall art style
>
> rules:
> - Only modify the torn-paper interior areas.
> - Do not change pose, anatomy, proportions, clothing details, shading, or scene elements.
>
> effects:
> - effect: "torn-paper-reveal"
>   placement: "across chest height"
>   description:
>   - Add a wide, natural horizontal tear across the chest area.
>   - The torn interior uses the style defined in interior_style.
>
> interior_style:
>   mode: "line-art"
>   style_settings:
>     line-art:
>       palette: "monochrome"
>       line_quality: "clean, crisp"
>       paper: "notebook paper with subtle ruled lines"

### 次元穿越

> 生成一张超现实的次元穿越场景，孙悟空从龙珠世界中跃出进入现实世界，光影效果震撼，视觉冲击力极强。龙珠世界侧保持鲜明色彩和动感线条，现实世界侧保持写实照片风格，两个世界在穿越点自然融合