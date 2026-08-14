<div align="center">

[中文](README.md) · [English](README_EN.md)

# QUAESTIO SOCRATICA

## The knowledge you discover is the knowledge you remember

**Turn any course into an exploration driven by questions.**

<br>

> Ask without taking the answer away. Teach without thinking in your place.<br>
> Learning is not receiving a finished product; it is watching an idea take shape in your own mind.

</div>

---

## It does not rush to give you the answer

Ordinary AI tutoring often feels like a talking encyclopedia: you ask, it explains. The explanation may be excellent, yet the understanding still belongs to the model.

Quaestio Socratica works differently.

> **Tutor:** If a polished AI answer cannot be reproduced tomorrow, is the missing piece really a longer prompt?<br>
> **You:** Perhaps what is missing is a defined process…<br>
> **Tutor:** Then which decisions belong to the model, and which belong to rules or people?

One question leads to another. You form a hypothesis, meet a counterexample, revise a boundary, and connect scattered ideas into your own structure. The tutor will not trap you in endless guessing: when you are stuck, it rephrases, hints, breaks the problem down, and finally explains directly.

This is bounded Socratic learning.

## Why active learning is more enjoyable

Because the next step is not another page—it is a discovery. A surprising case overturns your first intuition, a well-placed question opens a new branch, and a real task suddenly connects with an abstract idea. You are not carried through a table of contents; you leave your own path through a world of knowledge.

## Open a course and enter a world of ideas

<table>
<tr>
<td width="33%" valign="top">

### Discover actively

New knowledge appears through questions and tensions. You do not merely memorize a conclusion; you retrace the path by which it becomes necessary.

</td>
<td width="33%" valign="top">

### Let the route adapt

The course remembers what you know, where you struggle, and what you actually want to do. The standard route stays stable; your personal route changes.

</td>
<td width="33%" valign="top">

### Always find your way back

Roughly every two hours, you reach a checkpoint—a save point for completed ideas, open questions, and the next part of the journey.

</td>
</tr>
</table>

## Your tutor can be rigorous—or full of story

Choose one of three experiences:

- **Course mentor:** one original tutor whose manner fits the discipline. A mathematics tutor probes assumptions; a philosophy tutor searches for definitions and counterexamples; a management tutor tests incentives and tradeoffs.
- **Immersive exploration:** enter an original world with one to three tutors. Solve a mystery, conduct an investigation, or pursue a shared intellectual mission—something closer to a responsive *Sophie's World*.
- **Affinity tutor mode:** after explicit adult opt-in, join an otome-inspired course story with one to three original adult tutors. Each tutor has zero to three hearts; an optional post-checkpoint choice can add one heart to one tutor, and course completion may offer ensemble, friendship, or eligible light-romance endings.

Course-mentor and immersive modes contain no romance progression. Affinity mode permits light, non-sexual flirting and optional romance, but hearts never come from correct answers, study time, streaks, compliance, payment, or forced disclosure. Declining a relationship choice, pausing, or skipping a node never removes affinity or reduces teaching quality.

Whichever experience you choose, you can also decide how the tutor follows up:

- **Friendly (default):** encouraging, patient, and gently guided—the original default manner.
- **Strict:** separates claims, assumptions, evidence, and conclusions, and does not overlook vague terms, hidden conditions, or accidentally correct reasoning.
- **Humorous:** gives a good-natured tease to a wrong answer, or meets a conceptually correct but nonstandard answer with a light joke before translating it into standard terminology.

These styles change tone and follow-up pressure, not the factual standard. Strict never means humiliating the learner, and humorous never makes the learner the target. When you are stuck, every style still moves through rephrasing, hints, decomposition, and direct explanation.

## Begin in three steps

### 1. Copy an empty classroom

Copy the [`starter-course`](starter-course/) folder and rename it for your course.

### 2. Bring materials—or only a question

PPT, PDF, notes, code, lecture material, CSV, and webpages are all welcome. The material may be incomplete or wrong. You may also begin with nothing but a learning goal.

### 3. Speak inside the agent you already use

Open the whole course folder in Codex, Claude Code, or Cursor, then say:

> Use the local Quaestio Socratica skill to build and begin this course with me.

Or begin in Chinese:

> 使用这个文件夹里的 Quaestio Socratica skill，帮我建立并开始这门课程。

You do not need to program or run setup commands. The first conversation establishes:

- whether a teacher is authoring the course or a learner is building it personally;
- what you already know and what you want to accomplish in work or research;
- the desired depth of theory, mathematics, code, and practice;
- course-mentor, immersive, or adult opt-in affinity mode;
- a friendly, strict, or humorous questioning style.

The AI compiles the complete route first. Formal learning begins only after you explicitly approve it.

## You can always say, “I understand”

Non-core material can be skipped immediately. For a core idea, explain it briefly in your own words; reasonable understanding is enough to continue.

If you still insist on skipping, the tutor gives one honest warning, records the choice, and lets you move on. A good learning system supports motivation; it does not pretend to manufacture it.

## Finish with a map that is truly yours

Before the course closes, the system asks whether you want Chinese, English, or bilingual outputs. It then creates:

- concise personalized Cornell notes—not a textbook summary, but your conceptual thread, corrected misconceptions, transfer contexts, and next steps;
- a foldable HTML mindmap, with the course at the center, checkpoints as main branches, and knowledge nodes, prerequisites, and personal learning status visible at a glance.

## What can it teach?

Any subject that can form a knowledge structure, a chain of questions, and useful practice:

`Mathematics` · `Philosophy` · `Computer Science` · `AI` · `Economics` · `Law` · `Languages` · `History` · `Engineering` · `Management`

The same method can serve undergraduate, master's, PhD, EMBA, and DBA learners, as well as managers, domain experts, and lifelong learners. Depth, examples, and evidence change with the audience; the teaching core remains stable.

## Try a prepared course

[`From Prompts to Reliable AI Workflows`](demo/reliable-ai-workflows/) is an approved two-checkpoint demo. Open it in your agent and say, “Begin this demo course.”

## Questions about PDF, privacy, sources, or switching agents?

Those details should not interrupt your first learning experience. Read the [technical and usage FAQ](docs/FAQ_EN.md) when you need them.

## License

The Python scripts (`quaestio-socratica/scripts/` and the script copies embedded in each course) are licensed under [MIT](LICENSE-MIT). Everything else—the skill instructions, references, course template, starter course, demo course, and documentation—is licensed under [CC BY 4.0](LICENSE-CC-BY-4.0). Keep the attribution when you copy, adapt, or distribute your courses.

---

<div align="center">

Inspired by the Socratic learning tradition and [Socratopia](https://www.socratopia.app/zh).

### Sapere aude.

**Let the answer grow in your mind. Let the world of knowledge unfold beneath your feet.**

</div>
