"""Small semantic scene IR: shared styles, sizes and relative coordinates."""
from __future__ import annotations

import math
import re
import icon_assets
from glyphs import validate_glyph, validate_paths

ID = re.compile(r"^[a-z][a-z0-9-]*$")
ANCHORS = {"center", "north", "south", "east", "west", "north east", "north west", "south east", "south west"}
SHAPES = {"rectangle", "rounded", "ellipse", "diamond", "text"}


def number(value, name, positive=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number")
    if positive and value <= 0:
        raise ValueError(f"{name} must be positive")
    return float(value)


def endpoint(value, ids):
    node, _, anchor = value.partition(".")
    if node not in ids or (anchor and anchor not in ANCHORS):
        raise ValueError(f"Unknown endpoint: {value}")
    return node, anchor or "center"


def offset(value, tokens):
    return number(tokens[value] if isinstance(value, str) else value, "offset")


def resolve(scene):
    nodes = {n["id"]: n for n in scene["nodes"]}
    positions, visiting = {}, set()
    tokens = scene.get("layout_tokens_mm", {})

    def visit(key):
        if key in visiting:
            raise ValueError(f"Relative layout cycle at {key}")
        if key in positions:
            return positions[key]
        visiting.add(key)
        item = nodes[key]
        if "at_mm" in item:
            x, y = item["at_mm"]
        else:
            rel = item["relative"]
            x, y = visit(rel["of"])
            x += offset(rel.get("dx", 0), tokens)
            y += offset(rel.get("dy", 0), tokens)
        visiting.remove(key)
        positions[key] = (number(x, "x"), number(y, "y"))
        return positions[key]

    for key in nodes:
        visit(key)
    return positions


def validate(scene):
    if scene.get("schema_version") != 1:
        raise ValueError("schema_version must be 1")
    if not scene.get("nodes"):
        raise ValueError("scene must contain nodes")
    for collection in ("fonts", "line_styles", "node_styles", "sizes", "layout_tokens_mm"):
        for key in scene.get(collection, {}):
            if not ID.fullmatch(key):
                raise ValueError(f"Invalid {collection} key: {key}")
    for key, value in scene.get("layout_tokens_mm", {}).items():
        number(value, key)
    for font in scene["fonts"].values():
        for field in ['face','cjk_face','cjk_bold_face']:
            if field in font and not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9 ._-]{0,99}',font[field]):raise ValueError('Unsafe font face name')
        number(font["size_pt"], "font size", True)
        number(font.get("leading",1.2), "line spacing", True)
        if font.get("family","serif") not in ("serif","sans","mono"): raise ValueError("Unknown font family")
        if font.get("weight", "normal") not in {"normal", "bold"}:
            raise ValueError("font weight must be normal or bold")
    for line in scene["line_styles"].values():
        number(line["width_pt"], "line width", True)
        if line.get("dash", "solid") not in {"solid", "dashed", "dotted"}:
            raise ValueError("Unknown dash pattern")
        if line.get("arrow", "end") not in {"none", "start", "end", "both"}:
            raise ValueError("Unknown arrow style")
        if line.get("arrow_tip","Latex") not in {"Latex","Stealth","Triangle","To","Bar","Circle"}: raise ValueError("Unsupported arrow tip")
        for key in ["tip_length_mm","tip_width_mm","double_distance_mm"]:
            if key in line:number(line[key],key,True)
        for key in ["rounded_mm","shorten_start_mm","shorten_end_mm"]:
            if key in line:
                if number(line[key],key)<0:raise ValueError("Negative edge geometry")
        if "dash_pattern_mm" in line:
            if len(line['dash_pattern_mm'])!=2:raise ValueError("Dash pattern needs on/off lengths")
            for v in line['dash_pattern_mm']:number(v,"dash length",True)
        for key in ['tip_open','double']:
            if key in line and type(line[key])is not bool:raise ValueError('Expected boolean arrow option')
    for size in scene["sizes"].values():
        w, h = size
        number(w, "width", True)
        number(h, "height", True)
    for style in scene["node_styles"].values():
        opacity=number(style.get("opacity",1),"opacity")
        if not 0<=opacity<=1: raise ValueError("Opacity out of range")
        number(style.get("corner_mm",2),"corner radius",True)
        if not 0<=number(style.get("fill_opacity",1),"fill opacity")<=1: raise ValueError("Fill opacity out of range")
        if style["shape"] not in SHAPES:
            raise ValueError("Unsupported shape")
        if style["font"] not in scene["fonts"] or style["line"] not in scene["line_styles"]:
            raise ValueError("Node style refers to unknown font or line")
        if number(style.get("padding_mm", 2), "padding")<0:raise ValueError("Padding must be nonnegative")
        ratio = number(style.get("text_width_ratio", 1), "text width ratio", True)
        if ratio > 1:
            raise ValueError("text_width_ratio must be <= 1")
        if 'gradient' in style:
            g=style['gradient']
            if any(not re.fullmatch(r'#[0-9a-fA-F]{6}',g.get(k,'')) for k in ['from','to']):raise ValueError('Invalid gradient color')
            number(g.get('angle_deg',0),'gradient angle')
    colors = [v.get("color", "#222222") for v in scene["line_styles"].values()]
    colors += [v.get("fill", "#FFFFFF") for v in scene["node_styles"].values()]
    colors += [v.get("color", "#222222") for v in scene["fonts"].values()]
    if any(not re.fullmatch(r"#[0-9a-fA-F]{6}", c) for c in colors):
        raise ValueError("Colors must be #RRGGBB")
    all_items = scene["nodes"] + scene.get("containers", []) + scene.get("edges", [])
    ids = [v["id"] for v in all_items]
    if len(ids) != len(set(ids)) or any(not ID.fullmatch(v) for v in ids):
        raise ValueError("Object ids must be unique, lowercase, letters/digits/hyphens")
    node_ids = {n["id"] for n in scene["nodes"]}
    for node in scene["nodes"]:
        number(node.get("text_rotate_deg",0),"text rotation")
        if node["style"] not in scene["node_styles"] or node["size"] not in scene["sizes"]:
            raise ValueError(f"Unknown style/size for {node['id']}")
        if ("text" in node) == ("latex" in node):
            raise ValueError(f"{node['id']}: set exactly one of text or latex")
        if 'text_runs' in node:
            if 'latex' in node or not isinstance(node['text_runs'],list):raise ValueError('Text runs require plain text')
            for run in node['text_runs']:
                if not isinstance(run.get('text'),str) or run.get('weight','normal') not in ('normal','bold'):raise ValueError('Invalid text run')
            if ''.join(r['text'] for r in node['text_runs'])!=node['text']:raise ValueError('Text runs must concatenate to full node text')
        if "latex" in node and not node.get("latex_reviewed"):
            raise ValueError(f"{node['id']}: formula requires latex_reviewed=true")
        if ("at_mm" in node) == ("relative" in node):
            raise ValueError(f"{node['id']}: set exactly one of at_mm or relative")
        if "at_mm" in node:
            x, y = node["at_mm"]
            number(x, "x"); number(y, "y")
        elif node["relative"]["of"] not in node_ids:
            raise ValueError(f"{node['id']}: relative reference missing")
        w, h = scene["sizes"][node["size"]]
        style = scene["node_styles"][node["style"]]
        ratio = style.get("text_width_ratio", {"ellipse": .65, "diamond": .4}.get(style["shape"], 1))
        if w*ratio <= 2*style.get("padding_mm", 2):
            raise ValueError(f"{node['id']}: component width leaves no text area")
    for container in scene.get("containers", []):
        if not container.get("members") or not set(container["members"]) <= node_ids:
            raise ValueError("Container must contain known node ids")
        if container["style"] not in scene["node_styles"]:
            raise ValueError("Unknown container style")
        number(container.get("padding_mm", 4), "container padding", True)
    for edge in scene.get("edges", []):
        endpoint(edge["from"], node_ids); endpoint(edge["to"], node_ids)
        if edge["style"] not in scene["line_styles"]:
            raise ValueError("Unknown edge style")
        if edge.get("route", "straight") not in {"straight", "hv", "vh", "polyline"}:
            raise ValueError("Unsupported edge route")
        for point in edge.get("via", []):
            endpoint(point["of"], node_ids)
            offset(point.get("dx", 0), scene.get("layout_tokens_mm", {}))
            offset(point.get("dy", 0), scene.get("layout_tokens_mm", {}))
        if "label" in edge and edge.get("label_font", "body") not in scene["fonts"]:
            raise ValueError("Unknown edge label font")
    for node in scene["nodes"]:
        if "glyph" in node: validate_glyph(node, scene)
    icon_assets.validate(scene)
    validate_paths(scene)
    return resolve(scene)


