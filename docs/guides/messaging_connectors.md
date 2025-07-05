# Messaging Connectors Guide

This guide provides information on how to use the messaging connectors in the Science Data Kit (SDK) to interact with message brokers like Kafka and RabbitMQ.

## Overview

The SDK provides connectors for the following messaging systems:

- **Kafka**: A distributed streaming platform that is horizontally scalable, fault-tolerant, and has high throughput.
- **RabbitMQ**: A message broker that implements the Advanced Message Queuing Protocol (AMQP) and supports multiple messaging patterns.

These connectors allow you to:

- Connect to message brokers
- Create and manage topics/exchanges
- Publish messages
- Consume messages
- Work with pandas DataFrames

## Prerequisites

To use the messaging connectors, you need to have the following dependencies installed:

For Kafka:
```bash
pip install confluent-kafka
```

For RabbitMQ:
```bash
pip install pika
```

## Connecting to Message Brokers

### Kafka

```python
from science_data_kit.core.providers import registry, ProviderType

# Configure Kafka connection
kafka_config = {
    'bootstrap_servers': 'localhost:9092',
    'client_id': 'sdk-client',
    # Optional security settings
    'security_protocol': 'PLAINTEXT',  # or 'SSL', 'SASL_PLAINTEXT', 'SASL_SSL'
    'sasl_mechanism': 'PLAIN',  # if using SASL
    'sasl_username': 'username',  # if using SASL
    'sasl_password': 'password',  # if using SASL
}

# Create Kafka provider
kafka_provider = registry.create_provider(ProviderType.MESSAGING, 'kafka', kafka_config)

# Initialize provider
await kafka_provider.initialize()
```

### RabbitMQ

```python
from science_data_kit.core.providers import registry, ProviderType

# Configure RabbitMQ connection
rabbitmq_config = {
    'host': 'localhost',
    'port': 5672,
    'virtual_host': '/',
    'username': 'guest',
    'password': 'guest',
    'ssl': False,
    # Optional settings
    'connection_attempts': 3,
    'retry_delay': 2,
    'heartbeat': 60,
}

# Create RabbitMQ provider
rabbitmq_provider = registry.create_provider(ProviderType.MESSAGING, 'rabbitmq', rabbitmq_config)

# Initialize provider
await rabbitmq_provider.initialize()
```

## Managing Topics/Exchanges

### Listing Topics

```python
# List topics in Kafka
kafka_topics = await kafka_provider.list_topics()
for topic in kafka_topics:
    print(f"Topic: {topic['name']}, Partitions: {topic['partition_count']}")

# List exchanges in RabbitMQ
rabbitmq_exchanges = await rabbitmq_provider.list_topics()
for exchange in rabbitmq_exchanges:
    print(f"Exchange: {exchange['name']}, Type: {exchange['type']}")
```

### Creating Topics

```python
# Create a topic in Kafka
await kafka_provider.create_topic(
    topic_name='my-topic',
    partitions=3,
    replication_factor=1
)

# Create an exchange in RabbitMQ
await rabbitmq_provider.create_topic(
    topic_name='my-exchange'
    # partitions and replication_factor are ignored in RabbitMQ
)
```

### Deleting Topics

```python
# Delete a topic in Kafka
await kafka_provider.delete_topic('my-topic')

# Delete an exchange in RabbitMQ
await rabbitmq_provider.delete_topic('my-exchange')
```

### Getting Topic Information

```python
# Get topic info in Kafka
kafka_topic_info = await kafka_provider.get_topic_info('my-topic')
print(f"Topic: {kafka_topic_info['name']}")
print(f"Partitions: {kafka_topic_info['partition_count']}")
print(f"Configs: {kafka_topic_info['configs']}")

# Get exchange info in RabbitMQ
rabbitmq_exchange_info = await rabbitmq_provider.get_topic_info('my-exchange')
print(f"Exchange: {rabbitmq_exchange_info['name']}")
print(f"Exists: {rabbitmq_exchange_info['exists']}")
```

## Publishing Messages

### Publishing Individual Messages

```python
# Publish a message to Kafka
await kafka_provider.publish_message(
    topic_name='my-topic',
    message={'key': 'value', 'timestamp': '2023-08-01T12:00:00Z'},
    key='message-key',
    headers={'source': 'sdk', 'version': '1.0'}
)

# Publish a message to RabbitMQ
await rabbitmq_provider.publish_message(
    topic_name='my-exchange',
    message={'key': 'value', 'timestamp': '2023-08-01T12:00:00Z'},
    key='routing-key',
    headers={'source': 'sdk', 'version': '1.0'}
)
```

### Publishing DataFrames

