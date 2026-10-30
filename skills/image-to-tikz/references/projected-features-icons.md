# 立体特征图、网格、图标与箭头

本页适用于有可见立体张量/格网、投影切片、渐变或语义图标的参考图。先逐项读出可见面、格数、遮挡和颜色；不要把可见格数推断为通道数。特征图、格网、算子、文字和箭头保持原生 TikZ。

## 立体特征图

```json
{
  "kind":"cuboid", "face_mm":[20,12], "depth_mm":[5,4],
  "grid":[4,2,4],
  "face_styles":{"front":"blue-front","top":"blue-top","right":"blue-side"},
  "grid_style":"grid", "outline_style":"outline",
  "cell_styles":{"front":[["selected",null,null,null],["selected",null,null,null]]}
}
```

`face_mm` 是正面的宽高；`depth_mm=[dx,dy]` 是右上投影，二者均为正数；节点包围框必须是 `[w+dx,h+dy]`。`grid=[正面列数,正面行数,深度格数]`。三面共享顶点，因此改变尺寸后网格和边框仍接合。只画可见三面，不能用一张生成的立方体 PNG 代替。

`cell_styles` 可按 front/top/right 覆盖单元格；null 保留整个面的填充。front 为从上到下的行、从左到右的列；top 的行从后到前，right 的列从前到后。矩阵大小必须对应网格；不同色带高度不等时，可叠放多个有独立尺寸的 cuboid，按后到前顺序绘制并解释有意遮挡。

共享 `node_styles` 可使用 `gradient:{"from":"#D8E6F3","to":"#8BB6DF","angle_deg":90}`，由 TikZ 原生 shading 绘制，0度为左→右、90度为底→顶。渐变色、顶面亮度、侧面暗度分别设置；不要给全图每个面随机配色。

## 斜面与多边形

```json
{"kind":"grid-plane","face_mm":[30,12],
 "corners_uv":[[0.25,0],[1,0],[0.75,1],[0,1]],"grid":[4,4],
 "face_style":"plane","grid_style":"grid","outline_style":"outline"}
```

四角依次为左上、右上、右下、左下。`face_mm` 是外接矩形尺寸；格网通过四角插值产生。可选二维 `cell_styles` 与网格行列一致。用于输入/预测网格，不把纹理装饰当成计算连线。

任意原生闭合轮廓用 `kind:"polygon"`、`face_mm`、`points_uv`、`face_style` 和可选 `outline_style`。适合斜平面、黄色 chevron、空心粗双向箭头；梯形/三角投影也可以用 component_paths。可选轻阴影 `shadow:{"dx_mm":0.3,"dy_mm":0.3,"color":"#CCCCCC","opacity":0.3}` 只是装饰，视觉检查须包含阴影是否越过别的文字。

## 多类型箭头

`line_styles` 保留 `arrow:none|start|end|both`，另支持：

- `arrow_tip`: `Latex`、`Stealth`、`Triangle`、`To`、`Bar`、`Circle`；`tip_open` 控制空心头。
- `tip_length_mm`、`tip_width_mm`：头部长度/宽度；不同尺寸图须统一物理单位。
- `dash_pattern_mm:[on,off]`：自定义虚实段长；`double`、`double_distance_mm`：双线连接。
- `rounded_mm`、`shorten_start_mm`、`shorten_end_mm`：折角及端部间隙。

粗块状箭头用 polygon 而非把细线无限加粗；图中虚线若没有箭头头部，应设置 `arrow:none`。检查每条边的起点、终点、线型、颜色和方向，交叉不等于相连。

## 经用户要求生成的图标

只有独立语义 icon（天气、车辆、设备等）可作为可替换栅格资产；仅在用户要求/接受生成图标时使用。用可用的内置 image_gen 生成，明确不要生成架构图、文字或连接；透明背景请求使用 `transparent_background:true`。先保存原始生成文件与 prompt，再看图核验其语义和缩小后的清晰度。不能从原图裁一块当生成结果，也不能用生成的完整网络图冒充可编辑 TikZ。

```json
"assets": {
  "weather": {
    "path":"assets/weather.png", "kind":"generated-icon", "generator":"image_gen",
    "sha256":"<实际64位SHA256>", "prompt":"<实际生成提示词>",
    "width_px":1200,"height_px":400,"crop_px":[100,40,1100,360]
  }
}
```

节点设 `asset:"weather"`、空 `text`、无框 text 样式和独立尺寸/相对位置。所有标签另建原生文字节点。`crop_px` 是原始 PNG 上 `[left,top,right,bottom]`；渲染器用 TikZ clip 和缩放去掉透明边缘，不修改原资产。无 crop 时使用整图。文件必须放在任务内 `assets/`，打包/freeze 时一起保存；哈希或尺寸变化会让核验失效。

交付时明确：icon 是生成的近似与可替换 PNG，其内部笔画不是 TikZ；特征图及其渐变/格子、结构连线和文字为原生。具体提示词、来源和文件位置随任务保存。

## 字形与局部核验

`fonts.<role>.face` 可显式选择已安装字体（如 `Times New Roman`），与统一字号、粗细和行距配合；缺字体应报告编译问题，不能静默改成不同字体再称精确复刻。数学公式仍由 LaTeX 排版，需另核对上下标和字体观感。

先看整图比例，再放大特征图接缝/格网、橙色选中列、空心箭头、细虚线和上/下标。自动编译通过不能证明这些细节忠实。用户只指定页面中的某一 Figure 时先裁图体，记录原图 SHA256 与 crop_xyxy，OCR 和复刻均只作用于该范围。
