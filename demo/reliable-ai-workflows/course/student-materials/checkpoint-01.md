# CP01 · 从一个好回答到一条工作流

## 先分清三个东西

- **Prompt**：一次模型调用中的任务说明和上下文。
- **Workflow**：人、模型和工具按照预先设计的路径协作；关键节点可以设置程序化 gate。
- **Agent**：模型能在边界内动态决定下一步和工具使用。

这条边界是设计问题，不是营销名词。Anthropic 的官方工程文章明确区分预定义路径的 workflow 与由模型动态控制过程的 agent，并建议从最简单的方案开始，仅在有证据时增加复杂度。[来源：Anthropic，检索于 2026-07-26](https://www.anthropic.com/engineering/building-effective-agents)

## Prompt 为什么不等于 workflow

一个漂亮答案可能仍然无法重复，因为它没有明确：

1. 什么输入可以进入；
2. 成功是什么；
3. 哪些失败必须拒绝；
4. 哪一步可以使用概率判断；
5. 哪一步必须用代码、规则或人来确认；
6. 出错后停在哪里。

先写 **outcome contract**：

> 对于哪些输入，在什么限制下，产生什么可观察结果；哪些情况必须拒绝、升级或保留不确定性。

## 最小工作流骨架

`输入检查 → 任务拆分/路由 → 模型处理 → gate → 人工批准或写入结果 → 记录`

Prompt chaining 适合能被清晰拆分的固定子任务，routing 适合输入类别有显著差异的任务。两者都不是“步骤越多越高级”。[来源：Anthropic，检索于 2026-07-26](https://www.anthropic.com/engineering/building-effective-agents)

## Gate 的三种典型归属

- **代码**：格式、范围、必填字段、权限、重复写入。
- **模型**：需要语义判断、允许一定不确定性、后续仍有复核。
- **人**：价值判断、不可逆动作、显著财务/法律/声誉后果。

当前 OWASP guidance 建议对高风险操作保留 human approval，并隔离外部不可信内容；具体安全分类会演化，因此这里保留日期。[来源：OWASP LLM01:2025，检索于 2026-07-26](https://genai.owasp.org/llmrisk/llm01-prompt-injection/)

## CP01 练习

选择一项你做过的 AI 任务，写出：

- 一句话 outcome contract；
- 3–5 个步骤；
- 至少一个程序 gate；
- 至少一个需要人的决定，或说明为什么不需要；
- 一个明确的停止条件。