```python
import pandas as pd

# Create a DataFrame
df = pd.DataFrame({
    'id': [1, 2, 3],
    'name': ['Alice', 'Bob', 'Charlie'],
    'value': [10.5, 20.3, 15.7]
})

# Publish DataFrame to Kafka
messages_published = await kafka_provider.publish_dataframe(
    topic_name='my-topic',
    df=df,
    key_column='id'  # Use 'id' column as message key
)
print(f"Published {messages_published} messages to Kafka")

# Publish DataFrame to RabbitMQ
messages_published = await rabbitmq_provider.publish_dataframe(
    topic_name='my-exchange',
    df=df,
    key_column='id'  # Use 'id' column as routing key
)
print(f"Published {messages_published} messages to RabbitMQ")
```

## Consuming Messages

### Consuming with Callback Function

```python
# Define a callback function to process messages
def process_message(message):
    print(f"Received message: {message}")
    # Process the message as needed

# Consume messages from Kafka
messages_consumed = await kafka_provider.consume_messages(
    topic_name='my-topic',
    group_id='my-consumer-group',
    callback=process_message,
    max_messages=10,  # Stop after consuming 10 messages
    timeout_ms=5000   # Timeout after 5 seconds
)
print(f"Consumed {messages_consumed} messages from Kafka")

# Consume messages from RabbitMQ
messages_consumed = await rabbitmq_provider.consume_messages(
    topic_name='my-exchange',
    group_id='my-queue',
    callback=process_message,
    max_messages=10,  # Stop after consuming 10 messages
    timeout_ms=5000   # Timeout after 5 seconds
)
print(f"Consumed {messages_consumed} messages from RabbitMQ")
```

### Consuming to DataFrame

```python
# Consume messages from Kafka to DataFrame
kafka_df = await kafka_provider.consume_to_dataframe(
    topic_name='my-topic',
    group_id='my-consumer-group',
    max_messages=100,
    timeout_ms=5000
)
print(f"Consumed {len(kafka_df)} messages from Kafka")
print(kafka_df.head())

# Consume messages from RabbitMQ to DataFrame
rabbitmq_df = await rabbitmq_provider.consume_to_dataframe(
    topic_name='my-exchange',
    group_id='my-queue',
    max_messages=100,
    timeout_ms=5000
)
print(f"Consumed {len(rabbitmq_df)} messages from RabbitMQ")
print(rabbitmq_df.head())
```

## Best Practices

### Kafka

1. **Topic Naming**: Use descriptive names for topics, and consider using a naming convention that includes the data type, environment, and purpose.
2. **Partitioning**: Choose the number of partitions based on the expected throughput and the number of consumers. More partitions allow for more parallelism but require more resources.
3. **Replication**: Use a replication factor of at least 2 in production to ensure fault tolerance.
4. **Consumer Groups**: Use different consumer group IDs for different applications or components that need to process the same messages independently.
5. **Message Keys**: Use message keys to ensure that related messages are processed in order and by the same consumer.

### RabbitMQ

1. **Exchange Types**: Choose the appropriate exchange type based on your messaging pattern:
   - **Direct**: Route messages to queues based on an exact match of the routing key
   - **Topic**: Route messages to queues based on pattern matching of the routing key
   - **Fanout**: Route messages to all bound queues
   - **Headers**: Route messages based on header values
2. **Queue Durability**: Use durable queues for important messages that should survive broker restarts.
3. **Message Persistence**: Set the delivery mode to 2 (persistent) for important messages that should survive broker restarts.
4. **Acknowledgements**: Always acknowledge messages after processing to ensure they are removed from the queue.
5. **Prefetch Count**: Set the prefetch count to limit the number of unacknowledged messages a consumer can have at once.

## Troubleshooting

### Common Issues with Kafka

1. **Connection Refused**: Ensure that the Kafka broker is running and accessible from your application.
2. **Authentication Failed**: Check your SASL username and password, and ensure that the security protocol is correctly configured.
3. **Topic Not Found**: Ensure that the topic exists and that you have the necessary permissions to access it.
4. **Serialization Errors**: Ensure that your messages can be serialized to JSON or that you're providing them in the correct format.

### Common Issues with RabbitMQ

1. **Connection Refused**: Ensure that the RabbitMQ server is running and accessible from your application.
2. **Authentication Failed**: Check your username and password, and ensure that the virtual host exists and is accessible.
3. **Exchange Not Found**: Ensure that the exchange exists and that you have the necessary permissions to access it.
4. **Channel Closed**: This can happen if you try to declare an exchange or queue with different parameters than an existing one. Ensure that your declarations are consistent.

## Conclusion

The messaging connectors in the Science Data Kit provide a unified interface for interacting with different message brokers. By following this guide, you should be able to connect to Kafka and RabbitMQ, publish and consume messages, and work with pandas DataFrames.

For more information, refer to the API documentation for the `KafkaProvider` and `RabbitMQProvider` classes.