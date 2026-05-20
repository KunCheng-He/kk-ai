# 窗外风景

## 模板

此模板推荐使用**英文提示词**，中文版可能导致文字渲染效果下降。

```
Generate a photorealistic window view poster based on the following data:

location: [城市名],
specific_view: [景点/景观名],
Weather: [天气描述],
aspect_ratio: [比例]

- Use Image Search to search for an image of the specified place. Use keywords to search for the place.
- Keep the location and the view as close to the real reference as possible.
- If the location or view is unrealistic or fictional, create a composition blending both the location and the view into a single scene.
- Choose ONE specific image for the location and ONE specific image for the view to work with, don't use multiple images.
- Choose an appropriate window frame style for the location, keep the view consistent to the aspect ratio, rather than creating a collage.
- Reason about how current the time of day, and the weather each affect the view, and add details to the scene.
- Create an image which includes location name text, and a brief summary of the weather, using graphic design that matches the theme. Don't add any other text.
```

> **注意**：Nano Banana 2 支持 Image Search 功能，可以更准确地还原真实地点。Pro 版本只有 Google Search 工具。

## 示例

### 香港维多利亚港

> Generate a photorealistic window view poster based on the following data:
>
> location: Hong Kong,
> specific_view: Victoria Harbour,
> Weather: Sunny,
> aspect_ratio: 21:9
>
> - Use Image Search to search for an image of the specified place. Use keywords to search for the place.
> - Keep the location and the view as close to the real reference as possible.
> - Choose ONE specific image for the location and ONE specific image for the view to work with, don't use multiple images.
> - Choose an appropriate window frame style for the location, keep the view consistent to the aspect ratio, rather than creating a collage.
> - Reason about how current the time of day, and the weather each affect the view, and add details to the scene.
> - Create an image which includes location name text, and a brief summary of the weather, using graphic design that matches the theme. Don't add any other text.

只需修改 location、specific_view、Weather、aspect_ratio 四个字段即可适配不同城市。