# Mivy SDK

应用与工具共享的基础能力。PostgreSQL 客户端位于 `mivy_sdk.infra.postgres`，
不依赖服务入口或 Alembic。未来数据库模型和 metadata 由 `mivy_contracts.db` 管理。

## 配置

从仓库根目录运行 `uv sync`。参考根目录 `.env.example` 配置 PostgreSQL；
启动与迁移步骤见 [迁移说明](../../migrations/postgres/README.md)。

SDK 的 `PostgresConfig` 是不可变的 Pydantic `BaseModel`，只校验显式传入的值，
不读取环境变量或文件。字段为 `host`、`port`、`db`、`user`、`password`，全部必填；
未知字段会报错，避免拼写错误被忽略。SDK 不依赖 `pydantic-settings`。

```python
from mivy_sdk.infra.postgres import PostgresConfig

config = PostgresConfig(
    host="127.0.0.1",
    port=5432,
    db="mivy",
    user="mivy",
    password="your-development-password",  # 示例；实际凭据由运行入口提供。
)
```

`password` 是 `SecretStr`，`url` 是原生 SQLAlchemy URL。
配置和 URL 仍包含真实凭据，不应输出完整配置、关闭 URL 密码隐藏，或记录
`ValidationError.errors()` 中的原始输入。默认异常文本和对象表示会隐藏敏感值。

每个运行入口决定配置来源，并将配置对象注入客户端。当前只有 Alembic 需要加载配置：
其 `env.py` 定义 `MigrationSettings(BaseSettings)`，组合 `postgres: PostgresConfig`。
通过 Pydantic Settings 的嵌套字段解析，将现有 `POSTGRES_HOST` 等变量映射到模型，
字段校验仍由 SDK 统一定义。迁移不会要求与 PostgreSQL 无关的配置。

未来服务在启动时加载自身 settings，然后调用
`AsyncPostgresClient(service_settings.postgres)`。环境加载归入口，配置结构归 SDK，
业务代码只使用传入的客户端。当前不提前创建服务配置类或公共配置加载框架。

## 同步访问

以下示例使用上面显式构造的 `config`；应用也可以从自身 settings 中取得该对象。

```python
from sqlalchemy import text

from mivy_sdk.infra.postgres import PostgresClient

client = PostgresClient(config)
try:
    with client.connect() as connection:
        value = connection.scalar(text("SELECT 1"))

    with client.begin() as connection:
        connection.execute(text("SELECT 1"))
finally:
    client.dispose()
```

## 异步访问

```python
import asyncio

from sqlalchemy import text

from mivy_sdk.infra.postgres import AsyncPostgresClient, PostgresConfig


async def main(config: PostgresConfig) -> None:
    client = AsyncPostgresClient(config)
    try:
        async with client.connect() as connection:
            value = await connection.scalar(text("SELECT 1"))

        async with client.begin() as connection:
            await connection.execute(text("SELECT 1"))
    finally:
        await client.dispose()


asyncio.run(main(config))
```

异步 `connect()` 与 `begin()` 直接用于 `async with`，不需要先 `await`。
同步、异步客户端都组合 SQLAlchemy Engine，返回原生 Connection 和 Result，
保留原生异常。`client.engine` 提供原生高级接口，不额外包装 SQL 或业务 CRUD。

## 生命周期与事务

- 应用生命周期内复用客户端；不要为每条查询创建客户端。
- 导入包和构造客户端不建立网络连接，首次获取连接时才连接数据库。
- `connect()` 不自动提交，退出时回滚尚未提交的事务并归还连接。
- `begin()` 成功退出时提交，异常时回滚，随后归还连接；异常不会被吞掉。
- 每个线程／并发任务独立获取 Connection，异步客户端限于同一事件循环使用。
- 应用关闭时先结束操作并退出连接上下文，再调用或等待 `dispose()`。
- `dispose()` 不强制关闭借出的连接，也不是永久关闭客户端；后续调用仍可新建连接池。
- SDK 不管理 ORM Session，不配置应用日志，不进行隐式重试。

## 连接池策略

```python
from mivy_sdk.infra.postgres import PostgresClient, PostgresPoolOptions

client = PostgresClient(
    config,
    pool_options=PostgresPoolOptions(pool_size=5, max_overflow=10, pool_timeout=30.0),
)
# 一次性迁移使用 PostgresPoolOptions(enabled=False)。
```

默认开启连接池及 `pool_pre_ping`。`pool_timeout` 是池已满时等待空闲连接的秒数，
不是建立网络连接或执行 SQL 的超时。`pool_size` 必须为正，`max_overflow` 非负，
`pool_timeout` 为有限正数。不可变选项可供多个客户端使用，但客户端各自拥有自己的池。
禁用池时使用 `NullPool`，不向其传递队列池参数。默认驱动统一为 psycopg 3。

`PostgresPoolOptions` 显式实现共享的 `SupportsAsDict[EnginePoolOptions]` Protocol
（从 `mivy_contracts.protocols.common` 导入），通过 `asdict()` 返回一份新的 Engine 参数字典。
这是用于创建 Engine 的参数导出：启用时不包含 `enabled`，禁用时仅包含
`poolclass=NullPool`；禁用时仍校验所有配置字段。字段名与 SQLAlchemy 参数一致，
新增字段时需要保持这一约定。客户端的参数类型仍为 `PostgresPoolOptions | None`，
不会因为其他对象也有 `asdict()` 方法就接受它。Protocol 的类型参数用于约束导出结果，
不负责运行时校验；创建配置对象时不需要额外传入类型参数。

## 代码检查

在仓库根目录执行：

```bash
uv run mypy
uv run ruff check packages/sdk/src/mivy_sdk/infra packages/contracts/src/mivy_contracts/protocols migrations/postgres/env.py
uv run ruff format --check packages/sdk/src/mivy_sdk/infra packages/contracts/src/mivy_contracts/protocols migrations/postgres/env.py
```

设计参考：[SQLAlchemy 连接与事务](https://docs.sqlalchemy.org/en/20/core/connections.html)、
[异步资源管理](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)、
[OpenStack oslo.db](https://github.com/openstack/oslo.db/blob/master/oslo_db/sqlalchemy/enginefacade.py)、
[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)。
