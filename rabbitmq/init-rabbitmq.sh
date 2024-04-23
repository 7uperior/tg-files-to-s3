#!/bin/bash
# Wait for RabbitMQ server to start
sleep 10

echo "Creating new user and setting permissions..."
rabbitmqctl add_user "$RABBITMQ_USER" "$RABBITMQ_PASSWORD"
rabbitmqctl set_user_tags "$RABBITMQ_USER" administrator
rabbitmqctl set_permissions -p / "$RABBITMQ_USER" ".*" ".*" ".*"

echo "Complete setup."

# Continue with the normal entrypoint
exec docker-entrypoint.sh rabbitmq-server
