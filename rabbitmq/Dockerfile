# Use the official RabbitMQ image
FROM rabbitmq:management

# Copy the initialization script
COPY init-rabbitmq.sh /init-rabbitmq.sh

# Make the script executable
RUN chmod +x /init-rabbitmq.sh

# Use the custom script as the entrypoint
ENTRYPOINT ["/init-rabbitmq.sh"]
