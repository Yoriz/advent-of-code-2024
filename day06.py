import typing
import dataclasses
import enum
import itertools

FILENAME = "day06_data.txt"


def yield_data(filename: str) -> typing.Iterator[str]:
    with open(file=filename, mode="r") as read_file:
        for line in read_file:
            yield line.strip()


class LocationType(enum.Enum):
    OBSTRUCTION = "#"
    EMPTY = "."
    STARTING_POSITION = "^"
    OUT_OF_BOUNDS = "@"


class GaudeRoutePatrolExitState(enum.Enum):
    OUT_OF_BOUNDS = enum.auto()
    STUCK_IN_LOOP = enum.auto()
    STUCK_ROTATING = enum.auto()


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


@dataclasses.dataclass(slots=True, frozen=True)
class LocationState:
    location: Location
    location_direction: LocationDirection


@dataclasses.dataclass
class GridLocation:
    location: Location
    location_type: LocationType

    @property
    def x(self) -> int:
        return self.location.x

    @property
    def y(self) -> int:
        return self.location.y

    @property
    def value(self) -> str:
        return self.location_type.value


@dataclasses.dataclass
class Map:
    grid_locations: dict[tuple[int, int], GridLocation] = dataclasses.field(
        default_factory=dict
    )
    max_x_location: int = 0
    max_y_location: int = 0
    start_location: typing.Optional[Location] = None

    def add_grid_location(self, grid_location: GridLocation) -> None:
        if grid_location.location_type in (
            LocationType.OBSTRUCTION,
            LocationType.STARTING_POSITION,
        ):
            self.grid_locations[(grid_location.x, grid_location.y)] = grid_location
        self.update_max_values(grid_location.location)

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
                row = f"{row}{grid_location.value}"
            rows.append(row)
        return "\n".join(rows)


def create_map(data: typing.Iterator[str]) -> Map:
    map = Map()
    for y_index, line in enumerate(data):
        for x_index, character in enumerate(line):
            location = Location(x_index, y_index)

            match character:
                case LocationType.OBSTRUCTION.value:
                    location_type = LocationType.OBSTRUCTION
                case LocationType.EMPTY.value:
                    location_type = LocationType.EMPTY
                case LocationType.STARTING_POSITION.value:
                    location_type = LocationType.STARTING_POSITION
                    map.start_location = location
                case _:
                    raise ValueError(f"Invalid character: {character}")

            grid_location = GridLocation(location, location_type)
            map.add_grid_location(grid_location)

    return map


@dataclasses.dataclass
class GuardRoute:
    location: Location
    location_direction: LocationDirection
    location_states: list[LocationState] = dataclasses.field(default_factory=list)

    def __post_init__(self) -> None:
        self.location_states.append(
            LocationState(self.location, self.location_direction)
        )

    def turn_right(self) -> None:
        match self.location_direction:
            case LocationDirection.UP:
                self.location_direction = LocationDirection.RIGHT
            case LocationDirection.RIGHT:
                self.location_direction = LocationDirection.DOWN
            case LocationDirection.DOWN:
                self.location_direction = LocationDirection.LEFT
            case LocationDirection.LEFT:
                self.location_direction = LocationDirection.UP

    def patrol(self, map: Map) -> GaudeRoutePatrolExitState:
        turn_count = 0
        while True:
            neighbour_location = self.location.neighbour_location(
                self.location_direction
            )
            # print(neighbour_location)
            neighbour_location_state = LocationState(
                neighbour_location, self.location_direction
            )
            if neighbour_location_state in self.location_states:
                return GaudeRoutePatrolExitState.STUCK_IN_LOOP
            grid_location = map.get_grid_location(neighbour_location)
            match grid_location.location_type:
                case LocationType.OUT_OF_BOUNDS:
                    print("Out of bounds")
                    return GaudeRoutePatrolExitState.OUT_OF_BOUNDS
                case LocationType.OBSTRUCTION:
                    self.turn_right()
                    turn_count += 1
                    # print(f"Turned right {turn_count} times")
                    if turn_count > 3:
                        return GaudeRoutePatrolExitState.STUCK_ROTATING
                case _:
                    self.location = neighbour_location
                    self.location_states.append(
                        LocationState(self.location, self.location_direction)
                    )
                    turn_count = 0

    def distinct_visited_locations(self) -> list[Location]:
        return list(
            set([location_state.location for location_state in self.location_states])
        )

    def distinct_visited_locations_count(self) -> int:
        return len(self.distinct_visited_locations())

    def map_show_visited(self, map: "Map") -> str:
        rows: list[str] = []
        for y_index in range(map.max_y_location + 1):
            row = ""
            for x_index in range(map.max_x_location + 1):
                location = Location(x_index, y_index)
                grid_location = map.get_grid_location(location)
                value = (
                    grid_location.value
                    if not location in self.distinct_visited_locations()
                    else "X"
                )
                row = f"{row}{value}"
            rows.append(row)
        return "\n".join(rows)


def part_one() -> int:
    data = yield_data(FILENAME)
    map = create_map(data)
    if not map.start_location:
        raise ValueError("No start location found")
    gaurd_route = GuardRoute(map.start_location, LocationDirection.UP)
    gaurd_route.patrol(map)
    return gaurd_route.distinct_visited_locations_count()


def part_two() -> int:
    data = yield_data(FILENAME)
    map = create_map(data)
    map.add_grid_location(GridLocation(Location(3, 6), LocationType.OBSTRUCTION))
    if not map.start_location:
        raise ValueError("No start location found")
    gaurd_route = GuardRoute(map.start_location, LocationDirection.UP)
    gaurd_route.patrol(map)
    print(f"{len(gaurd_route.location_states)=}")
    stuck_in_loop_count = 0
    obstruction_locations: set[Location] = set()
    for index, (start, obstacle) in enumerate(
        itertools.pairwise(gaurd_route.location_states)
    ):
        print(f"Loop {index}")
        grid_location = map.get_grid_location(obstacle.location)
        if grid_location.location_type == LocationType.OBSTRUCTION:
            continue
        new_gaurd_route = GuardRoute(start.location, start.location_direction)
        map.add_grid_location(GridLocation(obstacle.location, LocationType.OBSTRUCTION))
        if new_gaurd_route.patrol(map) == GaudeRoutePatrolExitState.STUCK_IN_LOOP:
            stuck_in_loop_count += 1
            obstruction_locations.add(obstacle.location)
        map.add_grid_location(GridLocation(obstacle.location, LocationType.EMPTY))

    return len(obstruction_locations)


def main() -> None:
    print(f"Part one: {part_one()}")
    print(f"Part two: {part_two()}")


if __name__ == "__main__":
    main()
