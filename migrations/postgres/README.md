# PostgreSQL 迁移命令

所有命令在仓库根目录执行。Alembic 自动读取根目录 `.env`，环境变量优先。

## 准备与启动

```bash
# 安装依赖
uv sync

# 首次创建配置文件；保留已有 .env，创建后填写 POSTGRES_PASSWORD
[ -f .env ] || cp .env.example .env

# 启动 PostgreSQL，并等待健康检查通过（需先启动 Docker）
docker compose --env-file .env -f docker/compose.yaml up -d --wait

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

# 创建迁移脚本，随后填写 upgrade() 和 downgrade()
uv run alembic -c migrations/postgres/alembic.ini revision --rev-id 0001 -m "create securities"
```

编号依次使用 `0001`、`0002`，文件形如 `0001_create_securities.py`。
保持单个 head，由 `down_revision` 确定执行顺序；已在共享环境执行的脚本不改写。
当前没有业务迁移，暂未接入模型 metadata，不使用 `--autogenerate`。

## 升级与回退

以下编号命令需先创建对应 revision；回退可能删除表或数据，执行前检查脚本。

```bash
# 升级到最新版本；容器启动不会自动执行迁移
uv run alembic -c migrations/postgres/alembic.ini upgrade head

# 升级到指定版本
uv run alembic -c migrations/postgres/alembic.ini upgrade 0002

# 回退一个版本
uv run alembic -c migrations/postgres/alembic.ini downgrade -1

# 回退到指定版本
uv run alembic -c migrations/postgres/alembic.ini downgrade 0001
```

## 导出 SQL（不连接数据库）

```bash
# 从空版本到最新版本的升级 SQL，不读取数据库当前版本
uv run alembic -c migrations/postgres/alembic.ini upgrade head --sql

# 指定版本范围的升级或回退 SQL
uv run alembic -c migrations/postgres/alembic.ini upgrade 0001:0002 --sql
uv run alembic -c migrations/postgres/alembic.ini downgrade 0002:0001 --sql
```

## 停止与清理

```bash
# 删除容器和网络，保留数据库数据；重新运行 up 即可恢复服务
docker compose --env-file .env -f docker/compose.yaml down

# 删除容器、网络及数据卷，清空全部本地数据库数据
docker compose --env-file .env -f docker/compose.yaml down -v
```

数据库名、账号和密码仅在空数据卷首次初始化时生效，修改 `.env` 不会更新已有账号。
