# Email Service

A microservice for handling email notifications as part of a distributed notification system.

## Features

- Consumes messages from RabbitMQ email queue
- Sends emails using SMTP with retry mechanism
- Circuit breaker pattern for fault tolerance
- Template-based email generation
- Health checks and monitoring
- PostgreSQL for data persistence
- Docker containerization

## Setup

1. Copy `.env.example` to `.env` and configure your settings
2. Run `docker-compose up` to start all services
3. The service will be available at `http://localhost:8002`

## API Endpoints

- `GET /` - Service status
- `GET /api/v1/health` - Health check
- `GET /api/v1/notifications` - List email notifications
- `GET /api/v1/notifications/{id}` - Get specific notification
- `POST /api/v1/status` - Update notification status

## Message Format

The service expects messages in the following format:

```json
{
  "notification_type": "email",
  "user_id": "uuid",
  "template_code": "welcome_email",
  "variables": {
    "name": "John Doe",
    "link": "https://example.com"
  },
  "request_id": "unique_request_id",
  "priority": 1
}