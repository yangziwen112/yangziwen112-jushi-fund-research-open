# Notice and Acknowledgements

## 本项目代码

远端仓库预置的 [LICENSE](LICENSE) 为 CC0 1.0 Universal。本项目新增代码同时保留 [LICENSE-MIT](LICENSE-MIT) 作为明确的 MIT 许可文本；使用者应以具体文件和上游项目的许可证为准。

许可证不覆盖外部数据服务、第三方项目代码、商标或数据服务条款。

## 参考项目与贡献边界

| 项目 | 参考内容 | 本项目的处理方式 |
|---|---|---|
| [hzm0321/real-time-fund](https://github.com/hzm0321/real-time-fund) | 基金名称检索、盘中估值和历史净值备用方向 | 重新设计为来源声明、字段校验和可追踪降级链，不复制其代码 |
| [daggerFS/xalpha](https://github.com/daggerFS/xalpha) | 场外基金研究、费用和定投回测视角 | 只参考研究边界，重新实现最小样本外验证模块 |
| [akfamily/akshare](https://github.com/akfamily/akshare) | 公开金融数据接口适配思路 | 通过外部适配器使用，不复制其实现 |
| [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph) | 显式状态、流程分支和失败处理思路 | 仅借鉴工作流设计思想，本仓库核心模块不依赖它 |

上游项目的作者、版权和许可证归各自权利人所有。本仓库未 vendoring 上游源代码，也没有把公开披露重仓包装为实时持仓。

## 数据服务说明

历史净值、盘中估值、基金目录和披露期重仓数据来自公开服务或其适配器。数据的可用性、时效性、字段含义和访问限制由数据提供方决定；本项目不保证接口持续可用，也不构成投资建议。

## 使用者责任

使用者应分别阅读上游项目许可证、数据服务条款和适用法律法规。运行真实适配器时，应自行处理请求频率、商业使用权限、隐私保护和结果复核。
