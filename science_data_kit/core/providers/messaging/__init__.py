"""
Messaging Providers for Science Data Kit

This package provides providers for connecting to messaging systems like Kafka and RabbitMQ,
allowing the Science Data Kit to interact with message brokers for streaming data.
"""

# Import providers
from .kafka_provider import KafkaProvider
from .rabbitmq_provider import RabbitMQProvider

__all__ = ['KafkaProvider', 'RabbitMQProvider']
