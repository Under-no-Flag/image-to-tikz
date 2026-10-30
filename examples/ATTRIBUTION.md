# 案例来源与许可范围

根目录 MIT 用于原创 skill、通用工具及说明，不覆盖第三方图式、论文内容或字体。这里只发布用户要求展示的输入图/高清转换图，不发布整页论文、原始 OCR 响应或完整任务结果。图体输入来自已授权展示的指定测试图片。

## LeNet 与 Transformer

- 参考项目：[maximxue/Deep-Learning-TikZ](https://github.com/maximxue/Deep-Learning-TikZ)。
- 参考提交：`5d9cc04970c164d3c8966e70e181cf9369bad803`。
- 对应原文件：`tikz/chapter5 - LeNet.tex`、`tikz/chapter8 - Transformer Architecture Extended.tex`。
- `lenet/` 与 `transformer/` 的输入图源自上游 PDF；输出图为图片复刻后经过源码对照修正的版本，保留 **AGPL-3.0**。
- 许可证在 `licenses/AGPL-3.0.txt`；为保留对应源码可得性，仅将两个输出图的自包含 TeX 放在 `licenses/*-corresponding-source.tex`，不是完整案例产物或安装包运行依赖。
- 原始参考 TeX 可在上述固定提交的上游仓库获取。重建更改包括参数化布局、统一样式、可见堆叠/线条与字号。
- 保留上游作者权利；不把这些图列入根目录 MIT。

## 其他图式

| 目录 | 用户提供的参考 | 复刻范围 |
|---|---|---|
| `st-ssl/` | ST-SSL 架构截图 `download.png` | 三面板图式；小图边与字体有近似 |
| `projected-features/` | 标有 Figure 3 的网络图截图；未提供完整文献信息 | 网络/投影/特征图；天气图标重新生成 |
| `gman-figure4/` | `GMAN-p04-diagram.png` | 仅 Figure 4 图体，裁切范围记录在 metadata |
| `rail-roadmap/` | 孔佳鑫《基于深度学习的城市轨道交通车站客流状态识别与仿真研究》，用户提供第14页 | 仅图1-2图体，不含正文/页眉/水印 |
| `scenic-roadmap/` | 用户提供的景区研究路线截图，图4；未提供完整文献信息 | 三列图体与图注 |
| `lorenz-math/` | 用户提供的 Lorenz / 稀疏回归数学图；未提供完整文献信息 | 整图；输出轨迹与波形仅示意近似，严格忠实复刻未通过 |
| `threshold-math/` | 用户提供的两面板阈值与切换曲线图；未提供完整文献信息 | 两面板图体；定性几何复刻通过，不代表原函数恢复 |

这些图式/文字的权利归原作者；本仓库不声称拥有原始论文图片版权，也不额外授予其再利用许可。未核实的文献身份保持未提供，不根据缩写猜测出处。立体网络图中的天气图标是实际 GPT image_gen 生成的替代资产；其提示词和哈希保留在本地完整结果中。

所有发布图均不是“原作者认可”的版本。字体未随包分发。不同系统字体替换后需重新检查布局。
