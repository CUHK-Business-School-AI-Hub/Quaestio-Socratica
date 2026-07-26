#!/usr/bin/env python3
"""Build a conventional offline CSS mindmap from Quaestio Socratica state."""

from __future__ import annotations

import argparse
import csv
import html
import json
import re
import sys
from pathlib import Path


ALLOWED_STATUS = {
    "planned",
    "in_progress",
    "mastered",
    "self_reported",
    "forced_skip",
    "needs_review",
}

LABELS = {
    "zh": {
        "eyebrow": "Quaestio Socratica · 个人知识地图",
        "map_label": "课程知识地图",
        "mastered": "已掌握",
        "self_reported": "自述掌握",
        "needs_review": "待加强",
        "forced_skip": "强制跳过",
        "in_progress": "学习中",
        "planned": "待学习",
        "core": "核心节点",
        "learning_outcome": "学习目标",
        "evidence": "掌握证据",
        "depends_on": "先修节点",
        "unlocks": "后续连接",
        "personal_note": "个人记录",
        "select": "选择一个知识节点，查看它在整门课程中的位置。",
        "nodes": "个知识节点",
        "footer": "完全本地生成 · 无外部脚本、字体、分析或网络请求",
    },
    "en": {
        "eyebrow": "Quaestio Socratica · personal knowledge map",
        "map_label": "Course knowledge map",
        "mastered": "mastered",
        "self_reported": "self-reported",
        "needs_review": "needs review",
        "forced_skip": "forced skip",
        "in_progress": "in progress",
        "planned": "planned",
        "core": "core node",
        "learning_outcome": "Learning outcome",
        "evidence": "Acceptable evidence",
        "depends_on": "Depends on",
        "unlocks": "Unlocks",
        "personal_note": "Personal note",
        "select": "Select a knowledge node to see how it connects to the course.",
        "nodes": "knowledge nodes",
        "footer": "Generated locally · no external scripts, fonts, analytics, or network requests",
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("course_root", type=Path)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def split_ids(value: str) -> list[str]:
    return [item.strip() for item in value.split(";") if item.strip()]


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return [
            {key: (value or "").strip() for key, value in row.items()}
            for row in csv.DictReader(handle)
        ]


def status_fields(root: Path) -> dict[str, str]:
    text = (root / "course/course-status.md").read_text(encoding="utf-8")
    fields: dict[str, str] = {}
    for line in text.splitlines():
        match = re.match(r"^-\s+([^:]+):\s*(.*)$", line)
        if match:
            fields[match.group(1).strip()] = match.group(2).strip()
    return fields


def language_for(fields: dict[str, str]) -> str:
    language = fields.get("First dialogue language", "").lower()
    if any(token in language for token in ("中文", "chinese", "zh")):
        return "zh"
    if any(token in language for token in ("english", "英文", "en")):
        return "en"
    title = fields.get("Course title", "")
    return "zh" if re.search(r"[\u3400-\u9fff]", title) else "en"


def checkpoint_titles(root: Path) -> dict[str, str]:
    route = (root / "course/standard-route.md").read_text(encoding="utf-8")
    titles: dict[str, str] = {}
    for checkpoint, title in re.findall(
        r"^##\s+(CP\d{2,})\s*[—–:-]\s*(.+?)\s*$", route, flags=re.MULTILINE
    ):
        titles[checkpoint] = title.strip()
    return titles


def assert_acyclic(nodes: dict[str, dict[str, object]]) -> None:
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node_id: str) -> None:
        if node_id in visiting:
            raise ValueError(f"knowledge graph contains a cycle at {node_id}")
        if node_id in visited:
            return
        visiting.add(node_id)
        parents = nodes[node_id]["parents"]
        assert isinstance(parents, list)
        for parent_id in parents:
            visit(str(parent_id))
        visiting.remove(node_id)
        visited.add(node_id)

    for node_id in nodes:
        visit(node_id)


def build_data(root: Path) -> dict[str, object]:
    knowledge_rows = read_rows(root / "course/knowledge-map.csv")
    progress_rows = read_rows(root / "learner/progress.csv")
    progress = {row["node_id"]: row for row in progress_rows}

    if not knowledge_rows:
        raise ValueError("knowledge map has no nodes")

    nodes: dict[str, dict[str, object]] = {}
    checkpoint_order: list[str] = []
    for row in knowledge_rows:
        node_id = row["node_id"]
        if not node_id or node_id in nodes:
            raise ValueError(f"missing or duplicate node_id: {node_id!r}")
        parents = split_ids(row["parent_ids"])
        status = progress.get(node_id, {}).get("status", "planned")
        if status not in ALLOWED_STATUS:
            raise ValueError(f"node {node_id} has invalid status: {status}")
        checkpoint = row["checkpoint_id"]
        if checkpoint not in checkpoint_order:
            checkpoint_order.append(checkpoint)
        nodes[node_id] = {
            "id": node_id,
            "title": row["title"],
            "parents": parents,
            "checkpoint": checkpoint,
            "core": row["core"] == "true",
            "outcome": row["learning_outcome"],
            "evidence": row["evidence"],
            "status": status,
            "notes": progress.get(node_id, {}).get("notes", ""),
            "children": [],
        }

    for node_id, node in nodes.items():
        parents = node["parents"]
        assert isinstance(parents, list)
        for parent_id in parents:
            if parent_id not in nodes:
                raise ValueError(f"node {node_id} references unknown parent {parent_id}")
            children = nodes[parent_id]["children"]
            assert isinstance(children, list)
            children.append(node_id)

    assert_acyclic(nodes)
    roots = [
        node_id
        for node_id, node in nodes.items()
        if isinstance(node["parents"], list) and not node["parents"]
    ]
    if not roots:
        raise ValueError("knowledge graph has no root node")

    titles = checkpoint_titles(root)
    checkpoints = [
        {
            "id": checkpoint,
            "title": titles.get(checkpoint, checkpoint),
            "node_ids": [
                node_id
                for node_id, node in nodes.items()
                if node["checkpoint"] == checkpoint
            ],
        }
        for checkpoint in checkpoint_order
    ]

    fields = status_fields(root)
    language = language_for(fields)
    return {
        "title": fields.get("Course title", root.name),
        "language": language,
        "labels": LABELS[language],
        "roots": roots,
        "nodes": list(nodes.values()),
        "checkpoints": checkpoints,
    }


def render_html(data: dict[str, object]) -> str:
    title = str(data["title"])
    language = str(data["language"])
    payload = json.dumps(data, ensure_ascii=False).replace("<", "\\u003c")
    escaped_title = html.escape(title)
    return f"""<!doctype html>
<html lang="{language}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escaped_title} · Mindmap</title>
<style>
:root {{
  color-scheme: dark;
  --ink:#f4f0e6; --muted:#a8a59d; --panel:#171a1f; --line:#424750;
  --gold:#e7b65a; --green:#65c995; --blue:#739fff; --red:#f17878;
  --violet:#b798ff; --amber:#e9a84c; --gray:#7d838f;
}}
* {{ box-sizing:border-box }}
body {{
  margin:0; min-height:100vh; color:var(--ink);
  font-family:ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;
  background:
    radial-gradient(circle at 8% 4%,#30233b 0,transparent 34rem),
    radial-gradient(circle at 96% 18%,#153748 0,transparent 34rem),
    #0d0f12;
}}
header {{ padding:2.8rem clamp(1.2rem,5vw,5rem) 1.6rem }}
.eyebrow {{ color:var(--gold); letter-spacing:.17em; text-transform:uppercase; font-size:.7rem }}
h1 {{
  max-width:28ch; margin:.45rem 0 1.2rem; font-family:Georgia,serif;
  font-size:clamp(2.1rem,4.2vw,4.35rem); line-height:.98; text-wrap:balance;
}}
.legend {{ display:flex; flex-wrap:wrap; gap:.5rem }}
.legend span,.badge {{
  display:inline-flex; align-items:center; gap:.4rem; border:1px solid #373c45;
  border-radius:999px; padding:.3rem .65rem; color:#d9d6cf; font-size:.72rem;
}}
.dot {{ width:.55rem; height:.55rem; border-radius:50% }}
.mastered {{ --state:var(--green) }} .self_reported {{ --state:var(--blue) }}
.forced_skip {{ --state:var(--red) }} .needs_review {{ --state:var(--amber) }}
.in_progress {{ --state:var(--violet) }} .planned {{ --state:var(--gray) }}
.dot,.status-dot {{ background:var(--state) }}
.map-shell {{
  margin:0 clamp(.8rem,2vw,2rem); border:1px solid #30353d; border-radius:1.5rem;
  background:rgba(20,23,28,.88); box-shadow:0 1.2rem 4rem #0008; overflow:auto;
}}
.mindmap {{
  --connector:#545a66;
  min-width:1440px; min-height:620px; padding:3rem;
  display:grid; grid-template-columns:minmax(30rem,1fr) 17rem minmax(30rem,1fr); gap:3.5rem;
  align-items:center; position:relative;
}}
.center-topic {{
  grid-column:2;
  position:relative; z-index:2; min-height:11rem; padding:1.5rem;
  display:flex; flex-direction:column; justify-content:center;
  border:2px solid var(--gold); border-radius:46% 54% 51% 49% / 42% 44% 56% 58%;
  background:linear-gradient(145deg,#3e2d23,#1d2026 70%); box-shadow:0 0 3rem #e7b65a20;
}}
.center-topic::before,.center-topic::after {{
  content:""; position:absolute; top:50%; width:3.5rem;
  border-top:2px solid var(--connector);
}}
.center-topic::before {{ right:100% }}
.center-topic::after {{ left:100% }}
.center-topic strong {{ font-family:Georgia,serif; font-size:1.65rem; line-height:1.08 }}
.center-topic small {{ margin-top:.65rem; color:var(--gold); line-height:1.4 }}
.branch-stack {{
  position:relative; display:flex; flex-direction:column; gap:2.2rem;
}}
.branch-stack.left {{ grid-column:1; grid-row:1 }}
.branch-stack.right {{ grid-column:3; grid-row:1 }}
.branch-stack.left::after,.branch-stack.right::before {{
  content:""; position:absolute; top:2.2rem; bottom:2.2rem;
  border-left:2px solid var(--connector);
}}
.branch-stack.left::after {{ right:-1.75rem }}
.branch-stack.right::before {{ left:-1.75rem }}
.branch {{
  --branch:#73a7ff; position:relative;
  display:grid; gap:2.4rem; align-items:center;
}}
.branch.left {{ grid-template-columns:minmax(0,1fr) 13rem }}
.branch.right {{ grid-template-columns:13rem minmax(0,1fr) }}
.branch:nth-child(4n+1) {{ --branch:#73a7ff }}
.branch:nth-child(4n+2) {{ --branch:#b798ff }}
.branch:nth-child(4n+3) {{ --branch:#65c995 }}
.branch:nth-child(4n+4) {{ --branch:#e9a84c }}
.branch.left::after,.branch.right::before {{
  content:""; position:absolute; top:50%; width:1.75rem;
  border-top:2px solid var(--connector);
}}
.branch.left::after {{ left:100% }}
.branch.right::before {{ right:100% }}
.branch-head {{
  position:relative; min-height:5.2rem; width:100%; padding:.9rem 1rem;
  color:var(--ink); text-align:left; cursor:pointer; border:1px solid color-mix(in srgb,var(--branch) 60%,#333);
  border-radius:1.1rem; background:color-mix(in srgb,var(--branch) 13%,#20242a);
}}
.branch.left .branch-head {{ grid-column:2 }}
.branch.right .branch-head {{ grid-column:1 }}
.branch.left .branch-head::before,.branch.right .branch-head::after {{
  content:""; position:absolute; top:50%; width:2.4rem;
  border-top:2px solid var(--branch);
}}
.branch.left .branch-head::before {{ right:100% }}
.branch.right .branch-head::after {{ left:100% }}
.branch-head:hover,.branch-head:focus-visible {{ outline:none; box-shadow:0 0 0 3px color-mix(in srgb,var(--branch) 22%,transparent) }}
.branch-head b {{ display:block; color:var(--branch); letter-spacing:.12em; font-size:.72rem }}
.branch-head strong {{ display:block; margin-top:.32rem; font-size:.98rem; line-height:1.24 }}
.branch-head small {{ display:block; margin-top:.4rem; color:var(--muted) }}
.branch-toggle {{ position:absolute; right:.7rem; top:.7rem; color:var(--branch) }}
.node-cloud {{
  position:relative; display:grid; grid-template-columns:repeat(2,minmax(13rem,1fr));
  gap:.8rem 1rem;
}}
.branch.left .node-cloud {{ grid-column:1; padding-right:1.2rem }}
.branch.right .node-cloud {{ grid-column:2; padding-left:1.2rem }}
.branch.left .node-cloud::after,.branch.right .node-cloud::before {{
  content:""; position:absolute; top:1.6rem; bottom:1.6rem;
  border-left:2px solid var(--branch);
}}
.branch.left .node-cloud::after {{ right:0 }}
.branch.right .node-cloud::before {{ left:0 }}
.topic {{
  position:relative; display:grid; grid-template-columns:auto 1fr; gap:.65rem; align-items:start;
  min-height:4.7rem; padding:.8rem .9rem; color:var(--ink); text-align:left; cursor:pointer;
  border:1px solid #3a4049; border-radius:.9rem; background:#22262d;
}}
.branch.left .topic::after,.branch.right .topic::before {{
  content:""; position:absolute; top:50%; width:1.2rem;
  border-top:2px solid var(--branch);
}}
.branch.left .topic::after {{ left:100% }}
.branch.right .topic::before {{ right:100% }}
.topic:hover,.topic:focus-visible {{ outline:none; border-color:var(--branch); transform:translateY(-1px) }}
.status-dot {{ width:.72rem; height:.72rem; margin-top:.2rem; border-radius:50%; box-shadow:0 0 0 .22rem #ffffff0b }}
.topic strong {{ display:block; font-size:.9rem; line-height:1.25 }}
.topic small {{ display:block; margin-top:.27rem; color:var(--muted); font-size:.7rem }}
.branch.left.collapsed {{ grid-template-columns:13rem; justify-content:end }}
.branch.right.collapsed {{ grid-template-columns:13rem; justify-content:start }}
.branch.collapsed .node-cloud {{ display:none }}
.branch.collapsed .branch-head::before,.branch.collapsed .branch-head::after {{ display:none }}
.detail {{
  margin:1rem clamp(.8rem,2vw,2rem) 2rem; padding:1.5rem clamp(1rem,3vw,2.2rem);
  display:grid; grid-template-columns:minmax(14rem,.72fr) minmax(18rem,1.28fr); gap:2rem;
  background:rgba(20,23,28,.88); border:1px solid #30353d; border-radius:1.3rem;
}}
.detail h2 {{ margin:.35rem 0 .9rem; font-family:Georgia,serif; font-size:1.8rem }}
.detail p {{ color:#d7d4cc; line-height:1.58 }}
.detail-grid {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:1.2rem }}
.label {{ color:var(--gold); font-size:.68rem; letter-spacing:.12em; text-transform:uppercase }}
.cross {{ display:flex; flex-wrap:wrap; gap:.4rem; margin-top:.45rem }}
.core {{ color:#151515; background:var(--gold); border-color:var(--gold) }}
footer {{ padding:0 clamp(1rem,3vw,3rem) 2rem; color:var(--muted); font-size:.72rem }}
@media (max-width:760px) {{
  .mindmap {{ min-width:0; display:flex; flex-direction:column; padding:1.2rem }}
  .center-topic {{ min-height:auto; border-radius:1.2rem; margin-bottom:2rem; order:1 }}
  .branch-stack.left {{ display:block; order:2; width:100% }}
  .branch-stack.right {{ display:block; order:3; width:100% }}
  .center-topic::before,.center-topic::after,
  .branch-stack.left::after,.branch-stack.right::before,
  .branch.left::after,.branch.right::before,
  .branch.left .branch-head::before,.branch.right .branch-head::after,
  .branch.left .node-cloud::after,.branch.right .node-cloud::before,
  .branch.left .topic::after,.branch.right .topic::before {{ display:none }}
  .branch {{ display:block; margin-bottom:1.4rem }}
  .branch-head {{ margin-bottom:.7rem }}
  .branch.left .node-cloud,.branch.right .node-cloud {{ grid-template-columns:1fr; padding-left:1rem; padding-right:0; border-left:2px solid var(--branch) }}
  .detail,.detail-grid {{ grid-template-columns:1fr }}
}}
</style>
</head>
<body>
<header>
  <div class="eyebrow" id="eyebrow"></div>
  <h1>{escaped_title}</h1>
  <div class="legend" id="legend"></div>
</header>
<section class="map-shell">
  <div id="mindmap" class="mindmap" role="region"></div>
</section>
<aside class="detail" id="detail"></aside>
<footer id="footer"></footer>
<script>
const DATA={payload};
const L=DATA.labels;
const nodes=new Map(DATA.nodes.map(n=>[n.id,n]));
const mindmap=document.getElementById("mindmap");
const detail=document.getElementById("detail");
const element=(tag,cls,value)=>{{const e=document.createElement(tag);if(cls)e.className=cls;if(value!==undefined)e.textContent=value;return e}};
document.documentElement.lang=DATA.language;
document.getElementById("eyebrow").textContent=L.eyebrow;
document.getElementById("footer").textContent=L.footer;
mindmap.setAttribute("aria-label",L.map_label);
const legend=document.getElementById("legend");
["mastered","self_reported","needs_review","forced_skip","in_progress","planned"].forEach(status=>{{
  const item=element("span");item.append(element("i","dot "+status));item.append(document.createTextNode(L[status]));legend.append(item);
}});
const leftStack=element("div","branch-stack left");
const center=element("div","center-topic");
center.append(element("strong","",DATA.title));
center.append(element("small","",DATA.checkpoints.length+" checkpoints · "+DATA.nodes.length+" "+L.nodes));
mindmap.append(leftStack);
mindmap.append(center);
const rightStack=element("div","branch-stack right");
mindmap.append(rightStack);
function chips(ids){{
  const wrap=element("div","cross");
  ids.forEach(id=>wrap.append(element("span","badge",nodes.get(id)?.title||id)));
  return wrap;
}}
function show(n){{
  detail.replaceChildren();
  const intro=element("section");
  intro.append(element("div","eyebrow",n.checkpoint+" · "+L[n.status]));
  intro.append(element("h2","",n.title));
  const badges=element("div","cross");
  if(n.core)badges.append(element("span","badge core",L.core));
  badges.append(element("span","badge",n.id));
  intro.append(badges);
  const grid=element("section","detail-grid");
  const outcome=element("div");outcome.append(element("div","label",L.learning_outcome));outcome.append(element("p","",n.outcome));grid.append(outcome);
  const evidence=element("div");evidence.append(element("div","label",L.evidence));evidence.append(element("p","",n.evidence));grid.append(evidence);
  if(n.parents.length){{const block=element("div");block.append(element("div","label",L.depends_on));block.append(chips(n.parents));grid.append(block)}}
  if(n.children.length){{const block=element("div");block.append(element("div","label",L.unlocks));block.append(chips(n.children));grid.append(block)}}
  if(n.notes){{const block=element("div");block.append(element("div","label",L.personal_note));block.append(element("p","",n.notes));grid.append(block)}}
  detail.append(intro);detail.append(grid);
}}
DATA.checkpoints.forEach((cp,index)=>{{
  const side=index%2===0?"right":"left";
  const branch=element("section","branch "+side);
  const head=element("button","branch-head");head.type="button";
  head.append(element("b","",cp.id));
  head.append(element("strong","",cp.title));
  head.append(element("small","",cp.node_ids.length+" "+L.nodes));
  head.append(element("span","branch-toggle","−"));
  const cloud=element("div","node-cloud");
  cp.node_ids.forEach(id=>{{
    const n=nodes.get(id),button=element("button","topic");button.type="button";
    button.append(element("i","status-dot "+n.status));
    const copy=element("span");copy.append(element("strong","",n.title));copy.append(element("small","",n.id+(n.core?" · "+L.core:"")));
    button.append(copy);button.addEventListener("click",()=>show(n));cloud.append(button);
  }});
  head.addEventListener("click",()=>{{
    branch.classList.toggle("collapsed");
    head.querySelector(".branch-toggle").textContent=branch.classList.contains("collapsed")?"+":"−";
  }});
  if(side==="left"){{branch.append(cloud);branch.append(head);leftStack.append(branch)}}
  else{{branch.append(head);branch.append(cloud);rightStack.append(branch)}}
}});
const first=DATA.nodes[0];
if(first)show(first);else detail.append(element("p","",L.select));
</script>
</body>
</html>
"""


def build(course_root: Path, output: Path | None = None) -> Path:
    root = course_root.expanduser().resolve()
    data = build_data(root)
    target = (
        output.expanduser().resolve()
        if output
        else root / "outputs" / "personalized-mindmap.html"
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_html(data), encoding="utf-8")
    return target


def main() -> int:
    args = parse_args()
    try:
        target = build(args.course_root, args.output)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"Mindmap written: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
