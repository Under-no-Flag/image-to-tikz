# 神经网络图：参数化组件与图片盲测

先从图片清点阶段、可见面片数、遮挡顺序、标签与连接。不根据架构名称推断层数；visible_count 是图上的可见张数，tensor_channels 是文字标注的通道数，两者不能混用。不要把面片大小直接设为通道数或分辨率；图示可能使用非线性缩放。

## 图形组件

普通 scene 节点可增加 glyph 字段。组件节点用空 text、无框的 text 样式；尺寸必须等于 glyphs.dimensions(glyph)，验证器检查一致性。标签另设节点，相对所属组件定位。

```json
{"kind":"feature-stack", "face_mm":[24,24], "visible_count":6,
 "step_mm":[2.4,2.4], "light_style":"tensor-light", "dark_style":"tensor-dark"}
```

feature-stack 的面片在局部 x 向右、y 向下的坐标系按序覆盖，交替引用两种填充样式。包围框是 face + (count-1)*step。一个组件生成一个 FeatureStack 宏调用，内部 foreach 展开；统一修改宏或 palette 可调整整组外观。

```json
{"kind":"slab", "face_mm":[7,28], "shear_mm":28,
 "light_style":"tensor-light", "dark_style":"tensor-dark"}
```

slab 生成倾斜四边形，包围框宽度为 face_width + shear。这两类组件服务于特征图堆叠与倾斜全连接层。三面网格长方体 cuboid、斜格网 grid-plane 和 polygon 的定义见 [projected-features-icons.md](projected-features-icons.md)；不能宣称已覆盖任意投影或所有架构图。

## 组件局部连线

component_paths 元素包含 style、points、可选 closed。每个 point 为 `{"of":"组件ID","uv":[0.5,0.8]}`，按该组件包围框左上角为原点归一化。uv 可以超出 0–1，支持引线和外部标签。

感受野矩形是一条 closed path，映射细线另设 path；连接绑定组件，修改 scene 的位置或尺寸后重建即可跟随。不同线角色通过共享 line_styles 控制。未带箭头的原图连接不能擅自添加箭头。

可见面片与尺寸文字应分开：同级字号统一，面片宽高/偏移保留来源比例。OCR 框高估计不是字体 em 大小，尤其不能以聚合整图框来计算字号。

分组前必须检查是否存在多个字体层级：阶段标签即使语义相近，也可能按视觉层级分为主要标签与紧凑标签。至少抽查两处主标签、两处小标签及操作说明；不得把“统一字号”实现为全图同一字号。连线按角色分别设样式，感受野细线、层间主连接和文字引线不应默认共用同一个线宽。

## OCR 缓存与局部识别

normalize 支持 doc_title、figure_title，保留覆盖整图的合并文字，但以 aggregate 和 unreliable-aggregate 标记不可靠字号。对这类结果按原图拆分并核对文字，不把一大块 OCR 框当成一个组件。

需要局部校准时，写 regions.json：

```json
[{"id":"label-a", "box_xyxy":[100,20,350,100]}]
```

运行 `python scripts/ocr_regions.py RUN regions.json`。坐标对应 source.png，脚本缓存每块原始响应，重用同一 crop 时不发新请求；更改 crop 必须另取 id。结果映射回原图，追加到 ocr.json。无文字的区域如实记录 0 blocks，不替换成伪识别结果。手工纠错/补漏保留原 OCR id，并写入 scene.evidence。

## 盲测与后验对照

1. 重建阶段只读 PNG、OCR 和本 skill，不读目标的原始 TeX、PDF 文字层或生成脚本。
2. 先对照图片完成结构/视觉核验，运行 check --final。
3. 运行 `python scripts/freeze_run.py RUN`，复制当前产物并生成哈希与时间戳。
4. 快照完成后才打开原始 TikZ，记录可见层数、面片比例、局部偏移、字号和路径的差别。原文档有独立缩放时比较统一尺度下的比例，不直接比较裸 TeX 数字。
5. 源码中的隐藏结构或笔误要与可见图区分。后验结论写单独报告；如果需利用源码修正，创建独立的 source-assisted 版本。

轴对齐包围框会在斜向堆叠之间出现空白区域重叠。只对图片确认无实际遮挡的节点对写 allowed_overlaps 和具体理由；不要一键忽略所有重叠。最终查看真实面片与连线，不能只检查包围框。

## 复杂面板、注意力叠层与图网络

- 先分主路径、残差/反馈、局部放大、示意小图四类。先确定面板和共享样式，再复用局部组件；不要把分区 OCR 的整段外框当成一个节点。
- 透视重叠层按后到前建立节点，共享尺寸和位移。`opacity` 控制整体透明度，`fill_opacity` 可单独覆盖；显式 `allowed_overlaps` 解释有意遮挡。渲染器按节点顺序绘制其图元，避免后画底层遮住前层。
- 已测量的背景面板用 `role: "group"`，仅免除完全包含的子节点重叠告警；部分跨出仍告警。需随成员大小自动伸缩时使用 `containers.members`。标题切口与旋转文字外接框需逐项视觉核对，不能整体关闭检查。
- 曲线：`component_paths` 使用 `kind: "cubic"`，恰有起点、控制点 1、控制点 2、终点四个 `of/uv` 局部坐标。残差和反馈保留正交折线；放大曲线不应冒充计算边。
- 小图网络/散点用 `glyph.kind: "motif"`、`face_mm: [w,h]`，每个 `vertices` 元素包含 `uv: [u,v]`、`radius_mm`、`shape: circle|square|triangle`、填充颜色来自 `style`；`edges` 的 `ends: [i,j]` 引用顶点下标、`style` 引用线样式。所有标记和边为原生 TikZ。示意小图的低清细节无法精确读出时，在 evidence/报告中写明，不以可编译代替真实性。
- **局部坐标基于外接矩形**：使用 `(node.west |- node.north)`，不要用椭圆/菱形的 `north west`（它是轮廓上的斜向锚点）。连接到轮廓时才直接用语义锚点。
- `scene_builder.Canvas` 可把人工测得的像素框转换成毫米及相对位置，复用同尺寸 token；它不执行图像识别。子图关联面板、连线关联组件，移动面板后应带动子图，不能依赖独立绝对坐标。

字体支持 `family: serif|sans|mono` 和 `leading`（默认 1.2）；节点支持 `text_rotate_deg`，统一旋转类别的字号。混合数学和标签时检查字体宽度与上/下标，不要从 OCR 的整段包围框估字号。
