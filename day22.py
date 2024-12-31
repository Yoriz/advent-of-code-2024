import typing
import functools


TEST_FILENAME = "day22_testdata.txt)
FILENAME = "day22_data.txt"


def yield_data(filename: str) -> typing.Iterator[str]:
    with open(file=filename, mode="r") as read_file:
        for line in read_file:
            yield line.strip()


@functools.cache
def mix(secret_number: int, mix_number: int) -> int:
    return secret_number ^ mix_number


@functools.cache
def prune(secret_number: int) -> int:
    return secret_number % 16777216


@functools.cache
def mix_and_prune(secret_number: int, mix_number: int) -> int:
    result = mix(secret_number, mix_number)
    return prune(result)


@functools.cache
def evolve_secret_number(secret_number: int) -> int:
    result = secret_number * 64
    secret_number = mix_and_prune(secret_number, result)
    result = secret_number // 32
    secret_number = mix_and_prune(secret_number, result)
    result = secret_number * 2048
    secret_number = mix_and_prune(secret_number, result)

    return secret_number


def part_one() -> int:
    data = yield_data(FILENAME)
    total = 0
    for line in data:
        secret_number = int(line)

        for _ in range(2000):
            secret_number = evolve_secret_number(secret_number)

        total += secret_number

    return total


def part_two() -> int:
    data = yield_data(TEST_FILENAME)

    return 0


def main() -> None:
    print(f"Part one: {part_one()}")
    # print(f"Part two: {part_two()}")
    return None


if __name__ == "__main__":
    main()
