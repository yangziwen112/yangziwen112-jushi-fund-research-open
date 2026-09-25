# Jushi Fund Research Open

一个面向场外基金研究的、可审计的 Python 参考实现。项目把“数据从哪里来、数据是否可信、主源失效后如何降级、策略是否经过样本外验证”拆成可以运行和测试的模块。

> 本项目是“聚势”基金投研与持仓管理平台的开源 companion project，不包含用户持仓、截图、账号凭证或 API 密钥；不提供买卖指令，也不承诺投资收益。

## 项目解决什么问题

基金应用中，真正容易出错的往往不是画一张收益曲线，而是把盘中估值误当成正式净值、把披露期重仓误当成实时持仓、在数据接口失败后悄悄填入演示数据，或用一组很小的样本包装成策略结论。

本项目用一条可追踪链路处理这些问题：

```text
数据适配器 → 字段校验与日期去重 → 主源 → 备用源 → 本地缓存 → 数据不足
                                      ↓
                         正式净值研究 / MA20 / 60%训练-40%测试
```

## 当前实现

- `data_policy`：将上游字段统一为日期和单位净值，过滤非法值，记录数据源和尝试状态。
- `nav_chain`：按声明顺序调用数据源；主源失败后才进入备用源，再失败才使用经过校验的本地缓存，不生成伪造数据。
- `strategy`：实现无未来数据的 MA20 长仓/现金规则，以及 60% 训练、40% 测试的简单样本外回测；样本不足时拒绝输出统计结论。
- `tests`：覆盖字段校验、重复日期、主源失败、备用源、缓存降级和训练/测试边界。

这些模块使用 Python 标准库，方便替换为 FastAPI、SQLite 或具体数据供应商适配器。真实接口适配器应放在项目外层，并保留请求时间、来源、覆盖日期、返回行数和失败原因。

## 数据来源与边界

项目参考并记录了以下公开数据链路：

1. 天天基金移动端历史净值接口：用于分页获取正式历史净值；字段、分页和可用性需要在接入时再次校验。
2. 天天基金盘中估值接口：只作为盘中参考，不替代收盘后的正式净值，尤其不能直接替代 QDII 或跨市场基金的结算结果。
3. Eastmoney `pingzhongdata/{code}.js`：作为历史净值备用来源，结果必须标记为 `fallback` 并重新校验日期和数量。
4. AkShare 对公开基金目录和披露期重仓数据的适配：重仓数据只能说明报告期披露内容，不能包装成实时持仓。

完整来源、字段说明和许可证边界见 [SOURCES.md](SOURCES.md) 与 [NOTICE.md](NOTICE.md)。

## 运行测试

```powershell
cd fund-research-open
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
```

如果 Windows 上的 `python` 指向了不完整的环境，可使用已安装的完整 Python 解释器运行同一命令。

## 开源致谢

项目的来源分层、基金名称检索和实时估值研究参考了 [hzm0321/real-time-fund](https://github.com/hzm0321/real-time-fund)；基金研究和回测边界参考了 [daggerFS/xalpha](https://github.com/daggerFS/xalpha)；公开金融数据适配参考了 [akfamily/akshare](https://github.com/akfamily/akshare)；状态流和失败分支的工程思路参考了 [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph)。

本仓库没有复制这些项目的源代码或数据文件，具体致谢和许可证说明见 [NOTICE.md](NOTICE.md)。

## 简历中可使用的描述

**Jushi Fund Research Open｜基金数据与策略验证开源参考实现**

独立设计并开源基金数据质量与策略验证链路，围绕正式净值、盘中估值、备用源和本地缓存建立可审计的降级机制；实现字段校验、日期去重、MA20 信号和 60/40 样本外回测，并在 README 与 NOTICE 中明确数据来源、算法边界和上游项目致谢。
