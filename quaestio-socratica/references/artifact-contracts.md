# Artifact contracts

Use UTF-8. Keep state human-readable and editable. Prefer Markdown for narrative and CSV for repeated records.

## Required course files

### `course/course-status.md`

Use these labeled fields:

- `Lifecycle`: `draft`, `compiling`, `awaiting_approval`, `approved`, `learning`, or `completed`
- `Initialization mode`: `undecided` before the first dialogue, then `teacher` or `self`
- `Course title`
- `Course version`
- `Tutor mode`: `unselected`, `course-mentor`, `immersive`, or `affinity`
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

Record only useful learning context: role, tasks, prior knowledge, tools, transfer goal, time, depth preferences, language, fixed tutor mode, tutor selection, fixed questioning style, and affinity adult opt-in.

Use `Fixed tutor style`: `friendly`, `strict`, or `humorous`. `friendly` is the default. When reading an older learner profile without this field, treat it as `friendly` and add the field at the next safe profile update.

Use `Affinity adult opt-in`: `yes` or `no`. Default to `no`. `yes` confirms only that the learner states they are at least 18 and opts in; never record their exact age or identity document.

### `learner/affinity.csv`

Columns:

`tutor_id,tutor_name,affinity,route_stage,last_checkpoint,notes`

- New templates include the header, but older non-affinity workspaces may omit the file.
- In `affinity` mode, require exactly one to three unique tutors and adult opt-in `yes`.
- Tutor IDs use `T01`, `T02`, and `T03`.
- `affinity` is an integer from 0 to 3 and maps exactly to `route_stage`: `0=acquaintance`, `1=trust`, `2=fondness`, `3=route-ready`.
- `last_checkpoint` is blank before the first increase, then a checkpoint ID such as `CP01`.
- Outside affinity mode the file stays empty. Do not preserve dormant romantic state in another mode.
- Formal writes happen only at fixed checkpoint completion. Notes stay brief and never contain raw dialogue or sensitive disclosure.

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
