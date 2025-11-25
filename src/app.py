import os
import glob
import minizinc
import pprint
import logging
import pika

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def solve(solver: str, problem: str, instance: str):
    """
    Solver examples: coinbc, gecode
    """
    try:
        solver = minizinc.Solver.lookup(solver)
    except Exception as e:
        print(
            "Failed to find solver. Make sure minizinc is installed on the system, and the solver name is correct."
        )
        raise e

    print("Loading model")
    model = minizinc.Model(problem)

    print("Adding instance")
    model.add_file(instance)

    print("Create instance")
    instance = minizinc.Instance(solver, model)

    print("Solving...")
    result = instance.solve()
    pprint.pprint(result, depth=None, width=80)
    print("Status:", result.status)
    if result.solution is not None:
        print(result.solution)
        print()
        print()
        print(dict(result))
        print()
        print()
        if result.objective is not None:
            print("Objective:", result.objective)
    else:
        print("No solution found.")


def solve_from_file(solver: str, path: str):
    instances = glob.glob(f"{path}/*.dzn")
    problem = glob.glob(f"{path}/*.mzn")[0]
    print(f"loaded {len(instances)} instances")
    for instance in instances:
        solve(solver, problem, instance)


if __name__ == "__main__":
    solve_from_file("gecode", "../problems/nfc")


def main():
    solver_type = os.getenv("SOLVER_TYPE")
    queue_name = os.getenv("QUEUE_NAME")
    rabbitmq_host = os.getenv("RABBITMQ_HOST")
    rabbitmq_port = int(os.getenv("RABBITMQ_PORT", "5672"))
    rabbitmq_user = os.getenv("RABBITMQ_USER")
    rabbitmq_password = os.getenv("RABBITMQ_PASSWORD")

    if not all(
        [solver_type, queue_name, rabbitmq_host, rabbitmq_user, rabbitmq_password]
    ):
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
        problem = body.decode("utf-8")
        solve_problem(problem)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue_name, on_message_callback=callback)

    logger.info("Solver ready, waiting for problems")
    channel.start_consuming()


# if __name__ == "__main__":
#     main()
