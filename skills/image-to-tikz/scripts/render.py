"""Deterministic TikZ emitter. Text escapes by default; formulas stay editable."""
from __future__ import annotations

import re
import glyphs
import advanced_glyphs
import icon_assets
from tex_numbers import decimal

from scene import structural_checks



def escape(text):
    replacements = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$",
        "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}
    return "".join(r"\\" if c == "\n" else replacements.get(c, c) for c in str(text))


def text_runs_tex(runs,base_weight='normal'):
    result=[]
    for run in runs:
        content=escape(run['text']);weight=run.get('weight',base_weight)
        # Redundant font groups introduce extra xeCJK boundary glue.
        result.append(content if weight==base_weight else '{'+(r'\bfseries ' if weight=='bold' else r'\mdseries ')+content+'}')
    return ''.join(result)


def macro(prefix, index):
    # Alphabetic TeX control sequence, independent of user ids with digits/hyphens.
    result = ""
    while True:
        result = chr(65 + index % 26) + result
        index = index // 26 - 1
        if index < 0:
            return prefix + result


def generate(scene):
    checks = structural_checks(scene)
    colors = {}

    def color(value):
        if value not in colors:
            colors[value] = f"ink{len(colors)}"
        return colors[value]

    font_commands = {key: macro("Font", i) for i, key in enumerate(scene["fonts"])}
    size_commands = {key: (macro("Width", i), macro("Height", i)) for i, key in enumerate(scene["sizes"])}
    token_commands = {key: macro("Gap", i) for i, key in enumerate(scene.get("layout_tokens_mm", {}))}
    definitions = []
    cjk_commands={}
    for font in scene['fonts'].values():
        if font.get('cjk_face'):
            pair=(font['cjk_face'],font.get('cjk_bold_face'))
            if pair not in cjk_commands:
                name=macro('CJKFont',len(cjk_commands));cjk_commands[pair]=name
                opts='[BoldFont={%s}]'%pair[1] if pair[1] else ''
                definitions.append(r'\newCJKfontfamily\%s%s{%s}'%(name,opts,pair[0]))
    for key, font in scene["fonts"].items():
        pt = font["size_pt"]
        family = {"serif":r"\rmfamily", "sans":r"\sffamily", "mono":r"\ttfamily"}[font.get("family", "serif")]
        if font.get('face'):family=r'\fontspec{%s}'%font['face']
        if font.get('cjk_face'):family+='\\'+cjk_commands[(font['cjk_face'],font.get('cjk_bold_face'))]
        weight = r"\bfseries" if font.get("weight") == "bold" else r"\mdseries"
        definitions.append(r"\newcommand{\%s}{\fontsize{%g}{%g}\selectfont%s\color{%s}}" % (
            font_commands[key], pt, pt*font.get("leading", 1.2), family+weight, color(font.get("color", "#222222"))))
    for key, (w, h) in scene["sizes"].items():
        wm, hm = size_commands[key]
        definitions += [r"\newcommand{\%s}{%gmm}" % (wm, w), r"\newcommand{\%s}{%gmm}" % (hm, h)]
    for key, value in scene.get("layout_tokens_mm", {}).items():
        definitions.append(r"\newcommand{\%s}{%gmm}" % (token_commands[key], value))

    styles = []
    for key, line in scene["line_styles"].items():
        common = f"draw={color(line.get('color', '#222222'))},line width={line['width_pt']}pt,{line.get('dash', 'solid')},line cap=round,line join=round"
        if line.get('dash_pattern_mm'):
            on,off=line['dash_pattern_mm'];common+=f",dash pattern=on {on}mm off {off}mm"
        if line.get('double'):common+=f",double,double distance={line.get('double_distance_mm',.35)}mm"
        arrow = {"none": "-", "start": "<-", "end": "->", "both": "<->"}[line.get("arrow", "end")]
        tipopts=[]
        if line.get('tip_open'):tipopts.append('open')
        for option,field in [('length','tip_length_mm'),('width','tip_width_mm')]:
            if field in line:tipopts.append(f"{option}={line[field]}mm")
        tip='{'+line.get('arrow_tip','Latex')+('['+','.join(tipopts)+']' if tipopts else '')+'}'
        if any(k in line for k in ['arrow_tip','tip_open','tip_length_mm','tip_width_mm']):
            arrow='arrows={'+{'none':'-','start':tip+'-','end':'-'+tip,'both':tip+'-'+tip}[line.get('arrow','end')]+'}'
        extras=''
        for field,opt in [('rounded_mm','rounded corners'),('shorten_start_mm','shorten <'),('shorten_end_mm','shorten >')]:
            if field in line:extras+=f",{opt}={line[field]}mm"
        styles += [f"border-{key}/.style={{{common}}}", f"edge-{key}/.style={{border-{key},{arrow}{extras}}}"]
    for key, style in scene["node_styles"].items():
        shape = {"rounded": f"rectangle,rounded corners={style.get('corner_mm', 2)}mm", "text": "rectangle,draw=none,fill=none"}.get(style["shape"], style["shape"])
        gradient=','+advanced_glyphs.paint_options(style,color) if style.get('gradient') else ''
        styles.append(f"node-{key}/.style={{border-{style['line']},fill={color(style.get('fill', '#FFFFFF'))},{shape},align=center,inner sep={style.get('padding_mm', 2)}mm,outer sep=0pt,opacity={style.get('opacity',1)},fill opacity={style.get('fill_opacity',style.get('opacity',1))},font=\\{font_commands[style['font']]}{gradient}}}")

    def distance(value, negative=False):
        if isinstance(value, str):
            return ("-" if negative else "") + "\\" + token_commands[value]
        return decimal(-value if negative else value)+"mm"

    def point(item):
        return "($(%s)+(%s,%s)$)" % (item["of"], distance(item.get("dx", 0)), distance(item.get("dy", 0), True))

    # Topological order keeps every reference defined before use.
    emitted, nodes, body = set(), scene["nodes"], []
    while len(emitted) < len(nodes):
        for node in nodes:
            if node["id"] in emitted:
                continue
            if "relative" in node and node["relative"]["of"] not in emitted:
                continue
            at = "(%smm,%smm)" % (decimal(node["at_mm"][0]), decimal(-node["at_mm"][1])) if "at_mm" in node else point(node["relative"])
            wm, hm = size_commands[node["size"]]
            node_style = scene["node_styles"][node["style"]]
            padding = node_style.get("padding_mm", 2)
            ratio = node_style.get("text_width_ratio", {"ellipse": .65, "diamond": .4}.get(node_style["shape"], 1))
            ratio_permille = round(ratio*1000)
            text = node["latex"] if "latex" in node else escape(node["text"])
            if 'text_runs' in node:
                text=text_runs_tex(node['text_runs'],scene['fonts'][node_style['font']].get('weight','normal'))
            if "text_rotate_deg" in node:
                text = r"\rotatebox{%g}{\shortstack{%s}}" % (node["text_rotate_deg"],text)
            body.append(r"\node[node-%s,minimum width=\%s,minimum height=\%s,text width=\dimexpr\%s*%d/1000-%gmm\relax] (%s) at %s {%s};" % (
                node["style"], wm, hm, wm, ratio_permille, 2*padding, node["id"], at, text))
            emitted.add(node["id"])
            if "asset" in node:
                body.append(icon_assets.draw(node,scene))
            if "glyph" in node:
                body.append(glyphs.draw(node, scene, color))
    for path in scene.get("component_paths", []):
        body.append(glyphs.draw_path(path, scene))
    for container in scene.get("containers", []):
        members = "".join("("+key+")" for key in container["members"])
        label = ""
        if container.get("title"):
            font = font_commands[scene["node_styles"][container["style"]]["font"]]
            label = ",label={[font=\\%s]above:%s}" % (font, escape(container["title"]))
        body += [r"\begin{scope}[on background layer]",
            r"\node[node-%s,fit=%s,inner sep=%gmm%s] (%s) {};" % (
                container["style"], members, container.get("padding_mm", 4), label, container["id"]),
            r"\end{scope}"]
    for edge in scene.get("edges", []):
        route = {"straight": "--", "hv": "-|", "vh": "|-", "polyline": "--"}[edge.get("route", "straight")]
        points = [f"({edge['from']})"] + [point(p) for p in edge.get("via", [])] + [f"({edge['to']})"]
        path = f" {route} ".join(points)
        if edge.get("label"):
            font = font_commands[edge.get("label_font", "body")]
            # label on final segment, as a native editable node.
            last = points[-1]
            path = path[:-len(last)] + r"node[midway,fill=white,inner sep=1pt,font=\%s] {%s} " % (font, escape(edge["label"])) + last
        body.append(r"\draw[edge-%s] %s; %% %s" % (edge["style"], path, edge["id"]))
    # Capture actual TeX extents to detect font-induced size growth after compile.
    body += [r"\ifdefined\CaptureTikZPositions", r"\newwrite\positions", r"\immediate\openout\positions=figure.positions"]
    for node in nodes:
        key = node["id"]
        body.append(r"\path let \p1=(%s.west),\p2=(%s.north),\p3=(%s.east),\p4=(%s.south) in \pgfextra{\immediate\write\positions{%s,\x1,\y2,\x3,\y4}};" % (key, key, key, key, key))
    body += [r"\immediate\closeout\positions", r"\fi"]
    color_defs = [r"\definecolor{%s}{HTML}{%s}" % (name, value[1:]) for value, name in colors.items()]
    styles_tex = "% Edit shared fonts, component sizes, gaps, borders and arrows here.\n" + "\n".join(color_defs+definitions) + "\n" + glyphs.MACROS + "\n\\tikzset{\n" + ",\n".join(styles) + "\n}\n"
    figure_tex = "% Editable native TikZ. Positive scene y points down.\n\\begin{tikzpicture}[>=Latex]\n" + "\n".join(body) + "\n\\end{tikzpicture}\n"
    # preview.tex uses widely installed article+geometry, no standalone.cls dependency.
    boxes = list(checks["nominal_boxes_mm"].values())
    width = max(b[2] for b in boxes)-min(b[0] for b in boxes)+30
    height = max(b[3] for b in boxes)-min(b[1] for b in boxes)+35
    preview_tex = r"""\RequirePackage{fix-cm}
\documentclass{article}
\usepackage[paperwidth=%gmm,paperheight=%gmm,margin=5mm]{geometry}
\usepackage{graphicx}
\usepackage{fontspec}
\usepackage{xeCJK}
\IfFontExistsTF{PingFang SC}{\setCJKmainfont{PingFang SC}}{\IfFontExistsTF{Noto Sans CJK SC}{\setCJKmainfont{Noto Sans CJK SC}}{\IfFontExistsTF{Heiti SC}{\setCJKmainfont{Heiti SC}}{\setCJKmainfont[BoldFont=FandolHei-Bold.otf]{FandolHei-Regular.otf}}}}
\usepackage{tikz}
\usetikzlibrary{arrows.meta,calc,positioning,fit,backgrounds,shapes.geometric}
\pagestyle{empty}
\newcommand{\CaptureTikZPositions}{}
\input{styles.tex}
\begin{document}
\noindent\input{figure.tex}
\end{document}
""" % (width, height)
    return {"styles.tex": styles_tex, "figure.tex": figure_tex, "preview.tex": preview_tex}
