import dataclasses
import enum
import typing
import collections


TEST_FILENAME = "day20_testdata.txt"
FILENAME = "day20_data.txt"


def yield_data(filename: str) -> typing.Iterator[str]:
    with open(file=filename, mode="r") as read_file:
        for line in read_file:
            yield line.strip()


class LocationType(enum.Enum):
    OBSTRUCTION = "#"
    EMPTY = "."
    START = "S"
    END = "E"
    OUT_OF_BOUNDS = "@"
    PATH = "^"


@dataclasses.dataclass(slots=True, frozen=True)
class Location:
    x: int
    y: int

    def neighbour_location(self, location_direction: "LocationDirection") -> "Location":
        other_location: "Location" = location_direction.value
        return Location(self.x + other_location.x, self.y + other_location.y)

    def __mul__(self, other: int) -> "Location":
        return Location(self.x * other, self.y * other)


@enum.unique
class LocationDirection(enum.Enum):
    UP = Location(0, -1)
    RIGHT = Location(1, 0)
    DOWN = Location(0, 1)
    LEFT = Location(-1, 0)


PATH_DIRECTION_LABEL: dict[LocationDirection, str] = {
    LocationDirection.UP: "^",
    LocationDirection.RIGHT: ">",
    LocationDirection.DOWN: "v",
    LocationDirection.LEFT: "<",
}


@dataclasses.dataclass(slots=True, frozen=True)
class GridLocation:
    location: Location
    location_type: LocationType
    facing_direction: typing.Optional[LocationDirection] = None

    @property
    def x(self) -> int:
        return self.location.x

    @property
    def y(self) -> int:
        return self.location.y

    @property
    def label(self) -> str:
        if self.location_type == LocationType.PATH and self.facing_direction:
            return PATH_DIRECTION_LABEL[self.facing_direction]
        return self.location_type.value


@dataclasses.dataclass
class Grid:
    grid_locations: dict[tuple[int, int], GridLocation] = dataclasses.field(
        default_factory=dict
    )
    max_x_location: int = 0
    max_y_location: int = 0
    start_location: typing.Optional[Location] = None
    end_location: typing.Optional[Location] = None

    def add_grid_location(self, grid_location: GridLocation) -> None:
        location_type = grid_location.location_type
        if location_type in (
            LocationType.OBSTRUCTION,
            LocationType.START,
            LocationType.END,
            location_type.PATH,
        ):
            self.grid_locations[(grid_location.x, grid_location.y)] = grid_location
        self.update_max_values(grid_location.location)

        if location_type == LocationType.START:
            self.start_location = grid_location.location

        if location_type == LocationType.END:
            self.end_location = grid_location.location

        return None

    def remove_grid_location(self, grid_location: GridLocation) -> None:
        location_type = grid_location.location_type
        if (grid_location.x, grid_location.y) in self.grid_locations:
            del self.grid_locations[(grid_location.x, grid_location.y)]
            if location_type == LocationType.START:
                self.start_location = None
            if location_type == LocationType.END:
                self.end_location = None

        return None

    def update_max_values(self, location: Location) -> None:
        self.max_x_location = max(self.max_x_location, location.x)
        self.max_y_location = max(self.max_y_location, location.y)

    def get_grid_location(self, location: Location) -> GridLocation:
        if not self.location_in_grid(location):
            return GridLocation(location, LocationType.OUT_OF_BOUNDS)
        grid_location = self.grid_locations.get(
            (location.x, location.y), GridLocation(location, LocationType.EMPTY)
        )

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
                row = f"{row}{grid_location.label}"
            rows.append(row)
        return "\n".join(rows)


def create_grid(data: typing.Iterator[str]) -> Grid:
    grid = Grid()
    for y_index, line in enumerate(data):
        for x_index, character in enumerate(line):
            location = Location(x_index, y_index)
            match character:
                case LocationType.OBSTRUCTION.value:
                    location_type = LocationType.OBSTRUCTION
                case LocationType.EMPTY.value:
                    location_type = LocationType.EMPTY
                case LocationType.START.value:
                    location_type = LocationType.START
                case LocationType.END.value:
                    location_type = LocationType.END
                case _:
                    raise ValueError(f"Invalid character: {character}")

            grid_location = GridLocation(location, location_type)
            grid.add_grid_location(grid_location)

    return grid


@dataclasses.dataclass
class Path:
    grid: Grid
    grid_location_history: list[GridLocation] = dataclasses.field(default_factory=list)
    seen_locations: set[Location] = dataclasses.field(default_factory=set)

    @property
    def time(self) -> int:
        return len(self.seen_locations) - 1

    def __str__(self) -> str:
        grid = Grid(
            self.grid.grid_locations.copy(),
            self.grid.max_x_location,
            self.grid.max_y_location,
        )
        for grid_location in self.grid_location_history:
            grid.add_grid_location(grid_location)
        return str(grid)


