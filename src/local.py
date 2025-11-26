from zinc import print_result, solve
import glob


def problem_instances_from_file(path: str) -> tuple[str, list[str]]:
    problem = glob.glob(f"{path}/*.mzn")[0]
    instances = glob.glob(f"{path}/*.dzn")
    print(f"loaded {len(instances)} instances")
    return problem, instances


if __name__ == "__main__":
    problem, instances = problem_instances_from_file("../problems/nfc")
    result = solve("coinbc", problem, instances[0])
    print()
    print_result(result)
