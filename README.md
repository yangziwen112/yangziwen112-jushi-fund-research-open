# Jushi Fund Research Open

一个面向场外基金研究的可审计 Python 参考实现。项目将数据来源、字段校验、降级机制和策略验证拆成可运行、可测试的模块。

> 本项目是“聚势”基金投研与持仓管理平台的开源 companion project，不包含用户持仓、截图、账号凭证或 API 密钥；不提供买卖指令，也不承诺投资收益。

## 核心链路

```text
数据适配器 → 字段校验与日期去重 → 主源 → 备用源 → 本地缓存 → 数据不足
                                      ↓
                         正式净值研究 / MA20 / 60%训练-40%测试
```

## 当前实现

- `data_policy`：统一日期和单位净值字段，过滤非法值并记录数据源状态。
- `nav_chain`：按声明顺序调用数据源；主源失败后进入备用源，再失败才使用校验过的本地缓存，不生成伪造数据。
- `strategy`：实现无未来数据的 MA20 长仓/现金规则，以及 60% 训练、40% 测试的样本外回测；样本不足时拒绝输出统计结论。
- `tests`：覆盖字段校验、日期去重、主源失败、备用源、缓存降级和训练/测试边界。

## 数据来源与边界

项目记录并参考以下公开数据链路：

1. 天天基金移动端历史净值接口：用于分页获取正式历史净值，接入时需要重新校验字段和可用性。
2. 天天基金盘中估值接口：只作为盘中参考，不能替代收盘后的正式净值。
3. Eastmoney `pingzhongdata/{code}.js`：作为历史净值备用方向，结果必须标记为 `fallback` 并重新校验。
4. AkShare 公开基金目录与披露期重仓数据：重仓数据只能描述报告期内容，不能包装成实时持仓。

完整来源、字段说明和许可证边界见 [SOURCES.md](SOURCES.md) 与 [NOTICE.md](NOTICE.md)。

## 运行测试

```powershell
cd fund-research-open
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
```

## 开源致谢

项目参考了 [hzm0321/real-time-fund](https://github.com/hzm0321/real-time-fund)、[daggerFS/xalpha](https://github.com/daggerFS/xalpha)、[akfamily/akshare](https://github.com/akfamily/akshare) 和 [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph)。本仓库未复制这些项目的源代码或数据文件，具体边界见 [NOTICE.md](NOTICE.md)。

仓库根目录的 `LICENSE` 为远端仓库预置的 CC0 1.0；本项目保留 [LICENSE-MIT](LICENSE-MIT) 作为新增代码的 MIT 许可文本。

## 简历描述

**Jushi Fund Research Open｜基金数据与策略验证开源参考实现**

独立设计基金数据质量与策略验证链路，区分正式净值、盘中估值、备用源和本地缓存；实现数据校验、MA20 信号与 60/40 样本外回测，并在文档中明确数据来源、算法边界和上游项目致谢。
