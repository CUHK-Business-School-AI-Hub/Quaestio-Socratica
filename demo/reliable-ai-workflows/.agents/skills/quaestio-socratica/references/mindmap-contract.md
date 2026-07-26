# Personalized mindmap contract

Create a conventional spatial mind map, not an indented list presented as a
tree. The finished artifact is `outputs/personalized-mindmap.html`.

## Spatial grammar

- Put the course title in one visually dominant central topic.
- Draw every checkpoint as a primary branch connected to that center.
- Draw knowledge nodes as secondary topics connected to their checkpoint.
- Use visible CSS connectors between the center, branches, and topics. CSS
  pseudo-elements, borders, transforms, Grid, and Flexbox are sufficient.
- Preserve cross-checkpoint dependencies in the node-detail panel as
  `Depends on` and `Unlocks` links. Do not distort the main map merely to draw
  every graph edge.
- Never render the primary map as a nested `<ul>`, an outline, a sidebar, or a
  vertically indented document.

The desktop view must reveal the center-to-branch geometry at a glance. A
compact mobile fallback may stack branches, but it must preserve topic grouping
and visual connectors.

## Personal learning state

Show every node's recorded status through both color and text:

- `mastered`
- `self_reported`
- `needs_review`
- `forced_skip`
- `in_progress`
- `planned`

Mark core nodes visibly. Selecting a node should reveal its learning outcome,
acceptable evidence, prerequisites, downstream connections, and personal note
when present.

## Interaction and language

- Let the learner fold and unfold each checkpoint branch.
- Use the learner's first-dialogue language for interface labels.
- If the learner requested bilingual final outputs, include both language
  versions or an explicit in-page language switch.
- Preserve precise English or Latin terms when translating them would reduce
  disciplinary clarity.
- Ensure controls are keyboard accessible and meaningful without color alone.

## Portability and privacy

- Produce one UTF-8 HTML file with inline CSS and JavaScript.
- Do not load CDNs, web fonts, analytics, remote images, or any other network
  dependency.
- Read only the compiled knowledge map and durable learner state. Do not embed
  a raw conversation transcript.
- Escape learner-authored and source-authored text before inserting it into
  markup or script data.

An agent may author this file directly. When Python is already available,
`scripts/build_mindmap.py` provides a deterministic implementation of this
contract, but Python is not a learner requirement.
