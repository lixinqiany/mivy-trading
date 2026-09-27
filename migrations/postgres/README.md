# PostgreSQL 迁移命令

所有命令在仓库根目录执行。Alembic 自动读取根目录 `.env`，环境变量优先。

## 准备与启动

```bash
# 安装依赖
uv sync

# 首次创建配置文件；保留已有 .env，创建后填写 POSTGRES_PASSWORD
[ -f .env ] || cp .env.example .env

# 启动 PostgreSQL，并等待健康检查通过（需先启动 Docker）
docker compose --env-file .env -f docker/compose.yaml up -d --wait postgres

# 查看服务状态和数据库日志
docker compose --env-file .env -f docker/compose.yaml ps
docker compose --env-file .env -f docker/compose.yaml logs -f postgres
```

## 查看与创建迁移

```bash
# 查看数据库当前版本
uv run alembic -c migrations/postgres/alembic.ini current

# 查看迁移历史及最新版本
uv run alembic -c migrations/postgres/alembic.ini history
uv run alembic -c migrations/postgres/alembic.ini heads

# 根据模型生成下一份迁移草稿，随后人工检查 upgrade() 和 downgrade()
uv run alembic -c migrations/postgres/alembic.ini revision --autogenerate --rev-id 0003 -m "describe change"

# 检查数据库与模型是否存在可自动检测的差异
uv run alembic -c migrations/postgres/alembic.ini check
```

编号依次使用 `0001`、`0002`，文件形如 `0001_create_security_tables.py`。
编号至少四位，不足补零；超过 `9999` 后使用 `10000`，不重编号已有迁移。
保持单个 head，由 `down_revision` 确定执行顺序；已在共享环境执行的脚本不改写。
`0001_create_security_tables.py` 同时创建标的表和最新行情快照表；
`0002_create_crawl_task.py` 接续 `0001`，创建 `crawl_task` 表及其约束、索引。
metadata 来自 `mivy_contracts.db.Base`。本次只交付数据库结构，不自动升级本地业务数据库。
`--autogenerate` 和 `check` 不能完整检测 CHECK 变更，枚举允许值和约束需人工核对。
历史迁移固定保存结构和代码值，不导入当前模型或枚举。

## 升级与回退

以下编号命令需先创建对应 revision；回退可能删除表或数据，执行前检查脚本。

```bash
# 升级到最新版本；容器启动不会自动执行迁移
uv run alembic -c migrations/postgres/alembic.ini upgrade head

# 升级到首个版本，创建标的表和最新行情快照表
uv run alembic -c migrations/postgres/alembic.ini upgrade 0001

# 升级到任务表版本；数据库已在 0001 时仅执行新增任务表迁移
uv run alembic -c migrations/postgres/alembic.ini upgrade 0002

# 回退一个版本
uv run alembic -c migrations/postgres/alembic.ini downgrade -1

# 回退全部迁移，删除任务表、快照表和证券表及其数据
uv run alembic -c migrations/postgres/alembic.ini downgrade base
```

## 导出 SQL（不连接数据库）

```bash
# 从空版本到最新版本的升级 SQL，不读取数据库当前版本
uv run alembic -c migrations/postgres/alembic.ini upgrade head --sql

# 只导出 0002 新增任务表的升级 SQL
uv run alembic -c migrations/postgres/alembic.ini upgrade 0001:0002 --sql

# 导出当前最新版本到空版本的回退 SQL
uv run alembic -c migrations/postgres/alembic.ini downgrade 0002:base --sql
```

## 停止与清理

```bash
# 仅停止 PostgreSQL，保留数据，不影响 Kafka。
docker compose --env-file .env -f docker/compose.yaml stop postgres

# 删除整个 Compose 项目的容器和网络，保留 PostgreSQL 和 Kafka 数据卷。
docker compose --env-file .env -f docker/compose.yaml down

# 清空整个项目：同时删除 PostgreSQL 数据及 Kafka 消息、消费进度。
docker compose --env-file .env -f docker/compose.yaml down -v
```

数据库名、账号和密码仅在空数据卷首次初始化时生效，修改 `.env` 不会更新已有账号。
