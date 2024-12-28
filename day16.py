import dataclasses
import enum
import typing
import heapq


TEST_FILENAME = "day16_testdata.txt"
FILENAME = "day16_data.txt"


def yield_data(filename: str) -> typing.Iterator[str]:
    with open(file=filename, mode="r") as read_file:
        for line in read_file:
            yield line.strip()


Cost = int


class LocationType(enum.Enum):
    START = "S"
    END = "E"
    EMPTY = "."
    OBSTRUCTION = "#"
    OUT_OF_BOUNDS = "@"
    PATH = "^"


@dataclasses.dataclass(slots=True, frozen=True)
class Location:
    x: int
    y: int

    def neighbour_location(self, location_direction: "LocationDirection") -> "Location":
        other_location: "Location" = location_direction.value
        return Location(self.x + other_location.x, self.y + other_location.y)

    def distance(self, other_location: "Location") -> int:
        return abs(self.x - other_location.x) + abs(self.y - other_location.y)


@enum.unique
class LocationDirection(enum.Enum):
    UP = Location(0, -1)
    RIGHT = Location(1, 0)
    DOWN = Location(0, 1)
    LEFT = Location(-1, 0)


@enum.unique
class Movements(enum.Enum):
    FORWARD = enum.auto()
    TURN_LEFT = enum.auto()
    TURN_RIGHT = enum.auto()


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


def turn_left(location_direction: LocationDirection) -> LocationDirection:
    match location_direction:
        case LocationDirection.UP:
            location_direction = LocationDirection.LEFT
        case LocationDirection.RIGHT:
            location_direction = LocationDirection.UP
        case LocationDirection.DOWN:
            location_direction = LocationDirection.RIGHT
        case LocationDirection.LEFT:
            location_direction = LocationDirection.DOWN
        case _:
            raise ValueError(f"Invalid type: {location_direction}")

    return location_direction


