# Tutor packet · CP02

## Teaching intent

Turn the CP01 diagram into a system that can face stale information, hostile content, permissions, repeated runs, and measurable failure.

Sources: `S01`, `S02`, `S03`, `S04`, `S05`.

## N05 · Grounding, tools, and memory

**Essence:** Add an augmentation only to reduce a named uncertainty or enable an indispensable effect.

**Opening cases**

1. Summarize a supplied policy: context may suffice.
2. Answer current inventory: retrieval/tool required.
3. Draft then translate: fixed chain.
4. Investigate an unfamiliar production incident: possibly agentic, but only with bounded tools and ground truth.

Ask the learner to reject one unnecessary augmentation. This tests restraint, not vocabulary.

## N06 · Failure modes and least privilege

**Essence:** Autonomy makes small errors and hostile inputs compound. Permissions determine blast radius.

**Threat model prompts**

- What can the workflow read?
- What can it write or send?
- What external content can influence it?
- Which action is irreversible?
- Where can a human stop it?

**Key distinction:** Instruction filtering is not a complete cure. Segregation, least privilege, validation, and approval reduce impact. Keep `S04` learner-visible because security guidance changes.

**Acceptable evidence:** Remove one permission, add one trust boundary, and preserve the intended business outcome.

## N07 · Evaluate outcomes

**Essence:** A good eval defines a task, representative inputs, grading logic, and an outcome. A fluent trace can still end in the wrong state.

**Question path**

1. “如果模型自己说完成了，你信吗？”
2. “你能在环境中检查什么？”
3. “哪三个输入最容易暴露设计错误？”
4. “哪些检查适合代码、模型或人？”

**Minimum set**

- one normal case;
- one boundary/ambiguous case;
- one refusal or failure case;
- an observable oracle for each.

Do not require an API or formal eval platform. A CSV table can be enough.

## N08 · Reliable workflow canvas

Use the nine-part canvas in learner material. The learner should bring a real task.

**Challenge questions**

- What complexity did you deliberately omit?
- Which claim is time-sensitive?
- What happens when a source contains instructions?
- What proves the outcome exists?
- What is the stop condition?

**Completion evidence:** The canvas has outcome, inputs, steps, gates, permissions, evals, failure handling, and stopping conditions. It need not be production code.

## Closing

At checkpoint completion, update the learner files. Before final notes, ask whether additional language versions are wanted. Do not claim the learner built a secure production system; the achievement is a reasoned design.