def structural_checks(scene):
    positions = validate(scene)
    warnings = []
    roots = [n["id"] for n in scene["nodes"] if "at_mm" in n]
    if len(roots) > 1:
        warnings.append(f"Multiple absolute roots {roots}; justify independent components in review")
    boxes = {}
    for node in scene["nodes"]:
        x, y = positions[node["id"]]
        w, h = scene["sizes"][node["size"]]
        boxes[node["id"]] = [x-w/2, y-h/2, x+w/2, y+h/2]
    warnings.extend(geometry_checks(scene, boxes))
    return {"positions_mm": positions, "nominal_boxes_mm": boxes, "warnings": warnings}


def geometry_checks(scene, boxes):
    """Apply the same overlap/alignment promises to nominal or real TeX boxes."""
    warnings = []
    allowed = {frozenset(v["nodes"]) for v in scene.get("allowed_overlaps", []) if v.get("reason")}
    groups = {n["id"] for n in scene["nodes"] if n.get("role")=="group"}
    keys = list(boxes)
    for i, first in enumerate(keys):
        a = boxes[first]
        for second in keys[i+1:]:
            b = boxes[second]
            if ((first in groups and a[0]<=b[0]+.1 and a[1]<=b[1]+.1 and a[2]>=b[2]-.1 and a[3]>=b[3]-.1) or (second in groups and b[0]<=a[0]+.1 and b[1]<=a[1]+.1 and b[2]>=a[2]-.1 and b[3]>=a[3]-.1)):
                continue
            if min(a[2], b[2])-max(a[0], b[0]) > .1 and min(a[3], b[3])-max(a[1], b[1]) > .1:
                if frozenset((first, second)) not in allowed:
                    warnings.append(f"Node boxes overlap: {first}, {second}")
    # Explicit alignment groups are promises, not hints; mismatches fail QA.
    for group in scene.get("alignments", []):
        axis = group["axis"]
        if axis not in {"x", "y", "left", "right", "top", "bottom"}:
            raise ValueError(f"Unknown alignment axis {axis}")
        values = []
        for key in group["nodes"]:
            if key not in boxes:
                raise ValueError(f"Alignment references unknown node {key}")
            box = boxes[key]
            values.append(((box[0]+box[2])/2 if axis == "x" else (box[1]+box[3])/2) if axis in {"x", "y"}
                else box[{"left": 0, "top": 1, "right": 2, "bottom": 3}[axis]])
        if len(values) < 2 or max(values)-min(values) > .1:
            warnings.append(f"Alignment violated: {axis} {group['nodes']}")
    return warnings
