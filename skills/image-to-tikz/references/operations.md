# 安装、OCR 与单图验证

Python 3.10+；依赖见 skill 根目录 requirements.txt。渲染需要 PATH 中可调用的 xelatex、pdftoppm、pdfinfo；TeX 包需 fontspec、xeCJK、tikz、geometry。不依赖 standalone.cls。

```bash
uv venv /absolute/path/environment --python 3.11
uv pip install --python /absolute/path/environment/bin/python -r /absolute/path/skill/requirements.txt
/absolute/path/environment/bin/python /absolute/path/skill/scripts/workflow.py doctor
```

无 uv 可用 python3 -m venv + pip。CJK 字体依次尝试 PingFang SC、Noto Sans CJK SC、Heiti SC、FandolHei-Regular；缺字应修字体重编译。

## PaddleOCR-VL

使用参考 skill 的百度 AI Studio PaddleOCR-VL 异步 jobs 接口，默认模型 PaddleOCR-VL-1.6，可用 `ocr --model` 指定服务支持的其他模型。提交图片、轮询任务、读取文字框，不调用生图。

Token 读取顺序：环境变量 PADDLE_OCR_TOKEN → ~/.image-to-tikz/config.yaml → 参考 skill 的 ~/.editppt/config.yaml。配置只取 PADDLE_OCR_TOKEN。不要在项目、任务目录、skill 或命令参数保存 Token，不打印配置。用户级配置由用户本地填写，目录私有、文件权限 600：

```yaml
PADDLE_OCR_TOKEN: "填写自己的 Token"
```

