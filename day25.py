import typing
import dataclasses


TEST_FILENAME = "day25_testdata.txt"
FILENAME = "day25_data.txt"


def yield_data(filename: str) -> typing.Iterator[str]:
    with open(file=filename, mode="r") as read_file:
        for line in read_file:
            yield line.strip()


@dataclasses.dataclass
class Lock:
    pin_heights: list[int] = dataclasses.field(default_factory=list)

    def key_fits(self, key: "Key") -> bool:
        for key_height, lock_height in zip(key.pin_heights, self.pin_heights):
            if key_height + lock_height > 5:
                return False

        return True


@dataclasses.dataclass
class Key:
    pin_heights: list[int] = dataclasses.field(default_factory=list)


def create_locks_and_keys(data: typing.Iterator[str]) -> tuple[list[Lock], list[Key]]:
    locks: list[Lock] = []
    keys: list[Key] = []
    line_index: int = 0
    for line in data:
        match line_index:
            case 0:
                is_lock = line.startswith("#####")
                heights = [0, 0, 0, 0, 0]
                line_index += 1
            case 1 | 2 | 3 | 4 | 5:
                for index, char in enumerate(line):
                    if char == "#":
                        heights[index] += 1
                line_index += 1
            case 6:
                if is_lock:
                    locks.append(Lock(heights))
                else:
                    keys.append(Key(heights))
                line_index += 1
            case 7:
                line_index = 0

    return locks, keys


def part_one() -> int:
    data = yield_data(FILENAME)
    locks, keys = create_locks_and_keys(data)
    qty_fit: int = 0
    for key in keys:
        for lock in locks:
            if lock.key_fits(key):
                qty_fit += 1
    return qty_fit


def part_two() -> int:
    data = yield_data(TEST_FILENAME)

    return 0


def main() -> None:
    print(f"Part one: {part_one()}")
    # print(f"Part two: {part_two()}")
    return None


if __name__ == "__main__":
    main()
