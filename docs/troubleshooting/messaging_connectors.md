# Troubleshooting Messaging Connectors

This guide provides detailed troubleshooting steps for common issues encountered when using the Kafka and RabbitMQ connectors in the Science Data Kit (SDK).

## Table of Contents

1. [Kafka Connector Issues](#kafka-connector-issues)
   - [Connection Issues](#kafka-connection-issues)
   - [Authentication Issues](#kafka-authentication-issues)
   - [Topic Management Issues](#kafka-topic-management-issues)
   - [Publishing Issues](#kafka-publishing-issues)
   - [Consumption Issues](#kafka-consumption-issues)

2. [RabbitMQ Connector Issues](#rabbitmq-connector-issues)
   - [Connection Issues](#rabbitmq-connection-issues)
   - [Authentication Issues](#rabbitmq-authentication-issues)
   - [Exchange Management Issues](#rabbitmq-exchange-management-issues)
   - [Publishing Issues](#rabbitmq-publishing-issues)
   - [Consumption Issues](#rabbitmq-consumption-issues)

3. [General Troubleshooting Tips](#general-troubleshooting-tips)
   - [Checking Provider Initialization](#checking-provider-initialization)
   - [Debugging Asynchronous Code](#debugging-asynchronous-code)
   - [Handling Serialization Issues](#handling-serialization-issues)

## Kafka Connector Issues

### Kafka Connection Issues

#### Issue: Connection Refused

**Symptoms**:
- Error message: `Connection refused` or `Broker not available`
- `initialize()` method returns `False`
- `KafkaException` with error code `TRANSPORT`

**Possible Causes**:
1. Kafka broker is not running
2. Incorrect host or port
3. Network connectivity issues
4. Firewall blocking the connection

**Troubleshooting Steps**:
1. Verify that the Kafka broker is running:
   ```bash
   # Check if Kafka is running locally
   ps aux | grep kafka
   
   # If using Docker
   docker ps | grep kafka
   ```

2. Check the broker address and port:
   ```python
   print(f"Connecting to Kafka at {kafka_provider.bootstrap_servers}")
   ```

3. Test network connectivity:
   ```bash
   # Test TCP connection to the Kafka broker
   nc -zv <host> <port>
   ```

4. Check firewall settings:
   ```bash
   # Check if the port is open
   sudo ufw status
   ```

**Solution**:
```python
# Update the configuration with correct broker address
kafka_config = {
    'bootstrap_servers': 'correct-host:9092',
    'client_id': 'sdk-client',
}

# Create and initialize provider
kafka_provider = registry.create_provider(ProviderType.MESSAGING, 'kafka', kafka_config)
await kafka_provider.initialize()
```

### Kafka Authentication Issues

#### Issue: Authentication Failed

**Symptoms**:
- Error message: `Authentication failed` or `SASL authentication failed`
- `initialize()` method returns `False`
- `KafkaException` with error code `AUTHENTICATION`

**Possible Causes**:
1. Incorrect SASL username or password
2. Wrong SASL mechanism
3. SSL/TLS configuration issues
4. Missing or incorrect security protocol

**Troubleshooting Steps**:
1. Verify SASL credentials:
   ```python
   print(f"Using SASL mechanism: {kafka_provider.config.get('sasl_mechanism')}")
   print(f"Using username: {kafka_provider.config.get('sasl_username')}")
   # Don't print the password for security reasons
   ```

2. Check security protocol:
   ```python
   print(f"Using security protocol: {kafka_provider.config.get('security_protocol')}")
   ```

3. Verify SSL/TLS configuration:
   ```python
   print(f"SSL CA file: {kafka_provider.config.get('ssl_cafile')}")
   print(f"SSL certificate file: {kafka_provider.config.get('ssl_certfile')}")
   print(f"SSL key file: {kafka_provider.config.get('ssl_keyfile')}")
   ```

**Solution**:
```python
# Update the configuration with correct authentication details
kafka_config = {
    'bootstrap_servers': 'broker:9092',
    'client_id': 'sdk-client',
    'security_protocol': 'SASL_SSL',
    'sasl_mechanism': 'PLAIN',
    'sasl_username': 'correct-username',
    'sasl_password': 'correct-password',
    'ssl_cafile': '/path/to/ca.pem',
}

# Create and initialize provider
kafka_provider = registry.create_provider(ProviderType.MESSAGING, 'kafka', kafka_config)
await kafka_provider.initialize()
```

### Kafka Topic Management Issues

#### Issue: Topic Creation Failed

**Symptoms**:
- `create_topic()` method returns `False`
- Error message: `Topic already exists` or `Not enough brokers`

**Possible Causes**:
1. Topic already exists with different configuration
2. Insufficient brokers for the specified replication factor
3. Insufficient permissions to create topics
4. Invalid topic name

**Troubleshooting Steps**:
1. Check if the topic already exists:
   ```python
   topics = await kafka_provider.list_topics()
   topic_names = [topic['name'] for topic in topics]
   print(f"Existing topics: {topic_names}")
   ```

2. Verify replication factor:
   ```python
   # Get cluster metadata
   topics_metadata = kafka_provider.admin_client.list_topics(timeout=10)
   broker_count = len(topics_metadata.brokers)
   print(f"Number of brokers: {broker_count}")
   ```

3. Check topic name validity:
   ```python
   # Topic names should not contain characters like '/', '\', '.', ',', ' '
   import re
   topic_name = 'my-topic'
   if re.search(r'[/\\., ]', topic_name):
       print(f"Invalid topic name: {topic_name}")
   ```

**Solution**:
```python
# Create topic with valid configuration
try:
    # Use a replication factor that doesn't exceed the number of brokers
    success = await kafka_provider.create_topic(
        topic_name='valid-topic-name',
        partitions=3,
        replication_factor=min(3, broker_count)  # Don't exceed broker count
    )
    print(f"Topic creation {'succeeded' if success else 'failed'}")
except Exception as e:
    print(f"Error creating topic: {str(e)}")
```

### Kafka Publishing Issues

#### Issue: Message Publishing Failed

**Symptoms**:
- `publish_message()` method returns `False`
- Error message: `Topic not found` or `Message serialization failed`

**Possible Causes**:
1. Topic doesn't exist
2. Message cannot be serialized to JSON
3. Network issues during publishing
4. Producer configuration issues

**Troubleshooting Steps**:
1. Verify that the topic exists:
   ```python
   topics = await kafka_provider.list_topics()
   topic_names = [topic['name'] for topic in topics]
   if 'my-topic' not in topic_names:
       print("Topic 'my-topic' does not exist")
   ```

2. Check message serialization:
   ```python
   import json
   
   message = {'key': 'value', 'complex': {'nested': 'value'}}
   try:
       json_str = json.dumps(message)
       print(f"Message serialization successful: {json_str}")
   except Exception as e:
       print(f"Message serialization failed: {str(e)}")
   ```

3. Test producer configuration:
   ```python
   # Check producer configuration
   print(f"Producer configuration: {kafka_provider.producer.config}")
   ```

**Solution**:
```python
# Ensure topic exists before publishing
topics = await kafka_provider.list_topics()
topic_names = [topic['name'] for topic in topics]
if 'my-topic' not in topic_names:
    await kafka_provider.create_topic('my-topic', partitions=1, replication_factor=1)

# Ensure message is serializable
try:
    message = {'key': 'value', 'timestamp': '2023-08-01T12:00:00Z'}
    success = await kafka_provider.publish_message(
        topic_name='my-topic',
        message=message,
        key='message-key'
    )
    print(f"Message publishing {'succeeded' if success else 'failed'}")
except Exception as e:
    print(f"Error publishing message: {str(e)}")
```

### Kafka Consumption Issues

#### Issue: No Messages Consumed

**Symptoms**:
- `consume_messages()` returns 0
- No messages are processed by the callback function
- `consume_to_dataframe()` returns an empty DataFrame

**Possible Causes**:
1. No messages in the topic
2. Consumer group has already consumed all messages
3. Incorrect topic name
4. Timeout too short
5. Consumer configuration issues

**Troubleshooting Steps**:
1. Check if the topic has messages:
   ```python
   # This is a workaround as Kafka doesn't provide a direct way to count messages
   # You can use a separate consumer with a new group ID to check
   test_messages = []
   
   def collect_message(message):
       test_messages.append(message)
   
   await kafka_provider.consume_messages(
       topic_name='my-topic',
       group_id='test-group-' + str(int(time.time())),  # Use a unique group ID
       callback=collect_message,
       max_messages=10,
       timeout_ms=5000
   )
   
   print(f"Found {len(test_messages)} messages in the topic")
   ```

2. Check consumer group:
   ```python
   # Use a new consumer group to start from the beginning
   new_group_id = 'new-group-' + str(int(time.time()))
   print(f"Using new consumer group: {new_group_id}")
   ```

3. Verify topic name:
   ```python
   topics = await kafka_provider.list_topics()
   topic_names = [topic['name'] for topic in topics]
   print(f"Available topics: {topic_names}")
   ```

4. Increase timeout:
   ```python
   # Use a longer timeout
   timeout_ms = 30000  # 30 seconds
   print(f"Using timeout: {timeout_ms}ms")
   ```

**Solution**:
```python
# Use a new consumer group and longer timeout
try:
    new_group_id = 'new-group-' + str(int(time.time()))
    messages_consumed = await kafka_provider.consume_messages(
        topic_name='my-topic',
        group_id=new_group_id,
        callback=lambda msg: print(f"Received: {msg}"),
        max_messages=10,
        timeout_ms=30000  # 30 seconds
    )
    print(f"Consumed {messages_consumed} messages")
except Exception as e:
    print(f"Error consuming messages: {str(e)}")
```

## RabbitMQ Connector Issues

### RabbitMQ Connection Issues

#### Issue: Connection Refused

**Symptoms**:
- Error message: `Connection refused` or `Socket closed`
- `initialize()` method returns `False`
- `pika.exceptions.AMQPConnectionError`

**Possible Causes**:
1. RabbitMQ server is not running
2. Incorrect host or port
3. Network connectivity issues
4. Firewall blocking the connection

**Troubleshooting Steps**:
1. Verify that the RabbitMQ server is running:
   ```bash
   # Check if RabbitMQ is running locally
   sudo rabbitmqctl status
   
   # If using Docker
   docker ps | grep rabbitmq
   ```

2. Check the server address and port:
   ```python
   print(f"Connecting to RabbitMQ at {rabbitmq_provider.host}:{rabbitmq_provider.port}")
   ```

3. Test network connectivity:
   ```bash
   # Test TCP connection to the RabbitMQ server
   nc -zv <host> <port>
   ```

4. Check firewall settings:
   ```bash
   # Check if the port is open
   sudo ufw status
   ```

**Solution**:
```python
# Update the configuration with correct server address
rabbitmq_config = {
    'host': 'correct-host',
    'port': 5672,
    'virtual_host': '/',
    'username': 'guest',
    'password': 'guest',
    'connection_attempts': 3,
    'retry_delay': 2,
}

# Create and initialize provider
rabbitmq_provider = registry.create_provider(ProviderType.MESSAGING, 'rabbitmq', rabbitmq_config)
await rabbitmq_provider.initialize()
```

### RabbitMQ Authentication Issues

#### Issue: Authentication Failed

**Symptoms**:
- Error message: `ACCESS_REFUSED` or `Login was refused`
- `initialize()` method returns `False`
- `pika.exceptions.ProbableAuthenticationError`

**Possible Causes**:
1. Incorrect username or password
2. Wrong virtual host
3. Insufficient permissions
4. SSL/TLS configuration issues

**Troubleshooting Steps**:
1. Verify credentials:
   ```python
   print(f"Using username: {rabbitmq_provider.username}")
   print(f"Using virtual host: {rabbitmq_provider.virtual_host}")
   # Don't print the password for security reasons
   ```

2. Check SSL configuration:
   ```python
   print(f"SSL enabled: {rabbitmq_provider.ssl}")
   print(f"SSL options: {rabbitmq_provider.ssl_options}")
   ```

3. Test with default credentials:
   ```python
   # Try with default credentials
   test_config = {
       'host': rabbitmq_provider.host,
       'port': rabbitmq_provider.port,
       'virtual_host': '/',
       'username': 'guest',
       'password': 'guest',
       'ssl': False,
   }
   ```

**Solution**:
```python
# Update the configuration with correct authentication details
rabbitmq_config = {
    'host': 'localhost',
    'port': 5672,
    'virtual_host': '/',
    'username': 'correct-username',
    'password': 'correct-password',
    'ssl': False,
    'connection_attempts': 3,
    'retry_delay': 2,
}

# Create and initialize provider
rabbitmq_provider = registry.create_provider(ProviderType.MESSAGING, 'rabbitmq', rabbitmq_config)
await rabbitmq_provider.initialize()
```

### RabbitMQ Exchange Management Issues

#### Issue: Exchange Creation Failed

**Symptoms**:
- `create_topic()` method returns `False`
- Error message: `Exchange already exists` or `Access refused`

**Possible Causes**:
1. Exchange already exists with different parameters
2. Insufficient permissions to create exchanges
3. Invalid exchange name
4. Channel closed due to previous errors

**Troubleshooting Steps**:
1. Check if the exchange already exists:
   ```python
   # Try to declare the exchange passively
   try:
       rabbitmq_provider.channel.exchange_declare(
           exchange='my-exchange',
           passive=True
       )
       print("Exchange 'my-exchange' already exists")
   except Exception as e:
       print(f"Exchange does not exist or error: {str(e)}")
   ```

2. Check exchange name validity:
   ```python
   # Exchange names should not contain characters like '/', '\', '.', ',', ' '
   import re
   exchange_name = 'my-exchange'
   if re.search(r'[/\\., ]', exchange_name):
       print(f"Invalid exchange name: {exchange_name}")
   ```

3. Check channel status:
   ```python
   print(f"Channel is open: {rabbitmq_provider.channel.is_open}")
   ```

**Solution**:
```python
# Create exchange with valid configuration
try:
    # Ensure channel is open
    if not rabbitmq_provider.channel.is_open:
        rabbitmq_provider.channel = rabbitmq_provider.connection.channel()
    
    # Create exchange with valid name
    success = await rabbitmq_provider.create_topic(
        topic_name='valid-exchange-name'
    )
    print(f"Exchange creation {'succeeded' if success else 'failed'}")
except Exception as e:
    print(f"Error creating exchange: {str(e)}")
```

### RabbitMQ Publishing Issues

#### Issue: Message Publishing Failed

**Symptoms**:
- `publish_message()` method returns `False`
- Error message: `Channel closed` or `Exchange not found`

**Possible Causes**:
1. Exchange doesn't exist
2. Channel closed due to previous errors
3. Message cannot be serialized
4. Network issues during publishing

**Troubleshooting Steps**:
1. Verify that the exchange exists:
   ```python
   try:
       rabbitmq_provider.channel.exchange_declare(
           exchange='my-exchange',
           passive=True
       )
       print("Exchange 'my-exchange' exists")
   except Exception as e:
       print(f"Exchange does not exist or error: {str(e)}")
   ```

2. Check channel status:
   ```python
   print(f"Channel is open: {rabbitmq_provider.channel.is_open}")
   ```

3. Check message serialization:
   ```python
   import json
   
   message = {'key': 'value', 'complex': {'nested': 'value'}}
   try:
       json_str = json.dumps(message)
       print(f"Message serialization successful: {json_str}")
   except Exception as e:
       print(f"Message serialization failed: {str(e)}")
   ```

**Solution**:
```python
# Ensure exchange exists and channel is open before publishing
try:
    # Ensure channel is open
    if not rabbitmq_provider.channel.is_open:
        rabbitmq_provider.channel = rabbitmq_provider.connection.channel()
    
    # Ensure exchange exists
    try:
        rabbitmq_provider.channel.exchange_declare(
            exchange='my-exchange',
            passive=True
        )
    except Exception:
        # Create exchange if it doesn't exist
        await rabbitmq_provider.create_topic('my-exchange')
    
    # Publish message
    message = {'key': 'value', 'timestamp': '2023-08-01T12:00:00Z'}
    success = await rabbitmq_provider.publish_message(
        topic_name='my-exchange',
        message=message,
        key='routing-key'
    )
    print(f"Message publishing {'succeeded' if success else 'failed'}")
except Exception as e:
    print(f"Error publishing message: {str(e)}")
```

### RabbitMQ Consumption Issues

#### Issue: No Messages Consumed

**Symptoms**:
- `consume_messages()` returns 0
- No messages are processed by the callback function
- `consume_to_dataframe()` returns an empty DataFrame

**Possible Causes**:
1. No messages in the queue
2. Queue not bound to the exchange
3. Routing key mismatch
4. Channel closed due to previous errors
5. Timeout too short

**Troubleshooting Steps**:
1. Check if the queue is bound to the exchange:
   ```python
   # Declare queue and bind it to the exchange
   result = rabbitmq_provider.channel.queue_declare(queue='test-queue', durable=True)
   queue_name = result.method.queue
   
   rabbitmq_provider.channel.queue_bind(
       exchange='my-exchange',
       queue=queue_name,
       routing_key='#'  # Bind to all routing keys
   )
   
   print(f"Queue '{queue_name}' bound to exchange 'my-exchange'")
   ```

2. Check channel status:
   ```python
   print(f"Channel is open: {rabbitmq_provider.channel.is_open}")
   ```

3. Publish a test message:
   ```python
   # Publish a test message
   rabbitmq_provider.channel.basic_publish(
       exchange='my-exchange',
       routing_key='test',
       body=json.dumps({'test': 'message'}).encode('utf-8'),
       properties=pika.BasicProperties(
           content_type='application/json',
           delivery_mode=2
       )
   )
   print("Test message published")
   ```

4. Increase timeout:
   ```python
   # Use a longer timeout
   timeout_ms = 30000  # 30 seconds
   print(f"Using timeout: {timeout_ms}ms")
   ```

**Solution**:
```python
# Ensure queue is bound to exchange and use longer timeout
try:
    # Ensure channel is open
    if not rabbitmq_provider.channel.is_open:
        rabbitmq_provider.channel = rabbitmq_provider.connection.channel()
    
    # Declare queue and bind it to the exchange
    queue_name = 'test-queue'
    result = rabbitmq_provider.channel.queue_declare(queue=queue_name, durable=True)
    
    rabbitmq_provider.channel.queue_bind(
        exchange='my-exchange',
        queue=queue_name,
        routing_key='#'  # Bind to all routing keys
    )
    
    # Publish a test message
    rabbitmq_provider.channel.basic_publish(
        exchange='my-exchange',
        routing_key='test',
        body=json.dumps({'test': 'message'}).encode('utf-8'),
        properties=pika.BasicProperties(
            content_type='application/json',
            delivery_mode=2
        )
    )
    
    # Consume messages with longer timeout
    messages_consumed = await rabbitmq_provider.consume_messages(
        topic_name='my-exchange',
        group_id=queue_name,
        callback=lambda msg: print(f"Received: {msg}"),
        max_messages=10,
        timeout_ms=30000  # 30 seconds
    )
    print(f"Consumed {messages_consumed} messages")
except Exception as e:
    print(f"Error consuming messages: {str(e)}")
```

## General Troubleshooting Tips

### Checking Provider Initialization

Always check if the provider is properly initialized before using it:

```python
if not kafka_provider.is_initialized:
    print("Kafka provider not initialized")
    # Try to initialize again
    success = await kafka_provider.initialize()
    if not success:
        print("Failed to initialize Kafka provider")
        # Handle initialization failure
```

### Debugging Asynchronous Code

When debugging asynchronous code, use try-except blocks and print statements to track the flow:

```python
async def debug_kafka_operations():
    try:
        print("Initializing Kafka provider...")
        success = await kafka_provider.initialize()
        print(f"Initialization {'succeeded' if success else 'failed'}")
        
        if success:
            print("Listing topics...")
            topics = await kafka_provider.list_topics()
            print(f"Found {len(topics)} topics: {[t['name'] for t in topics]}")
            
            print("Creating topic...")
            success = await kafka_provider.create_topic('debug-topic', partitions=1, replication_factor=1)
            print(f"Topic creation {'succeeded' if success else 'failed'}")
            
            print("Publishing message...")
            success = await kafka_provider.publish_message('debug-topic', {'debug': 'message'})
            print(f"Message publishing {'succeeded' if success else 'failed'}")
    except Exception as e:
        print(f"Error during Kafka operations: {str(e)}")
        import traceback
        traceback.print_exc()
```

### Handling Serialization Issues

When dealing with complex data structures, ensure they can be serialized to JSON:

```python
def ensure_serializable(data):
    """
    Ensure that data can be serialized to JSON.
    
    Args:
        data: Data to check
        
    Returns:
        Serializable version of the data
    """
    try:
        # Try to serialize to JSON
        json.dumps(data)
        return data
    except (TypeError, ValueError) as e:
        print(f"Serialization error: {str(e)}")
        
        # Convert to serializable format
        if isinstance(data, dict):
            return {k: ensure_serializable(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [ensure_serializable(item) for item in data]
        elif isinstance(data, (set, tuple)):
            return [ensure_serializable(item) for item in data]
        elif hasattr(data, '__dict__'):
            return ensure_serializable(data.__dict__)
        elif hasattr(data, 'isoformat'):  # Handle datetime objects
            return data.isoformat()
        else:
            return str(data)  # Convert to string as a last resort
```

Use this function before publishing messages:

```python
# Ensure message is serializable
message = ensure_serializable(complex_data)
success = await kafka_provider.publish_message('my-topic', message)
```

By following these troubleshooting steps, you should be able to identify and resolve most issues with the Kafka and RabbitMQ connectors in the Science Data Kit.