FACING_DIRECTION_LABEL: dict[LocationDirection, str] = {
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
            return FACING_DIRECTION_LABEL[self.facing_direction]
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
        if grid_location.location_type in (
            LocationType.OBSTRUCTION,
            LocationType.START,
            LocationType.END,
            LocationType.PATH,
        ):
            self.grid_locations[(grid_location.x, grid_location.y)] = grid_location
        self.update_max_values(grid_location.location)

        if grid_location.location_type == LocationType.START:
            self.start_location = grid_location.location
        elif grid_location.location_type == LocationType.END:
            self.end_location = grid_location.location

        return None

    def remove_grid_location(self, grid_location: GridLocation) -> None:
        if (grid_location.x, grid_location.y) in self.grid_locations:
            del self.grid_locations[(grid_location.x, grid_location.y)]

            if grid_location.location_type == LocationType.START:
                self.start_location = None
            elif grid_location.location_type == LocationType.END:
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
    
    def copy(self) -> "Grid":
        return Grid(
            grid_locations=self.grid_locations.copy(),
            max_x_location=self.max_x_location,
            max_y_location=self.max_y_location, 
            start_location=self.start_location,
            end_location=self.end_location)


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
                case LocationType.START.value:
                    location_type = LocationType.START
                case LocationType.END.value:
                    location_type = LocationType.END
                case _:
                    raise ValueError(f"Invalid character: {character}")

            grid_location = GridLocation(location, location_type, facing_direction)
            grid.add_grid_location(grid_location)

    return grid




@dataclasses.dataclass
class Path:
    grid: Grid
    cost: Cost = 0
    path_grid_locations: list[GridLocation] = dataclasses.field(default_factory=list)

    @property
    def current_path_grid_location(self) -> GridLocation:
        return self.path_grid_locations[-1]

    @property
    def current_path_location(self) -> Location:
        return self.current_path_grid_location.location

    @property
    def facing_direction(self) -> typing.Optional[LocationDirection]:
        return self.current_path_grid_location.facing_direction

    def add_grid_location(self, grid_location: GridLocation) -> None:
        self.path_grid_locations.append(grid_location)
        return None
    
    @property
    def can_move_forward(self) -> bool:
        facing_direction = self.facing_direction
        if not facing_direction:
            raise ValueError("No facing direction found")
        neighbour_location = self.current_path_location.neighbour_location(
            facing_direction
        )
        neighbour_grid_location = self.grid.get_grid_location(neighbour_location)

        return neighbour_grid_location.location_type not in (LocationType.OBSTRUCTION, LocationType.OUT_OF_BOUNDS)

    def forward_path_grid_location(self) -> tuple[GridLocation, Cost]:
        facing_direction = self.facing_direction
        if not facing_direction:
            raise ValueError("No facing direction found")
        neighbour_location = self.current_path_location.neighbour_location(
            facing_direction
        )
        neighbour_grid_location = self.grid.get_grid_location(neighbour_location)
        path_grid_location = dataclasses.replace(
            neighbour_grid_location,
            location_type=LocationType.PATH,
            facing_direction=facing_direction,
        )
        return path_grid_location, 1

    def turn_left_path_grid_location(self) -> tuple[GridLocation, Cost]:
        facing_direction = self.facing_direction
        if not facing_direction:
            raise ValueError("No facing direction found")

        facing_direction = turn_left(facing_direction)
        path_grid_location = dataclasses.replace(
            self.current_path_grid_location,
            facing_direction=facing_direction,
        )
        return path_grid_location, 1000

    def turn_right_path_grid_location(self) -> tuple[GridLocation, Cost]:
        facing_direction = self.facing_direction
        if not facing_direction:
            raise ValueError("No facing direction found")

        facing_direction = turn_right(facing_direction)
        path_grid_location = dataclasses.replace(
            self.current_path_grid_location,
            facing_direction=facing_direction,
        )
        return path_grid_location, 1000
    
    def __str__(self) -> str:
        new_grid = self.grid.copy()
        added_locations: set[Location] = set()
        for path_grid_location in self.path_grid_locations:
            if path_grid_location.location in added_locations:
                continue
            new_grid.add_grid_location(path_grid_location)  
            added_locations.add(path_grid_location.location)
        return str(new_grid)
    
    def copy(self) -> "Path":
        return Path(cost=self.cost, grid=self.grid, path_grid_locations=self.path_grid_locations.copy())


@dataclasses.dataclass(order=True)
class PrioritizedItem:
    priority: int
    path: Path = dataclasses.field(compare=False)



def shortest_cheapest_path(grid: Grid, stop_at_first: bool = True) -> tuple[Cost,list[Path]]:
    start_location = grid.start_location
    end_location = grid.end_location
    if not start_location or not end_location:
        raise ValueError("Start or end location not found")
    grid_location = grid.get_grid_location(start_location)
    path_grid_location = dataclasses.replace(
        grid_location,
        location_type=LocationType.PATH,
        facing_direction=LocationDirection.RIGHT,
    )
    path = Path(grid)
    path.add_grid_location(path_grid_location)
    queue: list[PrioritizedItem] = [PrioritizedItem(0, path)]
    visited_grid_locations: set[GridLocation] = set()
    cheapest_paths: list[Path] = []
    while queue:
        prioritized_item = heapq.heappop(queue)
        path = prioritized_item.path
        print(f"Queue size: {len(queue)=} Distance: {path.current_path_location.distance(end_location)}")
        # print(f"{path.current_path_location=} {path.facing_direction=} {path.cost=}")
        if path.current_path_location == end_location:
            if stop_at_first:
                return path.cost, [path]
            if not cheapest_paths:
                cheapest_paths.append(path)
            if path.cost == cheapest_paths[0].cost:
                cheapest_paths.append(path)
            # cheapest_paths.append(path)


            
        if path.current_path_grid_location in visited_grid_locations:
            continue
        visited_grid_locations.add(path.current_path_grid_location)


        for movement in Movements:
            match movement:
                case Movements.FORWARD:
                    if not path.can_move_forward:
                        continue
                    path_grid_location, cost = path.forward_path_grid_location()
                    new_path = path.copy()
                    new_path.add_grid_location(path_grid_location)
                    new_path.cost += cost
                    distance = new_path.current_path_location.distance(end_location)
                    priority = new_path.cost + distance
                    heapq.heappush(queue, PrioritizedItem(priority, new_path))
                case Movements.TURN_LEFT:
                    path_grid_location, cost = path.turn_left_path_grid_location()
                    new_path = path.copy()
                    new_path.add_grid_location(path_grid_location)
                    new_path.cost += cost
                    distance = new_path.current_path_location.distance(end_location)
                    priority = new_path.cost + distance
                    heapq.heappush(queue, PrioritizedItem(priority, new_path))
                case Movements.TURN_RIGHT:
                    path_grid_location, cost = path.turn_right_path_grid_location()
                    new_path = path.copy()
                    new_path.add_grid_location(path_grid_location)
                    new_path.cost += cost
                    distance = new_path.current_path_location.distance(end_location)
                    priority = new_path.cost + distance
                    heapq.heappush(queue, PrioritizedItem(priority, new_path))
    if not cheapest_paths:
        return -1, []
    return cheapest_paths[0].cost, cheapest_paths

def unique_path_locations(paths: list[Path]) -> set[Location]:
    unique_locations: set[Location] = set()
    for path in paths:
        for grid_locaion in path.path_grid_locations:
            unique_locations.add(grid_locaion.location)
    return unique_locations 


def part_one() -> int:
    data = yield_data(FILENAME)
    grid = create_grid(data)
    print(grid)
    cost, paths = shortest_cheapest_path(grid)

    return cost


def part_two() -> int:
    data = yield_data(TEST_FILENAME)
    grid = create_grid(data)
    print(grid)
    cost, paths = shortest_cheapest_path(grid, False)
    print(f"{len(paths)=}")
    print(f"{cost=}")
    for path in paths:
        print(path.cost)
        print(path)

    unique_locations = unique_path_locations(paths)

    return len(unique_locations)


def main() -> None:
    print(f"Part one: {part_one()}")
    # print(f"Part two: {part_two()}")
    return None


if __name__ == "__main__":
    main()
