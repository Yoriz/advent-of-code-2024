import dataclasses
import enum
import typing
import collections


FILENAME = "day10_data.txt"


def yield_data(filename: str) -> typing.Iterator[str]:
    with open(file=filename, mode="r") as read_file:
        for line in read_file:
            yield line.strip()


class LocationType(enum.Enum):
    HEIGHT = enum.auto()
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
    RIGHT = Location(1, 0)
    DOWN = Location(0, 1)
    LEFT = Location(-1, 0)


@dataclasses.dataclass
class GridLocation:
    location: Location
    height: int
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
    max_x_location: int = 0
    max_y_location: int = 0
    zero_height_locations: list[Location] = dataclasses.field(default_factory=list)

    def add_grid_location(self, grid_location: GridLocation) -> None:
        self.grid_locations[(grid_location.x, grid_location.y)] = grid_location
        self.update_max_values(grid_location.location)

        if grid_location.height == 0:
            self.zero_height_locations.append(grid_location.location)

        return None

    def update_max_values(self, location: Location) -> None:
        self.max_x_location = max(self.max_x_location, location.x)
        self.max_y_location = max(self.max_y_location, location.y)

    def get_grid_location(self, location: Location) -> GridLocation:
        if not self.location_in_grid(location):
            return GridLocation(location, -1, LocationType.OUT_OF_BOUNDS)
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
                row = f"{row}{grid_location.height}"
            rows.append(row)
        return "\n".join(rows)


def create_map(data: typing.Iterator[str]) -> Grid:
    grid = Grid()
    for y_index, line in enumerate(data):
        for x_index, character in enumerate(line):
            location = Location(x_index, y_index)
            if character == ".":
                character = "-1"
            height = int(character)
            location_type = LocationType.HEIGHT
            grid_location = GridLocation(location, height, location_type)
            grid.add_grid_location(grid_location)

    return grid


@dataclasses.dataclass
class HikingTrail:
    trailhead_location: Location
    grid: Grid

    def find_trails(self, distinct: bool = False) -> int:
        trail_heads: set[Location] = set()
        distinct_trial_heads: list[Location] = []
        queue: collections.deque[list[Location]] = collections.deque()
        queue.append([self.trailhead_location])
        while queue:
            trail = queue.popleft()
            current_location = trail[-1]
            grid_location = self.grid.get_grid_location(current_location)
            for location_direction in LocationDirection:
                neighbour_location = current_location.neighbour_location(
                    location_direction
                )
                neighbour_grid_location = self.grid.get_grid_location(
                    neighbour_location
                )
                if neighbour_grid_location.location_type == LocationType.OUT_OF_BOUNDS:
                    continue
                if neighbour_grid_location.height <= grid_location.height:
                    continue
                if neighbour_grid_location.height > grid_location.height + 1:
                    continue
                new_trail = trail.copy()
                new_trail.append(neighbour_location)
                if grid_location.height == 8 and neighbour_grid_location.height == 9:
                    trail_heads.add(neighbour_location)
                    distinct_trial_heads.append(neighbour_location)
                else:
                    queue.append(new_trail)

        if distinct:
            return len(distinct_trial_heads)
        return len(trail_heads)


def part_one() -> int:
    data = yield_data(FILENAME)
    grid = create_map(data)
    toalscore = 0
    for location in grid.zero_height_locations:
        hiking_trial = HikingTrail(location, grid)
        score = hiking_trial.find_trails()
        toalscore += score

    return toalscore


def part_two() -> int:
    data = yield_data(FILENAME)
    grid = create_map(data)
    toalscore = 0
    for location in grid.zero_height_locations:
        hiking_trial = HikingTrail(location, grid)
        score = hiking_trial.find_trails(True)
        toalscore += score

    return toalscore


def main() -> None:
    print(f"Part one: {part_one()}")
    print(f"Part two: {part_two()}")


if __name__ == "__main__":
    main()
