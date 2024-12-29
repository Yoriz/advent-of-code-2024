import dataclasses
import typing


TEST_FILENAME = "day19_testdata.txt"
FILENAME = "day19_data.txt"


def yield_data(filename: str) -> typing.Iterator[str]:
    with open(file=filename, mode="r") as read_file:
        for line in read_file:
            yield line.strip()


@dataclasses.dataclass
class Onsen:
    patterns: set[str] = dataclasses.field(default_factory=set)
    designs: list[str] = dataclasses.field(default_factory=list)
    cache: dict[str, int] = dataclasses.field(default_factory=dict)

    def patterns_in_design(self, design: str) -> int:
        if design not in self.cache:
            if len(design) == 0:
                return 1
            else:
                result = 0
                for pattern in self.patterns:
                    if design.startswith(pattern):
                        result += self.patterns_in_design(design[len(pattern) :])

                self.cache[design] = result

        return self.cache[design]

    def possible_patterns(self, count_all_ways: bool = False) -> int:
        pattern_qty = 0
        for design in self.designs:
            print(f"{design=}")
            patterns_qty = self.patterns_in_design(design)
            if not count_all_ways and patterns_qty > 0:
                pattern_qty += 1
            else:
                pattern_qty += patterns_qty

        return pattern_qty


def create_onsen(data: typing.Iterator[str]) -> Onsen:
    patterns_string = next(data)
    _ = next(data)
    patterns = set(patterns_string.split(", "))
    designs: list[str] = []
    for line in data:
        designs.append(line)
    return Onsen(patterns=patterns, designs=designs)


def part_one() -> int:
    data = yield_data(FILENAME)
    onsen = create_onsen(data)
    possible_patterns = onsen.possible_patterns()
    return possible_patterns


def part_two() -> int:
    data = yield_data(FILENAME)
    onsen = create_onsen(data)
    possible_patterns = onsen.possible_patterns(True)
    return possible_patterns


def main() -> None:
    print(f"Part one: {part_one()}")
    print(f"Part two: {part_two()}")
    return None


if __name__ == "__main__":
    main()
