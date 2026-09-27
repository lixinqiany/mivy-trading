# Mivy Trading

## 开发环境

从仓库根目录执行：

```bash
# 安装 workspace 包和开发工具
uv sync --all-packages

# 安装 Git 提交钩子；每次新克隆仓库后执行一次
uv run pre-commit install

# 对已跟踪的文件执行全部提交检查
uv run pre-commit run --all-files
```

使用 VS Code 打开仓库根目录，安装 `.vscode/extensions.json` 中推荐的扩展。
Python 解释器使用根目录 `.venv/bin/python`；如果之前选过其他环境，运行
`Python: Select Interpreter` 切换到该解释器。

Ruff 提供编辑诊断，手动保存 Python 文件时格式化、整理导入并应用安全修复。
mypy 根据根目录 `pyproject.toml` 检查四个包的类型，在 Problems 面板显示问题。

提交钩子对本次提交的 Python 源码和迁移文件执行 Ruff；源码、依赖或检查配置
变化时执行四个包的 mypy 检查。Ruff 修改文件后，本次提交会中止，检查修改、
重新暂存后再提交。所有工具复用 uv 环境，依赖变化后先运行 `uv sync --all-packages`。

PostgreSQL 启动与迁移命令见 [迁移说明](migrations/postgres/README.md)。

Kafka 部署及 Topic 管理见 [Kafka 说明](migrations/kafka/README.md)，
同步、异步收发示例见 [SDK 说明](packages/sdk/README.md)。

模型、字段和代码说明见 [contracts](packages/contracts/README.md)。
