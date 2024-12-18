from collections import deque
import dataclasses
import enum
import typing


TEST_FILENAME = "day18_testdata.txt"
FILENAME = "day18_data.txt"


def yield_data(filename: str) -> typing.Iterator[str]:
    with open(file=filename, mode="r") as read_file:
        for line in read_file:
            yield line.strip()


@dataclasses.dataclass
class Defaults:
    filename: str
    max_x_location: int
    max_y_location: int
    falling_byte_qty: int


TEST_FILE_DEFAULTS = Defaults(
    filename=TEST_FILENAME, max_x_location=6, max_y_location=6, falling_byte_qty=12
)

FILE_DEFAULTS = Defaults(
    filename=FILENAME, max_x_location=70, max_y_location=70, falling_byte_qty=1024
)


class LocationType(enum.Enum):
    STEP = "O"
    EMPTY = "."
    CORRUPTED = "#"
    OUT_OF_BOUNDS = "X"


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
    RIGHT = Location(1, 0)
    DOWN = Location(0, 1)
    LEFT = Location(-1, 0)


@dataclasses.dataclass(slots=True)
class GridLocation:
    location: Location
    location_type: LocationType

    @property
    def label(self) -> str:
        return self.location_type.value

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
    max_x_location: int = 0
    max_y_location: int = 0
    corrupted_bytes: list[Location] = dataclasses.field(default_factory=list)
    byte_index: int = 0

    def add_corrupted_byte(self, location: Location) -> None:
        self.corrupted_bytes.append(location)

    @property
    def remaining_corrupted_bytes(self) -> list[Location]:
        return self.corrupted_bytes[self.byte_index :]

    def add_corrupted_byte_to_grid(self) -> None:
        location = self.corrupted_bytes[self.byte_index]
        grid_location = GridLocation(location, LocationType.CORRUPTED)
        self.add_grid_location(grid_location)
        self.byte_index += 1

    def add_grid_location(self, grid_location: GridLocation) -> None:
        if (grid_location.x, grid_location.y) in self.grid_locations:
            raise ValueError("Grid location is already occupied")

        if grid_location.location_type != LocationType.EMPTY:
            self.grid_locations[(grid_location.x, grid_location.y)] = grid_location

        return None

    def get_grid_location(self, location: Location) -> GridLocation:
        if not self.location_in_grid(location):
            return GridLocation(location, LocationType.OUT_OF_BOUNDS)
        grid_location = self.grid_locations.get(
            (location.x, location.y), GridLocation(location, LocationType.EMPTY)
        )

        return grid_location

    def remove_grid_location(self, grid_location: GridLocation) -> None:
        if (grid_location.x, grid_location.y) in self.grid_locations:
            del self.grid_locations[(grid_location.x, grid_location.y)]

        return None

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


def create_grid(
    data: typing.Iterator[str], max_x_location: int, max_y_location: int
) -> Grid:
    grid = Grid()
    for line in data:
        x, y = line.split(",")
        location = Location(int(x), int(y))
        grid.add_corrupted_byte(location)

    grid.max_x_location = max_x_location
    grid.max_y_location = max_y_location
    return grid


@dataclasses.dataclass
class Path:
    current_location: Location
    end_location: Location
    grid: Grid
    history: deque[Location] = dataclasses.field(default_factory=deque)
    steps: int = 0

    def is_valid_location(self, location: Location) -> bool:
        grid_location = self.grid.get_grid_location(location)
        return grid_location.location_type == LocationType.EMPTY

    def get_neighbours(self) -> typing.Iterator[Location]:
        for direction in LocationDirection:
            neighbour_location = self.current_location.neighbour_location(direction)
            if self.is_valid_location(neighbour_location):
                yield neighbour_location

    def move(self, location: Location) -> None:
        self.current_location = location
        self.history.append(location)
        self.steps += 1

    def is_at_destination(self) -> bool:
        return self.current_location == self.end_location


@dataclasses.dataclass
class PathFinder:
    start_location: Location
    end_location: Location
    grid: Grid
    queue: deque[Path] = dataclasses.field(default_factory=deque)
    visited: set[Location] = dataclasses.field(default_factory=set)

    def __post_init__(self):
        path = Path(self.start_location, self.end_location, self.grid)
        self.queue.append(path)

    def find_shortest_path(self) -> typing.Optional[Path]:
        while self.queue:
            path = self.queue.popleft()
            if path.current_location in self.visited:
                continue
            self.visited.add(path.current_location)

            if path.is_at_destination():
                return path

            for neighbour in path.get_neighbours():
                new_path = Path(
                    neighbour,
                    self.end_location,
                    self.grid,
                    path.history.copy(),
                    path.steps,
                )
                new_path.move(neighbour)
                self.queue.append(new_path)

        return None


def part_one() -> int:
    defaults = FILE_DEFAULTS
    data = yield_data(defaults.filename)
    grid = create_grid(data, defaults.max_x_location, defaults.max_y_location)
    for _ in range(defaults.falling_byte_qty):
        grid.add_corrupted_byte_to_grid()
    print(grid)
    path_finder = PathFinder(
        Location(0, 0), Location(defaults.max_x_location, defaults.max_y_location), grid
    )
    path = path_finder.find_shortest_path()
    if path:
        print("Shortest path:")
        return path.steps
    else:
        print("No path found")

    return 0


def part_two() -> tuple[int, int]:
    defaults = FILE_DEFAULTS
    data = yield_data(defaults.filename)
    grid = create_grid(data, defaults.max_x_location, defaults.max_y_location)
    for _ in range(defaults.falling_byte_qty):
        grid.add_corrupted_byte_to_grid()

    path_finder = PathFinder(
        Location(0, 0), Location(defaults.max_x_location, defaults.max_y_location), grid
    )
    path = path_finder.find_shortest_path()
    if not path:
        print("No path found")
        return 0, 0
    remaing_corrupted_bytes = grid.remaining_corrupted_bytes
    corrupted_bytes_in_path = [
        location for location in path.history if location in remaing_corrupted_bytes
    ]
    for location in corrupted_bytes_in_path:
        grid_location = GridLocation(location, LocationType.CORRUPTED)
        grid.add_grid_location(grid_location)
        loaction_index = path.history.index(location)
        previous_location = path.history[loaction_index - 1]
        new_path_finder = PathFinder(
            previous_location,
            Location(defaults.max_x_location, defaults.max_y_location),
            grid,
        )
        new_path = new_path_finder.find_shortest_path()
        if not new_path:
            print(f"Path blocked by {location}")
            break

    return location.x, location.y


def main() -> None:
    # print(f"Part one: {part_one()}")
    print(f"Part two: {part_two()}")
    return None


if __name__ == "__main__":
    main()
