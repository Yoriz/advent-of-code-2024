from typing import Iterator
import dataclasses
import enum


FILENAME = "day04_data.txt"


def yield_data(filename: str) -> Iterator[str]:
    with open(file=filename, mode="r") as read_file:
        for line in read_file:
            yield line.strip()


class LocationType(enum.Enum):
    LETTER = enum.auto()
    OUT_OF_BOUNDS = enum.auto()


@dataclasses.dataclass(slots=True, frozen=True)
class Location:
    x: int
    y: int

    def neighbour_location(self, location_direction: "LocationDirection") -> "Location":
        other_location: "Location" = location_direction.value
        return Location(self.x + other_location.x, self.y + other_location.y)


@enum.unique
class LocationDirection(enum.Enum):
    UP = Location(0, -1)
    UP_RIGHT = Location(1, -1)
    RIGHT = Location(1, 0)
    DOWN_RIGHT = Location(1, 1)
    DOWN = Location(0, 1)
    DOWN_LEFT = Location(-1, 1)
    LEFT = Location(-1, 0)
    UP_LEFT = Location(-1, -1)


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
class Map:
    grid_locations: dict[tuple[int, int], GridLocation] = dataclasses.field(
        default_factory=dict
    )
    max_x_location: int = 0
    max_y_location: int = 0

    def add_grid_location(self, grid_location: GridLocation) -> None:
        self.grid_locations[(grid_location.x, grid_location.y)] = grid_location
        self.update_max_values(grid_location.location)

        return None

    def update_max_values(self, location: Location) -> None:
        self.max_x_location = max(self.max_x_location, location.x)
        self.max_y_location = max(self.max_y_location, location.y)

    def get_grid_location(self, location: Location) -> GridLocation:
        if not self.location_in_grid(location):
            return GridLocation(location, "", LocationType.OUT_OF_BOUNDS)
        grid_location = self.grid_locations.get((location.x, location.y))
        if not grid_location:
            raise ValueError("GridLocation not found")

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


def create_map(data: Iterator[str]) -> Map:
    map = Map()
    for y_index, line in enumerate(data):
        for x_index, character in enumerate(line):
            location = Location(x_index, y_index)
            grid_location = GridLocation(location, character, LocationType.LETTER)
            map.add_grid_location(grid_location)
    return map


@dataclasses.dataclass
class GridWordFinder:
    map: Map
    word: str
    location: Location
    location_directions: list[LocationDirection] = dataclasses.field(
        default_factory=list
    )
    found_words: list[tuple[Location, LocationDirection]] = dataclasses.field(
        default_factory=list
    )

    def find_word_directions(self) -> None:
        if not self.location_directions:
            return

        grid_location = self.map.get_grid_location(self.location)
        if self.word[0] != grid_location.value:
            return

        for location_direction in self.location_directions:
            location = self.location
            for letter in self.word[1:]:
                neighbour_location = location.neighbour_location(location_direction)
                grid_location = self.map.get_grid_location(neighbour_location)
                if grid_location.value != letter:

                    break
                location = neighbour_location
            else:
                self.found_words.append((self.location, location_direction))


@dataclasses.dataclass
class GridXmasWordFinder:
    map: Map
    location: Location
    locations_found: list[Location] = dataclasses.field(default_factory=list)

    def check_xmas_location(self) -> None:
        grid_location = self.map.get_grid_location(self.location)
        if "A" != grid_location.value:
            return
        neighbour_locations: dict[LocationDirection, str] = {}
        for location_direction in (
            LocationDirection.UP_LEFT,
            LocationDirection.UP_RIGHT,
            LocationDirection.DOWN_LEFT,
            LocationDirection.DOWN_RIGHT,
        ):
            neighbour_location = self.location.neighbour_location(location_direction)
            neighbour_grid_location = self.map.get_grid_location(neighbour_location)
            neighbour_locations[location_direction] = neighbour_grid_location.value

        if not (
            (
                neighbour_locations[LocationDirection.UP_LEFT] == "M"
                and neighbour_locations[LocationDirection.DOWN_RIGHT] == "S"
            )
            or (
                neighbour_locations[LocationDirection.UP_LEFT] == "S"
                and neighbour_locations[LocationDirection.DOWN_RIGHT] == "M"
            )
        ):
            return

        if not (
            (
                neighbour_locations[LocationDirection.UP_RIGHT] == "M"
                and neighbour_locations[LocationDirection.DOWN_LEFT] == "S"
            )
            or (
                neighbour_locations[LocationDirection.UP_RIGHT] == "S"
                and neighbour_locations[LocationDirection.DOWN_LEFT] == "M"
            )
        ):
            return

        self.locations_found.append(self.location)


def part_one() -> int:
    data = yield_data(FILENAME)
    map = create_map(data)
    grid_word_finder = GridWordFinder(
        map, "XMAS", Location(0, 0), list(LocationDirection)
    )
    for grid_location in map.grid_locations.values():
        grid_word_finder.location = grid_location.location
        grid_word_finder.find_word_directions()

    return len(grid_word_finder.found_words)


def part_two() -> int:
    data = yield_data(FILENAME)
    map = create_map(data)
    grid_xmas_word_finder = GridXmasWordFinder(map, Location(0, 0))
    for grid_location in map.grid_locations.values():
        grid_xmas_word_finder.location = grid_location.location
        grid_xmas_word_finder.check_xmas_location()
    return len(grid_xmas_word_finder.locations_found)


def main():
    print(f"Part one: {part_one()}")
    print(f"Part two: {part_two()}")


if __name__ == "__main__":
    main()
