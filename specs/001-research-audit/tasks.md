# Tasks: 可审计基金研究报告

## Phase 1: Setup

- [x] T001 [P] 设计 `tests/test_audit.py` 的四类数据状态测试
- [x] T002 [P] 明确审计报告字段和 JSON 序列化边界

## Phase 2: Foundational

- [x] T003 实现 `src/jushi_fund_research/audit.py` 的数据审计摘要
- [x] T004 实现回测研究决策摘要

## Phase 3: User Story 1 - 数据证据 (P1)

- [x] T005 [US1] 为主源、备用源、缓存和不足状态生成覆盖范围与尝试摘要
- [x] T006 [US1] 增加无效点、重复日期和空来源测试

## Phase 4: User Story 2 - 研究决策 (P1)

- [x] T007 [US2] 将回测状态、样本边界、回撤和风险提示转为结构化报告
- [x] T008 [US2] 测试足够样本与 `insufficient_sample` 的决策差异

## Phase 5: User Story 3 - 上层消费 (P2)

- [x] T009 [US3] 提供稳定的 `to_dict` / JSON 可序列化输出
- [x] T010 [US3] 更新 `docs/research-audit.md` 和项目元信息中的可审计研究说明

## Phase 6: Polish

- [x] T011 [P] 运行完整 unittest 和 diff 检查
- [x] T012 [P] 生成收敛报告，记录未接入真实外部 API 的边界
