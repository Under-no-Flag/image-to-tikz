# Scene IR v1

`assets/scene-template.json` 是无内容的样式起点。先填写源图；`nodes=[]` 会报错，避免交付模板内容。

坐标和尺寸为 **mm**，x 向右、y 向下；字号和线宽为 TeX **pt**（72.27pt/in）。标识符以小写字母开头，仅含小写字母、数字和连字符。

| 字段 | 含义 |
|---|---|
| `fonts` | 层级的 size_pt、weight（normal/bold）、color、family（serif/sans/mono）、leading、可选拉丁 face、中文 cjk_face/cjk_bold_face |
| `line_styles` | width_pt、color、dash（solid/dashed/dotted）、arrow（none/start/end/both） |
| `node_styles` | shape、line、font、fill、padding_mm、corner_mm、opacity、fill_opacity |
| `sizes` | 命名 `[width_mm,height_mm]`，最小外框尺寸，溢出需修复 |
| `layout_tokens_mm` | 命名中心间距或偏移量，可正可负 |
| `nodes` | 组件或独立文字 |
| `containers` | 根据成员实际范围生成 fit 边框 |
| `edges` | 命名组件间关系 |
| `alignments` | 声明的对齐约束 |
| `ocr_exclusions` | 未用作可编辑文字的 OCR 误检与原因 |
| `allowed_overlaps` | 有意重叠的两节点与理由 |
| `assets` | 用户授权的独立 generated-icon 资产与来源/哈希，见 projected-features-icons.md |
| `unresolved` | 未确认文字/关系/元素，非空阻止验收 |

颜色使用 `#RRGGBB`。shape 为 rectangle、rounded、ellipse、diamond、text。text 为无框独立文字。椭圆和菱形留给正文的宽度默认按外框宽度的 0.65/0.4 计算，再减内边距，避免文字撑大形状。可在 node_styles 设置 text_width_ratio（0 到 1 之间）校准，并检查实际边界。

## 节点

```json
[
  {"id":"input", "style":"process", "size":"standard", "text":"数据采集", "at_mm":[0,0], "ocr_ids":["ocr-001"]},
  {"id":"clean", "style":"process", "size":"standard", "text":"数据清洗\n缺失处理", "relative":{"of":"input","dx":0,"dy":"row-pitch"}, "ocr_ids":["ocr-002","ocr-003"]},
  {"id":"model", "style":"process", "size":"standard", "latex":"$\\hat{y}=f_\\theta(x)$", "latex_reviewed":true, "relative":{"of":"clean","dx":"column-pitch","dy":0}, "ocr_ids":["ocr-004"]}
]
```

每节点设 text/latex 之一、at_mm/relative 之一。relative.of 为其他节点**中心**；允许前向引用，禁止循环。普通文字自动转义 `% & _ # $ { } \`，不要提前转义。latex 为核对过的公式，保留数学定界符；不执行未检查的 OCR LaTeX。

普通 text 可附 `text_runs`（片段 text、可选 weight）；拼接必须与 text 完全相同，缺省 weight 继承字体，不能同时设置 latex。

ocr_ids 对应 OCR 块，可多对一或一对多。补漏文字可无 id，但在视觉验收说明。修正错字仍引用原 id。默认外框是最小尺寸，文字引起的增长会报告，不静默缩字。

## 边与分组

```json
{
  "edges":[
    {"id":"collect-clean", "from":"input.south", "to":"clean.north", "style":"normal", "route":"straight"},
    {"id":"clean-model", "from":"clean.east", "to":"model.west", "style":"normal", "route":"hv", "label":"训练", "label_font":"body", "ocr_ids":["ocr-005"]},
    {"id":"loop", "from":"model.south", "to":"input.east", "style":"feedback", "route":"polyline", "via":[{"of":"model.east","dx":10,"dy":20},{"of":"input.east","dx":62,"dy":0}]}
  ],
  "containers":[{"id":"prepare-stage", "members":["input","clean"], "style":"section", "padding_mm":4, "title":"预处理", "ocr_ids":["ocr-006"]}],
  "alignments":[{"axis":"x","nodes":["input","clean"]},{"axis":"y","nodes":["clean","model"]}],
  "ocr_exclusions":[{"id":"ocr-007","reason":"箭头端点被误识别为字符"}],
  "allowed_overlaps":[], "unresolved":[]
}
```

端点支持 center、north、south、east、west、north east、north west、south east、south west。hv 先水平再垂直（`-|`），vh 先垂直再水平（`|-`）。via 为相对节点锚点的偏移。绕线不会自动避障，必须查看预览。

容器按扁平节点成员生成，可用成员集合表达外层组，不支持引用另一容器为成员。三次曲线、局部图网络及散点图元见 [network-glyphs.md](network-glyphs.md)；更复杂自由形状超出生成器能力时，记录缺口；保留本工作流和共享样式扩展生成器，不用栅格整图替代。

## 验收与编辑

review-template 记录源图、OCR、scene、TeX、预览的哈希。填写每项 `{ "passed": true, "evidence": "实际观察与对应节点/边" }` 并存为 review.json。这是 agent 的视觉检查记录；自动校验不能证明记录本身真实，必须先看图。

通常改 scene.json 后 build。可以直接改交付的 .tex，但再次 build 会由 scene 重新生成，旧视觉验收会失效。论文中加载 tikz 与 preview.tex 所列 libraries，先 `\input{styles.tex}`，在 figure 内 `\input{figure.tex}`；中文用 XeLaTeX 和可用 CJK 字体。路径相对编译工作目录。
