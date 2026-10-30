---
name: image-to-tikz
description: 将技术路线图、流程图、框架图等图片重建为可编辑的 LaTeX/TikZ，使用 PaddleOCR-VL 校对文字，统一线框、线条、同级字号、组件对齐和相对布局，并编译渲染核验。适用于有参考图片的结构图复刻与后续编辑。
---

# 图片转可编辑 TikZ

输出可单独修改文字、框、箭头、分组和布局的原生 TikZ。这是 **agent 视觉理解 + PaddleOCR + 确定性生成器**：脚本不自动推断完整图结构。不能把 OCR 框直接当组件，也不能把整图嵌入 `.tex` 冒充可编辑结果。

## 开始

脚本路径相对本 `SKILL.md` 的目录解析。用现有 Python 环境或独立环境安装 `requirements.txt`；不依赖开发仓库的绝对路径。运行 `python scripts/workflow.py doctor` 检查依赖和 Token 状态。配置、安装和测试约定见 [references/operations.md](references/operations.md)。

每次建立独立任务目录，保留原图。用户只指定某个 Figure 时，仅裁其图体并记录原图哈希与裁切坐标，不混入页面其他内容。用户明确要求隔离测试时，每个新上下文只分配目标图、skill 和任务要求，共用渲染器由协调者维护，避免并发覆盖。开发阶段只处理用户明确指定的图片，逐张完成，不遍历测试文件夹。收到多张明确指定的图时按顺序全部处理；仅提供文件夹且未指定时，先选一张有代表性的图。无需为了改 skill 跑完整图片集。

```bash
python scripts/workflow.py prepare /absolute/path/image.png --out /absolute/path/output/case-001 --width-mm 170
python scripts/workflow.py ocr /absolute/path/output/case-001
```

## 重建

先按 [references/reconstruction-playbook.md](references/reconstruction-playbook.md) 建立本图的组件、文字、连接和样式清单；这是跨图流程，不从测试图复制固定坐标与标签。

神经网络架构图先阅读 [references/network-glyphs.md](references/network-glyphs.md)。包含立体网格、渐变、投影面、多类箭头或生成图标时，再读 [references/projected-features-icons.md](references/projected-features-icons.md)。用参数化堆叠、倾斜层和组件局部连接保留可见几何；同角色共享风格，但张量尺寸比例不能强制统一。原始 TikZ 是盲测对照资料：图片重建、视觉核验与结果快照完成之前不得打开。对照后的修正必须另存版本，不能回填盲测结果。

1. 若 OCR 成功但无文字或遗漏大片标签，按 [operations.md 的分区补识别流程](references/operations.md#ocr-把架构图当成插图时) 关闭版面分析并按面板补识别。聚合 `ocr` 块不能当作字符高度；记录人工补录项。查看 `source.png`，再查看 `ocr-overlay.png` 和 `ocr.json`。核对文字、公式、框边界、箭头方向、分支、汇合、反馈回路、分组。纠正 OCR 错字并补漏；无法辨认的内容进入 `unresolved`，不要猜。
2. 在 `scene.json` 记录语义结构，按 [references/scene-format.md](references/scene-format.md) 使用命名节点、文字来源、边、容器和对齐约束。OCR 只提供文字证据；拓扑必须从原图读出。**不按常见架构补画连线**：逐条检查是否有可见线段、箭头和端点；相邻模块间空隙也要放大查看，无连线即保留空隙。
3. 用户关注首次转换效率、线宽或字重时，先读 [references/first-pass-style-calibration.md](references/first-pass-style-calibration.md)，测量线条并区分中文/拉丁字体与局部加粗，首次成功渲染留存快照。按 [references/style-layout.md](references/style-layout.md) 合并同类样式和组件尺寸。保留原图中有意义的虚实线、层级和颜色；统一截图噪声造成的细小差异。字号根据输出物理宽度与 OCR 框估计，再按语义层级校准。
4. 大部分组件通过 `relative.of` 和共享 `layout_tokens_mm` 定位。用同一尺寸组保证同宽同高，用 `alignments` 声明对齐。分组用 `containers.members` 的 `fit`，连线连接节点锚点，转折点相对节点定位。

不要逐个缩小文字来掩盖拥挤；先调整换行、共享组件尺寸或组间距。普通文字用 `text`（自动转义）；数学公式用核对过的 `latex` 并设 `latex_reviewed=true`。保留可编辑数学源码，避免截图公式。复杂插图不能可靠恢复时记录具体边界。用户要求生成语义 icon 时可用 image_gen 生成独立、可替换 PNG 并保存提示词/哈希；明确其笔画不可作为 TikZ 编辑。其余结构保持原生，不能悄悄省略或用生成整图替代。

## 编译与核验

```bash
python scripts/workflow.py build /absolute/path/output/case-001
python scripts/workflow.py check /absolute/path/output/case-001
python scripts/workflow.py review-template /absolute/path/output/case-001
```

`build` 生成集中样式 `styles.tex`、图主体 `figure.tex` 和完整 XeLaTeX 文档 `preview.tex`，编译 `preview.pdf`，默认以 300 DPI 渲染 `preview.png`（`build --dpi` 可调），输出左原图/右重建图的 `comparison.png`。检查实际组件尺寸是否被文字撑大、TeX 字体/溢出警告、声明的对齐和 OCR 条目覆盖。

实际查看原图和渲染图，核对文字/公式、拓扑/方向、分组、对齐/间距、字体/线条、裁切/重叠六项。在 `review-template.json` 基础上写 `review.json`，每项记录真实核对证据；未检查项保持 `passed=false`。不能仅因编译成功批量打勾。签名会让后续修改后的旧验收失效。

```bash
python scripts/workflow.py check /absolute/path/output/case-001 --final
```

视觉核验必须包括小间隙/箭头的局部放大，不能只看缩略对照图。若源码后验检查推翻盲测验收，在原任务新增 `post-freeze-audit.json`（`fidelity_passed: false` 与原因），保留快照、另建修订版；自动校验通过不等于图像忠实度通过。修复实际问题后重新 `build` 并复查。已通过的结果即交付，不为微小抗锯齿差异无限迭代；两轮局部修复后仍存在的实质问题应明确报告。缺少 Token、编译器或图像不清晰时保留当前可编辑产物，准确说明哪一步未完成。

交付图主体、共享样式、完整文档、PDF、预览及 `scene.json`；简短报告 OCR、编译、结构检查、视觉核验各自状态与未解决项。称“验收通过”必须满足 `check --final`。合成样例或缓存格式测试不能证明真实图片 OCR/复刻效果。

交付高清图时从 PDF 直接导出，默认 600 DPI；不要放大旧 PNG。命令不修改原任务与验收签名：

```bash
python scripts/workflow.py export /absolute/path/output/case-001 --out /absolute/path/exports/case-001 --dpi 600
```

PDF 中的原生图元可无损缩放；已生成的 PNG icon 仍受其原始像素限制。
