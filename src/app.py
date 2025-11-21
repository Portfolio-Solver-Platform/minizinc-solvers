import os
import logging
import pika

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def solve_problem(problem: str):
    logger.info(f"Solving problem: {problem}")


def main():
    solver_type = os.getenv("SOLVER_TYPE")
    queue_name = os.getenv("QUEUE_NAME")
    rabbitmq_host = os.getenv("RABBITMQ_HOST")
    rabbitmq_port = int(os.getenv("RABBITMQ_PORT", "5672"))
    rabbitmq_user = os.getenv("RABBITMQ_USER")
    rabbitmq_password = os.getenv("RABBITMQ_PASSWORD")

    if not all([solver_type, queue_name, rabbitmq_host, rabbitmq_user, rabbitmq_password]):
        raise ValueError("Missing required environment variables")

    logger.info(f"Starting solver: {solver_type}")
    logger.info(f"Listening to queue: {queue_name}")

    credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
    parameters = pika.ConnectionParameters(
        host=rabbitmq_host,
        port=rabbitmq_port,
        credentials=credentials,
        heartbeat=600,
        blocked_connection_timeout=300,
    )

    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    channel.queue_declare(queue=queue_name, durable=True)

    def callback(ch, method, properties, body):
        problem = body.decode('utf-8')
        solve_problem(problem)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue_name, on_message_callback=callback)

    logger.info("Solver ready, waiting for problems")
    channel.start_consuming()


if __name__ == "__main__":
    main()
