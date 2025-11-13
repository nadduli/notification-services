# publish_test_email.py
import json
import uuid

import pika

connection = pika.BlockingConnection(
    pika.URLParameters("amqp://guest:guest@localhost:5672/")
)
channel = connection.channel()

# make sure exchange exists (same name as your config)
channel.exchange_declare(exchange="notifications.direct", exchange_type="direct", durable=True)

request_id = "test-req-001"
user_id = str(uuid.uuid4())

message = {
    "notification_type": "email",
    "user_id": user_id,
    "template_code": "welcome_v1",
    "variables": {
        "name": "Test User",
        "link": "https://example.com",
        "meta": {}
    },
    "request_id": request_id,
    "priority": 5,
    "metadata": {
        "recipient_email": "someone@example.com",
        "locale": "en",
        "correlation_id": "corr-123",
        "extra": {}
    }
}

channel.basic_publish(
    exchange="notifications.direct",
    routing_key="email",
    body=json.dumps(message),
    properties=pika.BasicProperties(
        content_type="application/json",
        headers={
            "x-request-id": request_id,
            "x-correlation-id": "corr-123",
            "x-user-id": user_id,
            "x-retry-attempt": 0,
        },
    ),
)

print("Message sent!")
connection.close()