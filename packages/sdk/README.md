# Mivy SDK

为 Mivy Trading 的服务和工具提供统一的基础设施访问接口与可复用能力，减少重复实现。

- 封装数据库等基础设施的访问入口，统一配置结构和资源生命周期。
- 提供 PostgreSQL 同步、异步连接与 ORM 会话管理，以及 Kafka 同步、异步客户端。
- 使用 contracts 中的公共约定，由调用方提供配置并组织业务流程。

## Kafka

`mivy_sdk.infra.kafka` 提供 `KafkaConfig`、`KafkaProducer`、`KafkaConsumer`、
`AsyncKafkaProducer` 和 `AsyncKafkaConsumer`。SDK 使用 confluent-kafka，
管理配置和客户端生命周期；Topic 管理见 [Jikkou 操作说明](../../migrations/kafka/README.md)。

配置由调用方提供，SDK 不读取环境变量。以下演示用于独立开发或测试 Kafka：

```python
from confluent_kafka import KafkaException, TopicPartition
from pydantic import SecretStr

from mivy_sdk.infra.kafka import KafkaConfig, KafkaConsumer, KafkaProducer

config = KafkaConfig(
    bootstrap_servers="127.0.0.1:9092",
    security_protocol="SASL_PLAINTEXT",
    sasl_mechanism="PLAIN",
    username="mivy",
    password=SecretStr(password),  # 由应用的配置入口提供。
    consumer_options={"group.id": "mivy.data.crawling-workers"},
)

with KafkaProducer(config) as publisher:
    message = publisher.publish_and_wait(
        "mivy.data.crawling-tasks", b"example", key=b"security-id"
    )

with KafkaConsumer(config) as reader:
    reader.consumer.subscribe(["mivy.data.crawling-tasks"])
    for message in reader.consumer.consume(10, timeout=1):
        if error := message.error():
            raise KafkaException(error)
        # 实际调用方在处理成功后，决定当前分区能推进到哪里。
        print(message.value())
        reader.commit_offsets(
            [TopicPartition(message.topic(), message.partition(), message.offset() + 1)]
        )
```

异步版本使用相同配置，通过 `async with` 管理生命周期：

```python
from mivy_sdk.infra.kafka import AsyncKafkaConsumer, AsyncKafkaProducer

async with AsyncKafkaProducer(config) as publisher:
    message = await publisher.publish_and_wait("mivy.data.crawling-tasks", b"example")

async with AsyncKafkaConsumer(config) as reader:
    await reader.consumer.subscribe(["mivy.data.crawling-tasks"])
    messages = await reader.consumer.consume(10, timeout=1)
    # 检查错误、完成处理后，再 await reader.commit_offsets(...)。
```

### 配置和原生能力

生产者默认启用幂等发送和 `acks=all`。消费者默认关闭自动提交和自动 offset 存储，
使用 `auto.offset.reset=earliest`。调用方可用 `producer_options`、`consumer_options`
显式覆盖默认值，传入原生客户端支持的其他参数。地址、认证等连接字段只在
`KafkaConfig` 中设置，重复配置会报错。参数间的原生约束仍由 confluent-kafka 检查。

例如可配置 `producer_options={"compression.type": "zstd"}`，或者让一个新的消费组
使用 `consumer_options={"group.id": "quotes-reader", "auto.offset.reset": "latest"}`。
`latest` 只影响没有有效已提交进度时的起点。

`.producer` / `.consumer` 返回真实客户端，保留原生类型、异常和回调：

- 调用 `.producer.produce(...)` 可批量入队；调用方负责投递回调、轮询和错误处理。
- 调用 `.consumer.subscribe/consume/poll/assignment/pause/resume` 使用原生消费能力。
- SDK 不解析 JSON、不创建 Topic、不运行任务，也不决定业务进度何时提交。

同步和异步原生 API 的差异不被隐藏：异步 rebalance 回调应为协程；当前
`AIOProducer` 不支持发送 headers，需要 headers 的同步调用可通过原生 Producer 使用。
异步生产者默认 `batch_size=1, buffer_timeout=0.1`，可通过构造参数修改；
这控制 Python 层缓冲，librdkafka 的批处理配置仍然有效。等待投递的便利方法要求
启用后台驱动；批处理参数会影响消息何时发送。

### 生命周期与确认语义

内部按同步、异步各设一个生命周期基类，复用连接、关闭和上下文管理；
具体的生产者、消费者类负责发送、投递结果收尾和进度提交。基类不作为公共 API 导出。

构造只保存配置；`connect(timeout=10)` 初始化并检查连接，重复连接复用实例。
检查成功不代表消费者已获得分区。`with` / `async with` 自动连接和关闭；
关闭可重复调用，关闭后需要新建实例。连接检查失败也会清理已创建资源。

`publish_and_wait` 等待单条消息的投递结果，不逐条等待整个队列清空。
默认 `acks=all` 时成功表示 Kafka 已确认；显式使用 `acks=0` 时没有 broker 确认保障。
该便利方法需要成功投递回调，不能开启 `delivery.report.only.error`；原生发送不受此限制。
幂等发送处理客户端内部重试，不保证应用重复提交或业务执行只发生一次。
取消等待或投递超时也不能证明消息一定没有写入。

`commit_offsets` 要求显式提供各分区的**下一条 offset**，并等待、检查提交结果。
参数检查与特殊值语义遵循原生客户端；调用方应传非负的具体 offset，负值可能被跳过。
同一分区并发处理时，不能跨过尚未完成的较早消息。其他提交方式可直接使用原生接口。
默认配置下关闭消费者不会自动提交；显式启用自动提交后，关闭遵循原生行为。

关闭前先结束消费循环和对原生客户端的操作。Producer 收尾待发送消息，异步客户端
释放自身线程资源；SDK 只跟踪其便利发送方法，原生发送的回调仍由调用方负责。
连接检查的 timeout 直接传给原生元数据请求，默认 10 秒，`-1` 表示无限等待；
资源清理和关闭没有硬性总时限。

Producer 应在进程内长期复用，异步实例限定在所属事件循环内。一个 Consumer 由
一个读取循环驱动，再将消息交给业务并发执行；暂停分区后仍要持续轮询。
底层库维护和复用 broker 连接，无需另建 Kafka 连接池。数据库同样复用连接，
但通过共享 Engine/连接池向独立 Session 分配连接，二者的资源使用方式不同。

## 代码检查

```bash
uv run ruff check packages/sdk
uv run mypy
```
