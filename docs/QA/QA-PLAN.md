<!-- autoqa:document:qa-plan -->
# QA Plan

<!-- autoqa:section:scope -->
## Scope

- Release or task: 三种导师追问风格（亲切、严格、幽默）。
- In scope: 风格定义、默认选择、学习者画像持久化、旧课程兼容、初始化与内嵌技能分发、文档说明、验证器约束。
- Out of scope and why: 不自动判定生成式导师的“幽默程度”或人类主观感受；这类判断保留给人工 E2E。不改变课程难度、知识路线、证据标准和 checkpoint 状态机。

<!-- autoqa:section:governance-sources -->
## Governance Sources

| Source | Sections used | QA consequence |
| --- | --- | --- |
| 用户需求（2026-07-30） | 严格、亲切默认、幽默三种行为 | 三种风格必须可区分，亲切必须为默认 |
| `quaestio-socratica/SKILL.md` | Hold the teaching contract | 风格不能破坏直接讲解、强制跳过和单步追问边界 |
| `quaestio-socratica/references/artifact-contracts.md` | Learner profile | 风格值需可持久化且保持旧课程兼容 |
| `quaestio-socratica/references/tutor-styles.md` | 全文 | 行为、安全边界与统一反馈流程的直接验收依据 |

<!-- autoqa:section:risk -->
## Risk Assessment

| Risk | Impact | Likelihood | Test response | Human decision needed |
| --- | --- | --- | --- | --- |
| starter、demo 与主技能版本漂移 | 高 | 中 | 字节级同步测试 | 否 |
| 非法风格值被静默接受 | 中 | 中 | 负向校验测试 | 否 |
| 旧课程因缺字段失效 | 高 | 中 | 缺字段默认 `friendly` 测试 | 否 |
| 严格变成羞辱或无休止追问 | 高 | 中 | 契约检查 + HUMAN-002/HUMAN-004 | 是 |
| 幽默掩盖纠错或嘲讽学习者 | 高 | 中 | 契约检查 + HUMAN-003/HUMAN-004 | 是 |
| 三种风格改变事实判断 | 高 | 低 | 固定不变量 + HUMAN-004 | 是 |

<!-- autoqa:section:best-practice -->
## Best-Practice Resolution

- Registry packs checked: AutoQA best-practice registry。
- Applicable current packs: 无 Active pack。
- Online research required: 否；本次是标准库 Markdown/字段校验和生成式行为契约，不涉及陌生框架、高风险协议或易变平台规则。
- Sources and date reviewed: AutoQA 内置测试设计参考，2026-07-30。
- Assumptions or unresolved uncertainty: 假设风格在首次教学节点前固定，并跨整个 course run 保持一致；生成式表达质量只能由人工体验确认。

<!-- autoqa:section:environments -->
## Environments and Test Data

- Automated environment: 本地 Python 3 标准库，临时目录内复制 starter 或运行初始化器。
- Human E2E environment: 任一支持本地 skill 的 Codex、Claude Code 或 Cursor 会话。
- Test-data creation and cleanup: `tempfile.TemporaryDirectory` 自动隔离与清理；不写入真实学习者数据。
- Time, randomness, and external-service controls: 测试不依赖网络、时间或随机输出。

<!-- autoqa:section:responsibilities -->
## Responsibilities

- Agent owns: 字段契约、验证器、初始化产物、分发同步、命令执行与结果解释。
- Human owns: 亲切感、严格但不羞辱、幽默但不冒犯、玩梗是否清楚且不妨碍学习。
- Approval required for: 人工 E2E 完成后的发布判断。

<!-- autoqa:section:gates -->
## Gate Plan

| Gate | Scope | Command or handoff | Exit condition |
| --- | --- | --- | --- |
| File smoke | 三份 `validate_course.py` | `python3 -m py_compile ...` | 全部可编译 |
| Module black box | learner profile 风格解析与模板初始化 | `python3 -m unittest discover -s tests -v` | 合法、非法、兼容和初始化用例通过 |
| Feature integration | starter、demo、内嵌技能一致性 | unittest + 两个生命周期校验命令 | 所有分发入口行为一致且有效 |
| Human E2E | 三种导师行为及共同边界 | `docs/QA/HUMAN-E2E.md` | HUMAN-001 至 HUMAN-004 全部通过 |

<!-- autoqa:section:exit-criteria -->
## Exit Criteria

- [x] Every changed executable file has a recorded smoke command.
- [x] Every module entry, exit, and applicable case class is covered.
- [x] Every named automated flow variant has current passing evidence.
- [ ] Human E2E is complete for a release claim.
- [x] No P0 or P1 defect remains open.
- [x] Residual P2/P3 defects and untested risks are visible.

