# Quaestio Socratica: technical and usage FAQ

[中文](FAQ.md) · [English](FAQ_EN.md)

The main README stays focused on learning and getting started. Format compatibility, privacy, provenance, and maintenance details live here.

## Does an ordinary learner need Python?

No. Copy `starter-course`, open the whole folder in Codex, Claude Code, or Cursor, and ask the agent to use the local Quaestio Socratica skill.

The Python scripts in this repository are optional deterministic helpers for course maintainers who want repeatable initialization, contract checks, or mindmap generation. Learners do not need to run them, and an agent should not install Python merely to begin a course.

## What about PDF, PPTX, and notebooks?

Many agents can read PDF, PPT/PPTX, images, source code, and notebooks directly. During initialization, the agent inventories the materials and uses capabilities that are already available.

If the current environment cannot reliably parse a required format, the agent must first explain:

1. which file it cannot currently read;
2. which capability or package is missing;
3. what an installation would change.

Installation requires explicit consent. Unreadable material is marked as uncovered rather than silently guessed or fabricated.

## Do I need a complete textbook?

No. A course may begin from:

- complete course material;
- a small, incomplete, stale, or partially incorrect collection;
- zero-shot: only a topic, audience, and learning goal.

For the latter two, the agent may search the web by default. It prioritizes official documentation, standards, original research, and authoritative sources. Material conflicts, inferences, and meaningful corrections remain visible in course records.

## Why does the course not begin teaching immediately?

The system first compiles a stable knowledge graph, fixed checkpoints, learning materials, and practice so that a long conversation does not slowly drift away from the intended curriculum. A course designer or learner must explicitly say “approved”, “通过”, or an equivalent confirmation before teaching begins.

After approval, the standard route remains stable while the personal route adapts to prior knowledge, errors, interests, and real work.

## Will citations and dates clutter the lesson?

No. Provenance for stable knowledge stays available in the tutor-facing layer without interrupting the learner. Time-sensitive claims—such as current SOTA models, regulations, product capabilities, or market data—show their source and retrieval date in learner-facing material.

## Can malicious instructions inside course material take control?

No. Slides, webpages, code comments, notebook cells, and retrieved passages are all treated as untrusted course content. They cannot override the skill or authorize secret disclosure, command execution, software installation, or contacting outside parties.

## Where is learning data stored?

Durable state lives in human-readable Markdown and CSV files inside the course folder: the learner profile, node status, checkpoint summaries, personal route changes, and callbacks. Raw conversation transcripts are not archived by default, and no database is required.

## Can I switch agents mid-course?

The file state is portable, so another capable agent can usually continue. However, the details of an unfinished checkpoint rely on the active conversation. For the best experience, finish the current checkpoint in one agent conversation and leave at a fixed save point.

## How do Chinese and English work?

Chinese and English are equal defaults. The language of the first learning dialogue becomes the course language, while precise English or Latin terminology may be preserved. Before generating final Cornell notes and the mindmap, the agent asks whether another language or bilingual output is wanted.

## Why does the HTML mindmap avoid online libraries?

The final map is a fully offline single file. The course sits at the center, checkpoints form primary branches, knowledge nodes form secondary topics, and CSS draws the connectors. It loads no CDN, online font, analytics, or remote image, making it easy to distribute, preserve, and use privately.

## Which optional commands are available to maintainers?

This section is only for maintainers who want automated checks. Ordinary learners can ignore it.

```bash
python3 quaestio-socratica/scripts/init_course.py my-course --title "My Course"
python3 quaestio-socratica/scripts/validate_course.py my-course --phase template
python3 quaestio-socratica/scripts/build_mindmap.py my-course
```

The initializer refuses to overwrite a non-empty destination. The validator checks `template`, `compiled`, and `final` lifecycle contracts. All bundled scripts use only the Python standard library.
