# 写作扩展语法

> 阅读时机：需要在文章中使用 SVG 贴图装饰或学术参考文献样式时。

## SVG 贴图素材库

本工具内置丰富的 SVG 贴图素材，可用于装饰文章。贴图以代码形式嵌入，无需本地存储文件。

### 可用贴图分类

| 分类 | 贴图 | 说明 |
|------|------|------|
| **装饰** | star, heart, sparkle, flower, leaf | 星星、爱心、闪光、花朵、叶子 |
| **箭头** | arrow_right, arrow_down, arrow_curved | 右箭头、下箭头、弯曲箭头 |
| **标签** | tag, bookmark, flag | 标签、书签、旗帜 |
| **形状** | circle_ring, diamond, hexagon | 圆环、菱形、六边形 |
| **特殊** | ribbon, crown, lightning, chat_bubble, music_note, gift | 丝带、皇冠、闪电、对话气泡、音符、礼物 |

### 在 Markdown 中使用贴图

在 Markdown 中使用特殊语法插入贴图：

```markdown
# :star: 标题前加星星

正文内容 :heart: 可以在行内插入

::divider::  # 插入分隔线装饰

::tip:: 这是提示框内容

::important:: 这是重要标记
```

## 参考文献样式

学术/引用类文章可在文末添加「参考文献」章节，正文引用处用 `<sup>[1]</sup>` 角标标注，文献列表使用有序列表并在**列表后一行**写 `{: .references}` 挂弱化样式：

```markdown
正文中引用观点<sup>[1]</sup>。

## 参考文献

1. 张小明. 《公众号排版可读性研究》. 新媒体研究, 2023(5): 12-18.
2. 李华. 《移动端图文阅读体验优化实践》. 用户体验学报, 2024(2): 45-52.
{: .references}
```

`.references` 样式（13px 字号 + 辅助灰 #888）由主题 CSS 定义，视觉上弱于正文。

> [!NOTE] 实现说明
> Python-markdown 的 attr_list 会把列表后的 `{: .references}` 错误地挂到最后一个 `<li>` 上，转换器（`_hoist_list_classes`）会自动将 class 提升到 `<ol>/<ul>` 本身，写作时按上述直觉写法即可。
