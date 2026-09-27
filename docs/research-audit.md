# Research Audit Contract

聚势研究层现在可以把一批净值和一次样本外回测整理成机器可读的研究审计报告：

```python
from jushi_fund_research.audit import build_research_audit

report = build_research_audit(nav_result, backtest_result)
```

报告包含数据状态、选中来源、有效点数量、日期覆盖范围、降级尝试摘要、训练/测试边界、策略与基线指标，以及 `research_only` 或 `insufficient_data` 决策。

审计模块不会请求网络、调整策略参数或创建收益结论。它的价值是让上层 API、Agent 和前端消费结构化证据，而不是从一段自然语言中猜测数据质量。
