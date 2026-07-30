<!-- autoqa:document:qa-matrix -->
# QA Matrix

<!-- autoqa:section:requirements -->
## Requirement Traceability

| Requirement ID | Business rule or risk | Source | Module cases | Integration flows | Human checks | Status |
| --- | --- | --- | --- | --- | --- | --- |
| REQ-STYLE-001 | 提供 `friendly`、`strict`、`humorous`，并以 `friendly` 为默认 | 用户需求；`tutor-styles.md` | CASE-001, CASE-002, CASE-007 | FLOW-001 | HUMAN-001 | 自动化通过，人工待验 |
| REQ-STYLE-002 | 严格风格明确处理所有发现的推理缺口但不越过教学边界 | `tutor-styles.md#strict-strict` | CASE-004 | FLOW-003 | HUMAN-002, HUMAN-004 | 契约就绪，人工待验 |
| REQ-STYLE-003 | 幽默风格可吐槽错误观点、接梗非标准正确表达，但不嘲讽学习者或替代纠错 | `tutor-styles.md#humorous-humorous` | CASE-004 | FLOW-003 | HUMAN-003, HUMAN-004 | 契约就绪，人工待验 |
| REQ-STYLE-004 | 风格持久化到学习者画像；非法值拒绝；旧课程缺字段按 `friendly` 兼容 | `artifact-contracts.md` | CASE-001, CASE-002, CASE-003 | FLOW-001, FLOW-002 | HUMAN-001 | 通过 |
| REQ-STYLE-005 | 主技能、starter、demo 与新初始化课程包含同一运行时契约 | 分发结构 | CASE-005, CASE-006 | FLOW-001, FLOW-002 | 无 | 通过 |

<!-- autoqa:section:file-gates -->
## File Gates

| File | Kind | Narrow check | Covering command | Evidence |
| --- | --- | --- | --- | --- |
| `quaestio-socratica/scripts/validate_course.py` | executable | Python compile + business tests | CMD-TEST | 当前通过 |
| `starter-course/.agents/skills/quaestio-socratica/scripts/validate_course.py` | executable | Python compile + sync test | CMD-SMOKE | 当前通过 |
| `demo/reliable-ai-workflows/.agents/skills/quaestio-socratica/scripts/validate_course.py` | executable | Python compile + sync test | CMD-SMOKE | 当前通过 |
| Markdown、模板与 README 变更 | declarative | 消费端验证、同步测试与人工 E2E | CMD-TEST, CMD-STARTER, CMD-DEMO | 自动化通过；体验待验 |

<!-- autoqa:section:module-boundaries -->
## Module Boundaries

| Module | Entries | Exits | Applicable classes | Cases | Exemptions |
| --- | --- | --- | --- | --- | --- |
| `profile-style-validation` 风格画像校验 | `learner/learner-profile.md` | 标准化风格值或错误列表 | happy, negative, boundary | CASE-001, CASE-002, CASE-003 | 无状态、权限、并发与恢复行为 |
| `runtime-distribution` 课程初始化与分发 | 初始化 API；三份内嵌技能 | 新课程目录；一致运行时文件 | happy | CASE-005, CASE-006 | 无外部依赖与并发 |
| `generative-tutor-behavior` 生成式导师行为契约 | 学习者选择与回答 | 风格化反馈、诊断、一个主追问 | happy, boundary | CASE-007, CASE-004 | 自动化只验证契约存在；表达质量交由人工 E2E |

<!-- autoqa:section:business-flows -->
## Business Flows

| Flow ID | Variant | Given | When | Expected business outcome | Command | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| FLOW-001 | happy | 空课程初始化 | 初始化 self 课程 | 画像默认 friendly 且内嵌风格规则 | CMD-TEST | 通过 |
| FLOW-002 | failure/compatibility | 非法值或旧画像缺字段 | 运行 template 校验 | 非法值被拒绝；缺字段按 friendly 兼容 | CMD-TEST | 通过 |
| FLOW-003 | alternate human behavior | 同一课程选择三种风格 | 分别回答错误、含糊、正确但非标准内容 | 判断标准一致，表达与追问符合所选风格 | HUMAN-002 至 004 | 待人工 |
| FLOW-004 | regression | starter 与 approved demo | 运行生命周期校验 | 两者继续通过 | CMD-STARTER, CMD-DEMO | 通过 |

<!-- autoqa:section:fault-sensitivity -->
## Fault-Sensitivity Proof

| Critical rule | Challenge used | Expected failure observed | Restore-and-pass evidence |
| --- | --- | --- | --- |
| 只允许三种显式风格 | 临时课程画像写入 `sarcastic` | 校验器返回 `invalid Fixed tutor style` | 同一测试套件中的三种合法值与 starter 校验通过 |
| 分发副本不得漂移 | 字节级比较七个核心运行时文件 | 任一副本不同会触发 unittest diff | 当前两份副本全部通过 |

<!-- autoqa:section:residual-risk -->
## Residual Risk

| Risk or gap | Reason | Severity | Owner | Decision |
| --- | --- | --- | --- | --- |
| 生成式幽默可能因模型、语言和上下文波动 | 无法完全确定性自动判定 | P2 | Human | 完成 HUMAN-003/HUMAN-004 后再作发布判断 |
| 严格风格的主观压力感 | 个体感受差异 | P2 | Human | 完成 HUMAN-002 并记录体验 |
