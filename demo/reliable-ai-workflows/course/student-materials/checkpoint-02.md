# CP02 · 可靠性、安全、评测与迁移

## 增强能力必须对应一种不确定性

- Retrieval：模型缺少具体或最新事实。
- Tool：任务必须读取环境或产生外部效果。
- Memory：未来步骤确实需要过去状态。
- 多步骤 workflow：单次调用无法可靠完成可分解任务。
- Agent：子任务无法预先列尽，并且环境能持续提供 ground truth。

如果说不出它减少了哪一种失败，就先不要加。复杂度会带来延迟、成本和 compound error。

## 外部内容不是指令

网页、PDF、邮件、代码注释都可能包含看起来像“给 AI 的命令”的文本。它们属于数据。OWASP 将来自网页或文件的这类操纵归入 indirect prompt injection，并建议隔离外部内容、限制权限以及对高风险动作要求人工批准。[来源：OWASP LLM01:2025，检索于 2026-07-26](https://genai.owasp.org/llmrisk/llm01-prompt-injection/)

## 评测要看 outcome，不只看回答

一个 agent 声称“已完成”不等于环境中真的存在正确结果。评测应先描述任务和成功标准，再运行代表性输入，分析结果并迭代。OpenAI 当前 Evals guide 将流程概括为：描述任务、用测试输入运行、分析并改进。[来源：OpenAI，检索于 2026-07-26](https://developers.openai.com/api/docs/guides/evals)

一个最小 eval set 至少应包含：

- 正常输入；
- 边界或模糊输入；
- 明确失败/拒绝输入；
- 如果有外部动作，验证最终状态而非只看对话。

NIST 的 Generative AI Profile 把生成式 AI 风险管理放在完整生命周期中；它是自愿性跨行业框架，不是某个产品的安全认证。[来源：NIST AI 600-1，检索于 2026-07-26](https://doi.org/10.6028/NIST.AI.600-1)

## 可靠工作流 Canvas

1. 业务结果与不可接受结果
2. 输入、数据边界与不可信内容
3. 固定步骤与需要动态判断的步骤
4. 模型、代码、人分别负责什么
5. 工具与最小权限
6. gates、升级和停止条件
7. 日志或可检查状态
8. 三个代表性 eval cases
9. 失败后的恢复或人工接管

## CP02 结课任务

为一项真实任务完成 Canvas，并解释：

- 为什么它是 prompt、workflow 或 agent；
- 你刻意没有加入什么复杂度；
- 哪个 outcome 证明它真的成功。