[AI Studio Token 页面](https://aistudio.baidu.com/account/accessToken)。不承诺免费额度或服务可用性。缺 Token 时说明配置位置；可以继续结构分析与源码生成，但不声称 OCR 已运行，验收保持未通过。服务拒绝请求时报告状态，不静默换 OCR 或目测。

原始结果存 ocr-raw.json，归一化结果存 ocr.json，覆盖图存 ocr-overlay.png。已有 OCR 不重复上传。可用 `ocr RUN --raw /absolute/path/cached.json` 离线导入真实缓存结果：单页 prunedResult 或 `{ "page": prunedResult }`。先确认缓存对应同图和坐标空间；记录 imported provenance，不宣称本次网络识别。

总等待默认 300 秒，状态输出供 agent 跟进，工具以短轮询执行并保持沟通。超时后不自动重提限额任务，先检查任务状态。日志省略远程响应体和签名 URL，避免泄漏凭据。

接口参考：[paddle_text_hints.py](https://github.com/ningzimu/image-to-editable-ppt-skill/blob/b7be494e31a0ed56ef98716891db5474606b8cdf/skills/image-to-editable-ppt/cli/editppt/runtime/paddle_text_hints.py)。接口和模型名称需要配置后的在线验证，格式测试不代表服务已验证。

## 开发验证

仓库 test-images/ 存用户图片，outputs/任务名/ 存单次产物；安装后支持任意绝对路径。查看测试目录后选一张图：prepare → OCR → agent 读图填 scene → build → inspect → review → check --final。每轮只修实际问题，不覆盖旧任务，无需跑完整图片集。

合成场景用于验证转义、相对坐标、共享样式、编译与尺寸检查；模拟 OCR 数据测试解析、缩放和字号聚类。两者不代表真实图片识别/复刻验收。开发仓库测试：`python -m unittest discover -s tests -v`。

## OCR 把架构图当成插图时

返回成功但 0 个文字块不是识别成功。先检查 `ocr-raw.json` 的 `block_label`，记录该尝试。对新任务可指定：

```bash
python scripts/workflow.py ocr /absolute/run --no-layout-detection
```

对于已经 OCR 的任务，保留原始结果，按面板/文字区补识别，建立 `regions.json`：

```json
[{"id":"encoder-no-layout","box_xyxy":[100,100,600,700],"layout_detection":false}]
```

```bash
python scripts/ocr_regions.py /absolute/run /absolute/run/regions.json
```

多次补识别会保留已有区域并与新区域按 id 合并，避免后一次操作丢弃先前文字映射；冻结任务禁止再修改 OCR。每个区域的原图裁切与服务返回缓存保存在 `ocr-regions/<id>/`。同名缓存不能改变图像或识别模式；应换区域 id。坐标基于 `source.png`，脚本自动映回整图。关闭版面分析时服务返回 `block_label=ocr` 的整段文字，保留但标记 `unreliable-aggregate`，**不参与字号聚类**。整图/大裁切仍可能漏字，按语义面板裁切比一再整图重试有效；局部重复标签、箭头误认、上/下标和帽子/波浪线必须目视校对。

`ocr_coverage` 只是返回块的映射完整度，不是图中全部文字识别率。对聚合块，在对应面板节点记录 `ocr_ids`，在 `evidence.ocr_reconciliation` 明确漏识、误识、人工补录。无证据不要声称 OCR 100%。冻结结果时一并保存裁切图、原始 OCR、模式和哈希。

## TeX 环境与字体

macOS 可安装 [MacTeX（无 GUI）](https://formulae.brew.sh/cask/mactex-no-gui) 和 [Poppler](https://formulae.brew.sh/formula/poppler)：

```bash
brew install --cask mactex-no-gui
brew install poppler
```

安装后重开终端，必要时将 `/Library/TeX/texbin` 加入 PATH。已有 MacTeX/TeX Live 不必重复安装。Ubuntu/Debian 常用包：

```bash
sudo apt-get update
sudo apt-get install texlive-xetex texlive-lang-chinese texlive-latex-extra poppler-utils fonts-noto-cjk
```

Windows 可在 WSL2 Ubuntu 中按上面步骤运行；原生 Windows 未验证。完整 [TeX Live](https://tug.org/texlive/) 也可用。检查：

```bash
xelatex --version
pdftoppm -v
pdfinfo -v
kpsewhich xeCJK.sty
kpsewhich tikz.sty
```

字体不会随 skill 分发。默认有跨平台中文字体回退；精确复刻应在 `scene.json` 的 `fonts` 显式指定已安装字体。示例中的 `Songti SC`/`Times New Roman` 是原测试机字体，Linux 需安装合法可用字体，或在**另存的场景**中改成 `Noto Serif CJK SC`，并移除拉丁 `face` 使用 TeX 默认字体 并重新检查字宽、换行与粗体。TeX Live 自带 `FandolSong-Regular.otf` 与 `FandolSong-Bold.otf` 也可显式用于 `cjk_face`/`cjk_bold_face`。换字体后的布局不保证与原展示图完全相同。

## API 配置教程

先在 [PaddleOCR 控制台](https://aistudio.baidu.com/paddleocr) 确认账号可用的 API，再从 [Access Token 页面](https://aistudio.baidu.com/account/accessToken) 获取 Token。此适配器使用 AI Studio **异步 jobs** 服务，不是百度智能云通用 OCR 的 API Key/Secret Key，也不是本地 PaddleOCR 推理；不需要安装 paddlepaddle 或 GPU。

推荐使用用户级文件：

```bash
mkdir -p ~/.image-to-tikz
chmod 700 ~/.image-to-tikz
# 用编辑器新建 ~/.image-to-tikz/config.yaml，填入前文 YAML
chmod 600 ~/.image-to-tikz/config.yaml
python /absolute/path/image-to-tikz/scripts/workflow.py doctor
```

`doctor` 仅显示是否有配置，不验证 Token 有效性。也可在安全的会话环境中设置 `PADDLE_OCR_TOKEN`；不要把真实值写进仓库或共享命令。首次 `ocr` 是真实在线验证。401/403 检查账号、权限和 Token；429 检查服务配额；网络超时先查任务，避免重复提交。

默认地址为 `https://paddleocr.aistudio-app.com/api/v2/ocr/jobs`，模型为 `PaddleOCR-VL-1.6`。客户端以 multipart 的 `file`、`model`、`optionalPayload` 提交，使用 bearer Token；根据 `jobId` 查询状态，下载单页结果后归一化。服务模型若变动，用 `ocr --model 服务支持的名称`，不要改成其他 OCR 后仍宣称 PaddleOCR。原始结果和截图可能含用户内容，保存在本次任务目录，不自动上传到 GitHub。

## GPT image_gen：仅用于需要的独立图标

需要一个能看图、执行 Python/TeX，并提供 **GPT image_gen 工具**的 agent 环境。Skill 不捆绑生图模型，也不调用第三方生图 API。普通图的文字、框、特征图、渐变、网格与箭头不需要生图服务；用户要求生成语义 icon 时才调用宿主实际提供的 image_gen。

流程：查看参考局部 → 描述独立图标的线条/颜色/构成 → 生成透明背景 PNG → 将返回资产保存到任务 `assets/` → 在 `scene.assets` 写入实际 prompt、尺寸、SHA-256 和相对路径 → 通过原生 TikZ 放置。详见 [projected-features-icons.md](projected-features-icons.md)。PaddleOCR Token 不用于 GPT 生图；这个 skill 没有 `GPT_IMAGE_TOKEN` 配置项。宿主未提供该工具时，报告 icon 步骤不可用，不伪造生成记录，也不以生成整图代替 TikZ。

已有示例的生成图标可离线重编译，无需再次调用 image_gen。PNG 图标自身的笔画不是可编辑矢量，必须在交付中声明。

## 高清导出

工作预览默认 300 DPI；`build RUN --dpi 600` 可直接构建更高分辨率。验收后建议另目录导出：

```bash
python scripts/workflow.py export /absolute/path/run --out /absolute/path/export-600 --dpi 600
```

允许 72–1200 DPI；600 通常足够，1200 会显著增加内存和文件大小。导出直接重渲染矢量 PDF，记录 PDF/PNG 哈希、像素尺寸和 DPI，不覆盖已冻结证据。PDF 是缩放最清晰的交付格式；提高 DPI 不会增加源图信息或 PNG icon 内部细节。
