import os
import glob
import minizinc
import pprint
import logging
import pika
from pprint import pprint
from minizinc import Status, Solver, Result

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def solve(solver: str, problem: str, instance: str) -> Result:
    """
    Solver examples: coinbc, gecode
    """
    try:
        solver = Solver.lookup(solver)
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
    return instance.solve()


def problem_instances_from_file(path: str) -> tuple[str, list[str]]:
    problem = glob.glob(f"{path}/*.mzn")[0]
    instances = glob.glob(f"{path}/*.dzn")
    print(f"loaded {len(instances)} instances")
    return problem, instances


def print_result(result: Result) -> None:
    # pprint(result, depth=None, width=80)
    status = result.status
    status_str = None
    if status == Status.ERROR or status == Status.UNKNOWN:
        status_str = "error"
        print(f"Status: {status_str}")
        return
    elif status == Status.UNBOUNDED:
        status_str = "unbounded"
        print(f"Status: {status_str}")
        return
    elif status == Status.UNSATISFIABLE:
        status_str = "unsatisfiable"
        print(f"Status: {status_str}")
        return

    if status == Status.OPTIMAL_SOLUTION:
        status_str = "optimal"
    elif status == Status.SATISFIED:
        status_str = "satisfied"
    elif status == Status.ALL_SOLUTIONS:
        status_str = "all solutions"

    print("Status:", status_str)
    print("Solve time:", result.statistics["solveTime"])
    print("Total time:", result.statistics["time"])
    print("Solution:")
    print(result.solution)


if __name__ == "__main__":
    problem, instances = problem_instances_from_file("../problems/nfc")
    result = solve("coinbc", problem, instances[0])
    print()
    print_result(result)


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
