import dataclasses
import typing


FILENAME = "day11_data.txt"


def yield_data(filename: str) -> typing.Iterator[str]:
    with open(file=filename, mode="r") as read_file:
        for line in read_file:
            yield line.strip()


@dataclasses.dataclass(slots=True)
class Stone:
    number: int
    amount: int = 1

    def apply_rule(self, multiply_by: int = 2024) -> list["Stone"]:
        num_str = str(self.number)
        match num_str:
            case "0":
                return [Stone(number=1, amount=self.amount)]

            case num_str if len(num_str) % 2 == 0:
                mid_index = len(num_str) // 2
                left_number = int(num_str[:mid_index])
                right_number = int(num_str[mid_index:])
                return [
                    Stone(number=left_number, amount=self.amount),
                    Stone(number=right_number, amount=self.amount),
                ]

            case _:
                number = self.number * multiply_by
                return [Stone(number=number, amount=self.amount)]


@dataclasses.dataclass
class Stones:
    stones: dict[int, Stone] = dataclasses.field(default_factory=dict)

    def append(self, stone: Stone) -> None:
        if stone.number in self.stones:
            self.stones[stone.number].amount += stone.amount
            return None
        self.stones[stone.number] = stone
        return None

    def blink(self) -> None:
        old_stones = self.stones.copy()
        self.stones.clear()
        for stone in old_stones.values():
            new_stones = stone.apply_rule()
            for new_stone in new_stones:
                self.append(new_stone)
        return None

    def stone_qty(self) -> int:
        return sum(stone.amount for stone in self.stones.values())

    def __str__(self) -> str:
        return " ".join(
            f"{stone.number}:{stone.amount}" for stone in self.stones.values()
        )


def create_stones(data: typing.Iterator[str]) -> Stones:
    stones = Stones()
    for line in data:
        number_strs = line.split(" ")
        for number_str in number_strs:
            number = int(number_str)
            stones.append(Stone(number=number))
    return stones


def part_one() -> int:
    data = yield_data(FILENAME)
    stones = create_stones(data)
    for _ in range(25):
        stones.blink()
    return stones.stone_qty()


def part_two() -> int:
    data = yield_data(FILENAME)
    stones = create_stones(data)
    for _ in range(75):
        stones.blink()
    return stones.stone_qty()


def main() -> None:
    print(f"Part one: {part_one()}")
    print(f"Part two: {part_two()}")


if __name__ == "__main__":
    main()
