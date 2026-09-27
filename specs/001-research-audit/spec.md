# Feature Specification: 可审计基金研究报告

**Feature Branch**: `001-research-audit`
**Created**: 2026-09-27
**Status**: Draft
**Input**: 将基金项目从“有几个数据校验函数”提升为“能交付一份带证据、边界和决策状态的研究结果”。

## User Scenarios & Testing

### User Story 1 - 判断数据能否支持研究 (Priority: P1)

研究者拿到一批基金净值后，可以看到选中的来源、有效行数、日期覆盖范围、降级过程和数据是否足以支持研究。

**Independent Test**: 主源成功、备用源接管、仅缓存可用、全部不足四类输入均生成不同且可序列化的审计结果。

### User Story 2 - 判断策略结果是否可采信 (Priority: P1)

研究者查看回测结果时，同时看到训练/测试边界、样本量、基线、风险提示和“仅研究/样本不足”决策，不再只看到一个收益数字。

**Independent Test**: 对足够样本和不足样本分别生成 `research_only` 与 `insufficient_data` 决策。

### User Story 3 - 让 Agent 或前端安全消费 (Priority: P2)

上层应用可以消费稳定的字典结构，按状态展示结果，而不需要解析自然语言或猜测数据来源。

**Independent Test**: 审计报告可通过 JSON 序列化，字段只包含研究所需的来源、覆盖、指标和限制。

## Edge Cases

- 多个来源成功但日期覆盖不一致时，报告必须保留被选来源和覆盖范围。
- 所有来源失败且无缓存时，决策必须拒绝研究，不返回收益结论。
- 回测状态为 `insufficient_sample` 时，策略收益、回撤和决策理由必须保持空/拒绝状态。
- 日期只有一条或有重复日期时，覆盖范围基于标准化后的有效点计算。

## Requirements

- **FR-001**: 系统 MUST 为 `NavChainResult` 提供可序列化的数据审计摘要。
- **FR-002**: 数据审计摘要 MUST 包含状态、选中来源、有效行数、起止日期和尝试记录摘要。
- **FR-003**: 系统 MUST 为回测结果提供研究决策摘要，区分 `research_only` 和 `insufficient_data`。
- **FR-004**: 研究决策 MUST 包含训练行数、测试行数、基线回撤、策略回撤和风险限制。
- **FR-005**: 审计摘要 MUST 不声称预测收益、不执行交易、不伪造缺失数据。
- **FR-006**: 现有公开 API（函数参数和核心字段）保持兼容。

## Success Criteria

- **SC-001**: 四类数据源状态都有自动化测试。
- **SC-002**: 足够样本与不足样本的研究决策可以被上层直接区分。
- **SC-003**: JSON 序列化不丢失状态、日期覆盖和风险边界。
- **SC-004**: 原有 9 项测试继续通过。

## Assumptions

- 本次不接入新的基金供应商，不把实时 API 假设写成已可用事实。
- 审计模块只整理当前代码已有的 `NavChainResult` 和 `BacktestResult`。
- 结果用于研究工程展示，不构成投资建议。
