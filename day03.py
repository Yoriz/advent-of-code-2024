from typing import Iterator
import dataclasses
from enum import Enum
import string


FILENAME = "day03_data.txt"


def yield_characters(filename: str) -> Iterator[str]:
    with open(file=filename, mode="r") as read_file:
        for line in read_file:
            striped_line = line.strip()
            for character in striped_line:
                yield character


DIGITS = string.digits
OPEN_BRACKET = "("
CLOSE_BRACKET = ")"
SEPERATOR = ","


class MemoryPart(Enum):
    PREFIX = 1
    NUMBER1 = 2
    NUMBER2 = 3
    DO = 4
    DONT = 5


@dataclasses.dataclass
class Prefix:
    letters: list[str] = dataclasses.field(default_factory=list)

    def add_letter(self, letter: str) -> None:
        self.letters.append(letter)

    def is_mul(self) -> bool:
        return self.letters[-3:] == ["m", "u", "l"]

    def is_do(self) -> bool:
        return self.letters[-2:] == ["d", "o"]

    def is_dont(self) -> bool:
        return self.letters[-5:] == ["d", "o", "n", "'", "t"]


@dataclasses.dataclass
class Number:
    numbers: list[str] = dataclasses.field(default_factory=list)

    def add_number(self, number: str):
        self.numbers.append(number)

    def get_number(self) -> int:
        return int("".join(self.numbers))


@dataclasses.dataclass
class MemoryParser:
    prefix: Prefix = dataclasses.field(default_factory=Prefix)
    number1: Number = dataclasses.field(default_factory=Number)
    number2: Number = dataclasses.field(default_factory=Number)
    use_conditional: bool = False

    def __post_init__(self):
        self.memory_part = MemoryPart.PREFIX
        self.total = 0
        self.counter = 0
        self.enabled = True

    def reset(self):
        self.prefix = Prefix()
        self.number1 = Number()
        self.number2 = Number()
        self.memory_part = MemoryPart.PREFIX

    def add_character(self, character: str):
        match self.memory_part:
            case MemoryPart.PREFIX if character == OPEN_BRACKET:
                if self.prefix.is_mul() and self.enabled:
                    self.memory_part = MemoryPart.NUMBER1
                elif self.prefix.is_do() and self.use_conditional:
                    self.memory_part = MemoryPart.DO
                elif self.prefix.is_dont() and self.use_conditional:
                    self.memory_part = MemoryPart.DONT
                else:
                    self.reset()
            case MemoryPart.NUMBER1 if character == SEPERATOR:
                self.memory_part = MemoryPart.NUMBER2
            case MemoryPart.NUMBER1 if character not in DIGITS:
                self.reset()
            case MemoryPart.NUMBER2 if character == CLOSE_BRACKET:
                self.counter += 1
                # print(
                #     f"{self.counter}: {self.prefix.letters}, {self.number1.get_number()}, {self.number2.get_number()}"
                # )
                self.total += self.number1.get_number() * self.number2.get_number()
                self.reset()
            case MemoryPart.NUMBER2 if character not in DIGITS:
                self.reset()
            case MemoryPart.NUMBER1 if character in DIGITS:
                self.number1.add_number(character)
            case MemoryPart.NUMBER2 if character in DIGITS:
                self.number2.add_number(character)
            case MemoryPart.PREFIX:
                self.prefix.add_letter(character)
            case MemoryPart.DO:
                self.enabled = True
                self.reset()
            case MemoryPart.DONT:
                self.enabled = False
                self.reset()


def part_one() -> int:
    characters = yield_characters(FILENAME)
    memory_parser = MemoryParser()
    for character in characters:
        memory_parser.add_character(character)

    return memory_parser.total


def part_two() -> int:
    characters = yield_characters(FILENAME)
    memory_parser = MemoryParser(use_conditional=True)
    for character in characters:
        memory_parser.add_character(character)

    return memory_parser.total


def main():
    print(f"Part one: {part_one()}")
    print(f"Part two: {part_two()}")


if __name__ == "__main__":
    main()
