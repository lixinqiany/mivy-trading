# Mivy Contracts

为 Mivy Trading 各服务和共享库定义统一的数据结构与接口协议，保持跨模块的语义一致。

- 约定公共业务枚举及其代码含义。
- 定义共享数据库模型、字段和关联关系。
- 提供通用接口协议，供 SDK 和业务模块共同遵循。

## 抓取任务

`CrawlTask` 对应 `crawl_task` 表，记录一次抓取任务及其执行状态。
本次只定义数据库结构；任务创建、派发和执行逻辑留待 API 与 worker 实现。

| 字段 | 含义 |
| --- | --- |
| `id` | PostgreSQL UUID 主键，由调用方显式提供 UUID7，无生成默认值。 |
| `idempotency_key` | 调用方提供的 UUID4，具有唯一约束，用于后续 HTTP 创建请求幂等。 |
| `type` | `security_info`、`latest_quote` 或 `daily_bar`；Python 枚举及 ORM 验证，无数据库类型值 CHECK，增加任务类型无需因此修改表。 |
| `params_version` | 参数版本，数据库默认值为 `1`，必须为正整数。 |
| `params` | 不可为 `null` 的 JSONB 对象；当前不定义具体业务参数，后续按 `type` 与 `params_version` 选择参数模型验证。 |
| `status` | `pending`、`dispatched`、`running`、`completed` 或 `failed`；数据库默认 `pending`，带取值 CHECK。 |
| `last_error` | 可空文本，保存最近一次错误说明。 |
| `created_at` | 创建时间，数据库默认 `now()`。 |
| `dispatched_at` | 可空，记录派发确认时间。 |
| `started_at` | 可空，记录执行开始时间。 |
| `finished_at` | 可空，记录成功或失败的结束时间。 |

四个时间字段均使用带时区时间戳。任务不继承 `TimestampMixin`，没有 `updated_at`。
表包含 `(created_at, id)` 索引，便于按创建顺序查询任务。
数据库要求 `dispatched` 填写派发时间，`running`／`completed` 填写开始时间，
且只有 `completed`／`failed` 填写结束时间；更新状态时应同时填写对应时间。

任务创建后，类型、参数版本及参数应保持不变；这项更新规则由后续应用逻辑保证。
派发确认可能晚于任务开始甚至结束，补记 `dispatched_at` 时不能把 `running` 或终态回退为 `dispatched`，
也不能假设 `dispatched_at <= started_at`。

HTTP 请求幂等用于避免重复创建任务，Kafka 补发用于处理任务派发，两者是不同机制。
目前没有实现 HTTP 幂等处理、Kafka 补发或 outbox；字段和说明不代表这些行为已经实现。
