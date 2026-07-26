# Artifact contracts

Use UTF-8. Keep state human-readable and editable. Prefer Markdown for narrative and CSV for repeated records.

## Required course files

### `course/course-status.md`

Use these labeled fields:

- `Lifecycle`: `draft`, `compiling`, `awaiting_approval`, `approved`, `learning`, or `completed`
- `Initialization mode`: `undecided` before the first dialogue, then `teacher` or `self`
- `Course title`
- `Course version`
- `Tutor mode`: `unselected`, `course-mentor`, or `immersive`
- `First dialogue language`: `unselected` until the first learner message
- `Approved by`: blank before approval
- `Approved on`: ISO date or blank

### `course/source-register.csv`

Columns:

`source_id,title,kind,location,provenance,authority,time_sensitive,retrieved_on,used_for,notes`

Allowed provenance: `provided`, `external`, `ai-synthesis`, `inference`.

### `course/knowledge-map.csv`

Columns:

`node_id,title,parent_ids,checkpoint_id,core,estimated_minutes,learning_outcome,evidence,source_ids`

- Separate multiple parents or sources with `;`.
- Use `true` or `false` for `core`.
- Every parent must reference an existing node.
- Every non-root node needs at least one parent.
- Checkpoint IDs use `CP01`, `CP02`, and so on.

### `course/standard-route.md`

List fixed checkpoints, node IDs, expected time, outcomes, transitions, and completion conditions. Do not personalize this file.

### Material directories

- `course/student-materials/`: concise learner-facing material.
- `course/tutor-materials/`: detailed, source-aware teaching material.

## Required learner files

### `learner/learner-profile.md`

Record only useful learning context: role, tasks, prior knowledge, tools, transfer goal, time, depth preferences, language, fixed tutor mode, and tutor selection.

### `learner/personalized-route.md`

For each deviation from the standard route, use: node/checkpoint, `shortened|lengthened|remediation|candidate-skip`, reason, and implication.

### `learner/progress.csv`

Columns:

`checkpoint_id,node_id,status,confidence_basis,started_on,completed_on,route_delta,notes`

Allowed status:

- `planned`
- `in_progress`
- `mastered`
- `self_reported`
- `forced_skip`
- `needs_review`

Formal writes happen only at fixed checkpoint completion. The demo may contain a completed illustrative learner state.

### Other learner state

- `learner/callbacks.md`: unresolved misconceptions and later callback opportunities.
- `learner/checkpoint-notes.md`: cumulative micro-Cornell notes, at most one page per checkpoint.
- `learner/session-archive.md`: compact checkpoint summaries, never raw transcripts.

## Final outputs

- `outputs/personalized-cornell-notes.md`
- `outputs/personalized-mindmap.html`

The HTML must follow [mindmap-contract.md](mindmap-contract.md): a conventional
spatial map with a central course topic, checkpoint branches, knowledge topics,
and visible CSS connectors rather than a nested-list tree. It must be a single
offline file with embedded CSS and JavaScript, no CDN, remote font, external
image, analytics, or network request.

## Lifecycle validation

- `template`: required files and exact CSV headers exist.
- `compiled`: template passes; lifecycle is `approved`, `learning`, or `completed`; approval fields are set; sources, knowledge nodes, checkpoints, and dual-layer materials are populated.
- `final`: compiled passes; lifecycle is `completed`; every knowledge node has a progress row with a terminal status; final Cornell notes and offline mindmap exist.
