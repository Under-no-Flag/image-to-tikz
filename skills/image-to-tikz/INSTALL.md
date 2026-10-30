# 独立安装

将本文件所在的整个 `image-to-tikz/` 文件夹复制到宿主 agent 的 skill 目录。Codex 当前常用 `~/.agents/skills/` 或项目 `.agents/skills/`；使用 `~/.codex/skills/` 的桌面环境按其实际加载位置安装。不要覆盖未备份的同名 skill，不要安装重复副本。

1. 安装 Python 3.10+，创建虚拟环境，用该环境的 `python -m pip install -r /absolute/path/image-to-tikz/requirements.txt` 安装依赖。
2. 安装 XeLaTeX + Poppler，使 `xelatex`、`pdftoppm`、`pdfinfo` 在 PATH 中。中文需要 xeCJK 与中文字体。
3. 在用户级 `~/.image-to-tikz/config.yaml` 设置 `PADDLE_OCR_TOKEN`，或由安全环境变量注入。不要写在此 skill 文件夹中。
4. 运行 `python /absolute/path/image-to-tikz/scripts/workflow.py doctor`。
5. 向支持图像观察与本地执行的 agent 提交参考图，调用 `$image-to-tikz`。如要求生成独立语义图标，宿主还需要提供 GPT image_gen。

完整环境命令、API 配置、分区 OCR 和生图边界见 [references/operations.md](references/operations.md)。入口为 [SKILL.md](SKILL.md)。版本见 `VERSION`，包不依赖开发仓库、案例数据、其他 skill 或本机绝对路径；Python/TeX/云服务不随包分发。
