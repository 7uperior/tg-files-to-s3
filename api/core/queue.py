"""This module is concerned with rabbitmq connection."""

import json
import os
from typing import AsyncGenerator, Awaitable, Callable

import aio_pika
from aio_pika import Channel, Connection, Message

# Load environment variables
RABBITMQ_USER = os.getenv('RABBITMQ_USER')
RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD')
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST')
RABBITMQ_PORT = os.getenv('RABBITMQ_PORT')
# Construct the RabbitMQ connection URL
RABBITMQ_URL = f'amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}:{RABBITMQ_PORT}/'


# Function to connect to RabbitMQ
async def connect_to_rabbit() -> Connection:
	return await aio_pika.connect_robust(RABBITMQ_URL)


# Async generator to manage the RabbitMQ publisher lifecycle
async def get_publisher(queue: str = 'files') -> AsyncGenerator[Callable[[dict], Awaitable[None]], None]:
	connection: Connection = await connect_to_rabbit()
	channel: Channel = await connection.channel()

	await channel.declare_queue(queue)

	async def publish_message(message: dict) -> None:
		"""Publish a message to RabbitMQ."""
		try:
			await channel.default_exchange.publish(Message(body=json.dumps(message).encode()), routing_key=queue)
		except Exception as e:
			print(f'Failed to publish message: {e}')

	try:
		yield publish_message
	finally:
		await channel.close()
		await connection.close()
