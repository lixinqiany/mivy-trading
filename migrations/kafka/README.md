# Kafka 部署与 Topic 管理

所有命令在仓库根目录执行，要求 Docker Compose 2.23.1 或更高版本（使用 `configs.content`）。
Kafka 使用 `docker/compose.yaml` 部署，保留官方镜像的默认启动入口；
broker 参数和账号通过 Compose 环境变量配置。
Jikkou 1.1.0 按 `topics.yaml` 中的声明管理业务 Topic，以 Git 记录配置变更，无需迁移编号或迁移历史表。

## 首次配置与启动

保留已有根目录 `.env`，首次使用时从 `.env.example` 复制，并补充其中的 Kafka 配置。
生成 `KAFKA_CLUSTER_ID` 和 `KAFKA_PASSWORD` 后分别填入 `.env`：

```bash
docker run --rm --entrypoint /opt/kafka/bin/kafka-storage.sh apache/kafka:4.3.1 random-uuid
openssl rand -hex 32
```

`KAFKA_USERNAME` 使用字母、数字、下划线或连字符；`KAFKA_PASSWORD` 使用上面生成的
64 位十六进制字符串。凭据直接传给原生 JAAS 配置，不额外实现特殊字符转义。

首次启动和后续启动使用同一条命令：

```bash
docker compose --env-file .env -f docker/compose.yaml up -d --wait kafka

# 查看运行状态及日志。
docker compose --env-file .env -f docker/compose.yaml ps kafka
docker compose --env-file .env -f docker/compose.yaml logs -f kafka
```

官方启动流程首次自动初始化存储，后续启动复用已有存储，
并拒绝不匹配的 cluster ID；`KAFKA_CLUSTER_ID` 应随数据卷长期保持不变。
PLAIN 账号由启动时的 JAAS 配置提供，无需提前创建账号。

宿主机客户端使用 `.env` 中的 `KAFKA_BOOTSTRAP_SERVERS`，默认 `127.0.0.1:9092`；
Compose 网络内的客户端使用 `kafka:29092`。两者都使用 `PLAIN` 认证和 `SASL_PLAINTEXT`：
没有 TLS，用户名和密码以明文传输；宿主机端口只绑定回环地址，限本机或受控 Docker 网络使用。

## 预览与应用 Topic

Jikkou 使用镜像默认入口，通过静态 `config.json` 选择 `application.conf`，
认证参数由 Compose 传入，仓库配置文件中不保存秘密。
服务放在 `tools` profile 下，正常启动不会常驻；`run jikkou` 会直接运行指定服务。

```bash
docker compose --env-file .env -f docker/compose.yaml run --rm jikkou health get kafka
docker compose --env-file .env -f docker/compose.yaml run --rm jikkou validate -f topics.yaml
docker compose --env-file .env -f docker/compose.yaml run --rm jikkou diff -f topics.yaml \
  --options=delete-orphans=false --options=config-delete-orphans=false
docker compose --env-file .env -f docker/compose.yaml run --rm jikkou apply -f topics.yaml \
  --options=delete-orphans=false --options=config-delete-orphans=false
```

`topics.yaml` 定义 `mivy.data.crawling-tasks`：两个分区、一个副本、最少同步副本数为 1，
按 `delete` 策略保留消息七天。Kafka 按日志段清理，七天并非逐条消息的精确删除时刻；
消费或提交进度不直接删除消息。

修改声明后，先检查 `diff` 再 `apply`。相同声明重复应用不重建 Topic、不清空消息；
上面的 `diff` 和 `apply` 命令显式设置 `delete-orphans=false` 与 `config-delete-orphans=false`，
省略 Topic 或配置项不会隐式删除已有资源或重置其配置。需要恢复某个配置时显式填写目标值。
分区数只能增加，减少分区或重命名不作为普通配置变更处理。

应用配置后可再次检查差异；`--fail-on-changes` 在存在差异时返回退出码 3：

```bash
docker compose --env-file .env -f docker/compose.yaml run --rm jikkou diff -f topics.yaml \
  --options=delete-orphans=false --options=config-delete-orphans=false --fail-on-changes
```

Kafka 已关闭自动创建 Topic。业务生产者和消费者不会创建 Topic；
消费者组在客户端加入时创建，本阶段不需要声明消费者组资源。

## 修改账号密码

用 `openssl rand -hex 32` 生成新密码，修改根目录 `.env` 中的 `KAFKA_PASSWORD`，
再重建 Kafka 容器使新账号配置生效；修改用户名也使用相同步骤：

```bash
docker compose --env-file .env -f docker/compose.yaml up -d --force-recreate --wait kafka
docker compose --env-file .env -f docker/compose.yaml run --rm jikkou health get kafka
```

Compose 同时更新 broker、健康检查和 Jikkou 使用的认证配置；重建容器保留数据卷。
使用该账号的应用也需要更新凭据并重启客户端。

## 停止与恢复

```bash
docker compose --env-file .env -f docker/compose.yaml stop kafka
docker compose --env-file .env -f docker/compose.yaml up -d --wait kafka
```

消息、消费进度和 KRaft 元数据保存在 Kafka 数据卷中，停止或重建容器不会清除它们。
单节点只有一份数据，本阶段没有服务器故障后的副本接管能力。

本阶段只提供部署、Topic 管理和通用 SDK，不在启动时执行任务派发、任务状态更新或爬虫逻辑。