def find_path(grid: Grid) -> Path:
    if not grid.start_location:
        raise ValueError("No start location found")
    if not grid.end_location:
        raise ValueError("No end location found")
    current_grid_location = grid.get_grid_location(grid.start_location)
    end_grid_location = grid.get_grid_location(grid.end_location)
    grid_location_history = [current_grid_location]
    seen_locations = {current_grid_location.location}
    path = Path(grid, grid_location_history, seen_locations)
    while True:
        # for _ in range(85):
        if current_grid_location == end_grid_location:
            print(f"Found end location in {path.time - 1} steps")
            break
        current_grid_location = path.grid_location_history[-1]
        location = current_grid_location.location
        for location_direction in LocationDirection:
            neighbour_location = location.neighbour_location(location_direction)
            neighbour_grid_location = grid.get_grid_location(neighbour_location)
            if neighbour_grid_location.location_type in (
                LocationType.OUT_OF_BOUNDS,
                LocationType.OBSTRUCTION,
            ):
                continue
            if neighbour_location in path.seen_locations:
                continue
            path_grid_location = dataclasses.replace(
                neighbour_grid_location,
                location_type=LocationType.PATH,
                facing_direction=location_direction,
            )

            path.grid_location_history.append(path_grid_location)
            path.seen_locations.add(neighbour_grid_location.location)
            current_grid_location = neighbour_grid_location
            break

    # path.seen_locations.remove(path.grid_location_history[0].location)
    # path.grid_location_history.pop(0)
    return path


@dataclasses.dataclass
class CheatPath:
    grid: Grid
    path: Path
    cheat_grid_location: GridLocation
    start_index: int
    remainder_index: int

    @property
    def time(self) -> int:
        return (
            len(self.path.grid_location_history[: self.start_index + 1])
            + 1
            + len(self.path.grid_location_history[self.remainder_index :])
            - 1
        )

    def time_saved(self) -> int:
        return self.path.time - self.time

    def __str__(self) -> str:
        grid = Grid(
            self.grid.grid_locations.copy(),
            self.grid.max_x_location,
            self.grid.max_y_location,
        )
        for grid_location in self.path.grid_location_history[: self.start_index + 1]:
            grid.add_grid_location(grid_location)
        grid.add_grid_location(self.cheat_grid_location)
        for grid_location in self.path.grid_location_history[self.remainder_index :]:
            grid.add_grid_location(grid_location)
        return str(grid)


@dataclasses.dataclass
class CheatPaths:
    path: Path
    cheat_paths: list[CheatPath] = dataclasses.field(default_factory=list)

    @property
    def grid(self) -> Grid:
        return self.path.grid

    def find_cheat_paths(self) -> None:
        for index, grid_location in enumerate(self.path.grid_location_history[:-1]):
            location = grid_location.location
            location_direction = grid_location.facing_direction
            remaining_path_locations = set(
                grid_location.location
                for grid_location in self.path.grid_location_history[index + 3 :]
            )
            for location_direction in LocationDirection:
                neighbour_location1 = location.neighbour_location(location_direction)
                neighbour_grid_location1 = self.grid.get_grid_location(
                    neighbour_location1
                )
                neighbour_location2 = neighbour_location1.neighbour_location(
                    location_direction
                )
                neighbour_grid_location2 = self.grid.get_grid_location(
                    neighbour_location2
                )
                if neighbour_grid_location2.location in remaining_path_locations:
                    for remainder_index, grid_location in enumerate(
                        self.path.grid_location_history[index:], index
                    ):
                        if grid_location.location == neighbour_grid_location2.location:
                            break

                    grid_location = dataclasses.replace(
                        neighbour_grid_location1,
                        location_type=LocationType.PATH,
                        facing_direction=location_direction,
                    )
                    self.cheat_paths.append(
                        CheatPath(
                            self.grid,
                            self.path,
                            grid_location,
                            index,
                            remainder_index,
                        )
                    )


def part_one() -> int:
    data = yield_data(FILENAME)
    grid = create_grid(data)
    path = find_path(grid)
    print(f"{path.time=}")

    counter: typing.Counter[int] = collections.Counter()

    cheat_paths = CheatPaths(path)
    cheat_paths.find_cheat_paths()
    for cheat_path in cheat_paths.cheat_paths:
        counter[cheat_path.time_saved()] += 1

    total_cheats = 0
    for pico, qty in counter.items():
        if pico >= 100:
            total_cheats += qty

    return total_cheats


def part_two() -> int:
    data = yield_data(TEST_FILENAME)

    return 0


def main() -> None:
    print(f"Part one: {part_one()}")
    # print(f"Part two: {part_two()}")
    return None


if __name__ == "__main__":
    main()
