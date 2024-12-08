import dataclasses
import enum
from typing import Iterator
import typing
import string
import collections
import itertools


FILENAME = "day08_data.txt"


def yield_data(filename: str) -> Iterator[str]:
    with open(file=filename, mode="r") as read_file:
        for line in read_file:
            yield line.strip()


FREQUENCY_CHARACTERS = "".join(
    (string.ascii_lowercase, string.ascii_uppercase, string.digits)
)


class LocationType(enum.Enum):
    ANTENNA = enum.auto()
    EMPTY = enum.auto()
    OUT_OF_BOUNDS = enum.auto()
    ANTINODE = enum.auto()


class LocationCharacter(enum.Enum):
    EMPTY = "."
    OUT_OF_BOUNDS = "@"
    ANTINODE = "#"


@dataclasses.dataclass(slots=True, frozen=True)
class Location:
    x: int
    y: int

    def differance(self, other: "Location") -> "Location":
        return Location(self.x - other.x, self.y - other.y)

    def offset_by(self, differance: "Location") -> "Location":
        return Location(self.x + differance.x, self.y + differance.y)


@dataclasses.dataclass
class GridLocation:
    location: Location
    value: str
    location_type: LocationType

    @property
    def x(self) -> int:
        return self.location.x

    @property
    def y(self) -> int:
        return self.location.y


@dataclasses.dataclass
class Grid:
    grid_locations: dict[tuple[int, int], GridLocation] = dataclasses.field(
        default_factory=dict
    )
    frquencies: dict[str, list[GridLocation]] = dataclasses.field(
        default_factory=lambda: collections.defaultdict(list)
    )
    antinode_grid_locations: dict[tuple[int, int], GridLocation] = dataclasses.field(
        default_factory=dict
    )
    max_x_location: int = 0
    max_y_location: int = 0

    def add_grid_location(self, grid_location: GridLocation) -> None:
        match grid_location.location_type:
            case LocationType.ANTENNA:
                self.grid_locations[(grid_location.x, grid_location.y)] = grid_location
                self.frquencies[grid_location.value].append(grid_location)
                self.update_max_values(grid_location.location)
            case LocationType.ANTINODE:
                self.antinode_grid_locations[(grid_location.x, grid_location.y)] = (
                    grid_location
                )
            case _:
                self.update_max_values(grid_location.location)

        return None

    def update_max_values(self, location: Location) -> None:
        self.max_x_location = max(self.max_x_location, location.x)
        self.max_y_location = max(self.max_y_location, location.y)

    def get_grid_location(self, location: Location) -> GridLocation:
        grid_location = GridLocation(
            location, LocationCharacter.EMPTY.value, LocationType.EMPTY
        )
        if not self.location_in_grid(location):
            grid_location.value = LocationCharacter.EMPTY.value
            grid_location.location_type = LocationType.EMPTY
            return grid_location

        grid_location = self.antinode_grid_locations.get(
            (location.x, location.y), grid_location
        )

        grid_location = self.grid_locations.get((location.x, location.y), grid_location)

        return grid_location

    def location_in_grid(self, location: Location) -> bool:
        return all(
            (
                location.x > -1,
                location.x < self.max_x_location + 1,
                location.y > -1,
                location.y < self.max_y_location + 1,
            )
        )

    def get_frequency_pairs(
        self, frequency_value: str
    ) -> list[tuple[GridLocation, GridLocation]]:
        frequency_pairs: list[tuple[GridLocation, GridLocation]] = []
        for frequency1, frequency2 in itertools.combinations(
            self.frquencies[frequency_value], 2
        ):
            frequency_pairs.append((frequency1, frequency2))

        return frequency_pairs

    def create_antinode(
        self, frequency_value: str, resonant_harmonics: bool = False
    ) -> None:
        frequency_pairs = self.get_frequency_pairs(frequency_value)
        for frequency1, frequency2 in frequency_pairs:
            if resonant_harmonics:
                self.add_grid_location(
                    GridLocation(
                        frequency1.location,
                        LocationCharacter.ANTINODE.value,
                        LocationType.ANTINODE,
                    )
                )
                self.add_grid_location(
                    GridLocation(
                        frequency2.location,
                        LocationCharacter.ANTINODE.value,
                        LocationType.ANTINODE,
                    )
                )
            for frequency1, frequency2 in (
                (frequency1, frequency2),
                (frequency2, frequency1),
            ):

                location_difference = frequency1.location.differance(
                    frequency2.location
                )
                location = frequency1.location
                location = location.offset_by(location_difference)

                while self.location_in_grid(location):
                    self.add_grid_location(
                        GridLocation(
                            location,
                            LocationCharacter.ANTINODE.value,
                            LocationType.ANTINODE,
                        )
                    )
                    if not resonant_harmonics:
                        break
                    location = location.offset_by(location_difference)

        return None

    def create_antinodes(self, resonant_harmonics: bool = False) -> None:
        for frequency_value in self.frquencies.keys():
            self.create_antinode(frequency_value, resonant_harmonics)

        return None

    def __str__(self) -> str:
        rows: list[str] = []
        for y_index in range(self.max_y_location + 1):
            row = ""
            for x_index in range(self.max_x_location + 1):
                location = Location(x_index, y_index)
                grid_location = self.get_grid_location(location)
                row = f"{row}{grid_location.value}"
            rows.append(row)
        return "\n".join(rows)


def create_map(data: typing.Iterator[str]) -> Grid:
    grid = Grid()
    for y_index, line in enumerate(data):
        for x_index, character in enumerate(line):
            location = Location(x_index, y_index)

            match character:
                case character if character in FREQUENCY_CHARACTERS:
                    location_type = LocationType.ANTENNA
                    value = character
                case LocationCharacter.EMPTY.value:
                    location_type = LocationType.EMPTY
                    value = LocationCharacter.EMPTY.value
                case _:
                    raise ValueError(f"Invalid character: {character}")

            grid_location = GridLocation(location, value, location_type)
            grid.add_grid_location(grid_location)

    return grid


def part_one() -> int:
    data = yield_data(FILENAME)
    grid = create_map(data)
    grid.create_antinodes()
    return len(grid.antinode_grid_locations)


def part_two() -> int:
    data = yield_data(FILENAME)
    grid = create_map(data)
    grid.create_antinodes(True)
    return len(grid.antinode_grid_locations)


def main() -> None:
    print(f"Part one: {part_one()}")
    print(f"Part two: {part_two()}")


if __name__ == "__main__":
    main()
