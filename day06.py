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
    GUARD = "^"
    OUT_OF_BOUNDS = "@"


class GaurdRouteExitState(enum.Enum):
    OUT_OF_BOUNDS = enum.auto()
    STUCK_IN_LOOP = enum.auto()


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


def turn_right(location_direction: LocationDirection) -> LocationDirection:
    match location_direction:
        case LocationDirection.UP:
            location_direction = LocationDirection.RIGHT
        case LocationDirection.RIGHT:
            location_direction = LocationDirection.DOWN
        case LocationDirection.DOWN:
            location_direction = LocationDirection.LEFT
        case LocationDirection.LEFT:
            location_direction = LocationDirection.UP
        case _:
            raise ValueError(f"Invalid type: {location_direction}")

    return location_direction


GUARD_DIRECTION_LABEL: dict[LocationDirection, str] = {
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
        if self.location_type == LocationType.GUARD and self.facing_direction:
            return GUARD_DIRECTION_LABEL[self.facing_direction]
        return self.location_type.value


@dataclasses.dataclass
class Grid:
    grid_locations: dict[tuple[int, int], GridLocation] = dataclasses.field(
        default_factory=dict
    )
    max_x_location: int = 0
    max_y_location: int = 0
    guard_location: typing.Optional[Location] = None

    def add_grid_location(self, grid_location: GridLocation) -> None:
        if grid_location.location_type in (
            LocationType.OBSTRUCTION,
            LocationType.GUARD,
        ):
            self.grid_locations[(grid_location.x, grid_location.y)] = grid_location
        self.update_max_values(grid_location.location)

        if grid_location.location_type == LocationType.GUARD:
            self.guard_location = grid_location.location

        return None

    def remove_grid_location(self, grid_location: GridLocation) -> None:
        if (grid_location.x, grid_location.y) in self.grid_locations:
            del self.grid_locations[(grid_location.x, grid_location.y)]
            if grid_location.location_type == LocationType.GUARD:
                self.guard_location = None

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
            facing_direction = None

            match character:
                case LocationType.OBSTRUCTION.value:
                    location_type = LocationType.OBSTRUCTION
                case LocationType.EMPTY.value:
                    location_type = LocationType.EMPTY
                case LocationType.GUARD.value:
                    location_type = LocationType.GUARD
                    facing_direction = LocationDirection.UP
                case _:
                    raise ValueError(f"Invalid character: {character}")

            grid_location = GridLocation(location, location_type, facing_direction)
            grid.add_grid_location(grid_location)

    return grid


@dataclasses.dataclass
class GuardRoute:
    grid: Grid
    grid_location_history: list[GridLocation] = dataclasses.field(default_factory=list)
    seen_grid_locations: set[GridLocation] = dataclasses.field(default_factory=set)

    def __post_init__(self):
        guard_location = self.grid.guard_location
        if not guard_location:
            raise ValueError("Guard location not found")
        grid_location = self.grid.get_grid_location(guard_location)
        self.grid_location_history.append(grid_location)
        self.seen_grid_locations.add(grid_location)

    @property
    def distinct_visited_locations(self) -> set[Location]:
        return set(gridlocation.location for gridlocation in self.grid_location_history)

    def patrol(self) -> GaurdRouteExitState:
        while True:
            current_grid_location = self.grid_location_history[-1]
            location = current_grid_location.location
            facing_direction = current_grid_location.facing_direction
            if not facing_direction:
                raise ValueError("No facing direction found")
            neighbourlocation = location.neighbour_location(facing_direction)
            neighbour_grid_location = self.grid.get_grid_location(neighbourlocation)
            match neighbour_grid_location.location_type:
                case LocationType.OUT_OF_BOUNDS:
                    return GaurdRouteExitState.OUT_OF_BOUNDS
                case LocationType.OBSTRUCTION:
                    facing_direction = turn_right(facing_direction)
                    new_grid_location = dataclasses.replace(
                        current_grid_location,
                        facing_direction=facing_direction,
                    )
                case LocationType.EMPTY:
                    new_grid_location = dataclasses.replace(
                        current_grid_location,
                        location=neighbourlocation,
                    )
            if new_grid_location in self.seen_grid_locations:
                return GaurdRouteExitState.STUCK_IN_LOOP

            self.grid_location_history.append(new_grid_location)
            self.seen_grid_locations.add(new_grid_location)
            self.grid.remove_grid_location(current_grid_location)
            self.grid.add_grid_location(new_grid_location)
            # print(self.grid)
            # print(f"{len(self.distinct_visited_locations)=}")


@dataclasses.dataclass
class FindLoopingGuardRoutes:
    grid: Grid
    obstruction_locations: set[Location] = dataclasses.field(default_factory=set)

    def __post_init__(self):
        guard_location = self.grid.guard_location
        if not guard_location:
            raise ValueError("Guard location not found")
        guard_grid_location = self.grid.get_grid_location(guard_location)
        guard_grid_location_copy = dataclasses.replace(guard_grid_location)
        self.guard_grid_location_copy = guard_grid_location_copy

    def reset_guard(self) -> None:
        guard_location = self.grid.guard_location
        if not guard_location:
            return None
        guard_grid_location = self.grid.get_grid_location(guard_location)
        self.grid.remove_grid_location(guard_grid_location)
        new_guard_grid_location = dataclasses.replace(self.guard_grid_location_copy)
        self.grid.add_grid_location(new_guard_grid_location)

    def find_obstruction_locations(self, locations: set[Location]) -> None:
        amount_of_locations = len(locations)
        for index, location in enumerate(locations):
            self.reset_guard()
            grid_location = self.grid.get_grid_location(location)
            if grid_location.location_type != LocationType.EMPTY:
                continue
            print(f"Trying location: {location} of {index} {amount_of_locations}")
            obstruction_grid_location = GridLocation(location, LocationType.OBSTRUCTION)
            self.grid.add_grid_location(obstruction_grid_location)
            guard_route = GuardRoute(self.grid)
            exit_state = guard_route.patrol()
            if exit_state == GaurdRouteExitState.STUCK_IN_LOOP:
                self.obstruction_locations.add(location)
            self.grid.remove_grid_location(obstruction_grid_location)


def part_one() -> int:
    data = yield_data(FILENAME)
    grid = create_grid(data)
    guard_route = GuardRoute(grid)
    exit_state = guard_route.patrol()
    print(exit_state)
    return len(guard_route.distinct_visited_locations)


def part_two() -> int:
    data = yield_data(FILENAME)
    grid = create_grid(data)
    guard_route = GuardRoute(grid)
    guard_route.patrol()
    locations = guard_route.distinct_visited_locations

    data = yield_data(FILENAME)
    grid = create_grid(data)
    find_looping_guard_routes = FindLoopingGuardRoutes(grid)
    find_looping_guard_routes.find_obstruction_locations(locations)
    return len(find_looping_guard_routes.obstruction_locations)


def main() -> None:
    print(f"Part one: {part_one()}")
    print(f"Part two: {part_two()}")


 if __name__ == "__main__":
     main()
