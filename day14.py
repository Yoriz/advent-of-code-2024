import collections
import enum
import typing
import dataclasses

FILENAME = "day14_data.txt"


def yield_data(filename: str) -> typing.Iterator[str]:
    with open(file=filename, mode="r") as read_file:
        for line in read_file:
            yield line.strip()


class LocationType(enum.Enum):
    ROBOT = enum.auto()
    EMPTY = enum.auto()
    OUT_OF_BOUNDS = enum.auto()


@dataclasses.dataclass(slots=True)
class Robot:
    location: "Location"
    offset: "Location"
    time_step: int = 0


@dataclasses.dataclass(slots=True, frozen=True)
class Location:
    x: int
    y: int

    def differance(self, other: "Location") -> "Location":
        return Location(self.x - other.x, self.y - other.y)

    def offset_by(self, differance: "Location") -> "Location":
        return Location(self.x + differance.x, self.y + differance.y)

    def neighbour_location(self, location_direction: "LocationDirection") -> "Location":
        other_location: "Location" = location_direction.value
        return Location(self.x + other_location.x, self.y + other_location.y)


@dataclasses.dataclass(slots=True)
class GridLocation:
    location: Location
    location_type: LocationType
    robots: list[Robot] = dataclasses.field(default_factory=list)

    @property
    def label(self) -> str:
        match self.location_type:
            case LocationType.ROBOT:
                return str(self.robot_count)
            case LocationType.EMPTY:
                return "."
            case LocationType.OUT_OF_BOUNDS:
                return "@"

    @property
    def x(self) -> int:
        return self.location.x

    @property
    def y(self) -> int:
        return self.location.y

    def add_robot(self, robot: Robot) -> None:
        self.robots.append(robot)
        return None

    def remove_robot(self, robot: Robot) -> None:
        self.robots.remove(robot)
        return None

    @property
    def robot_count(self) -> int:
        return len(self.robots)


@dataclasses.dataclass(slots=True)
class Grid:
    max_x_location: int
    max_y_location: int
    grid_locations: dict[tuple[int, int], GridLocation] = dataclasses.field(
        default_factory=dict
    )
    time_step: int = 0

    def remove_grid_location(self, grid_location: GridLocation) -> None:
        del self.grid_locations[(grid_location.x, grid_location.y)]
        return None

    def add_robot(self, robot: Robot) -> None:
        grid_location = self.get_grid_location(robot.location)
        match grid_location.location_type:
            case LocationType.OUT_OF_BOUNDS:
                raise ValueError("Robot out of bounds")
            case LocationType.ROBOT:
                self.grid_locations[(robot.location.x, robot.location.y)].add_robot(
                    robot
                )
            case LocationType.EMPTY:
                self.grid_locations[(robot.location.x, robot.location.y)] = (
                    GridLocation(robot.location, LocationType.ROBOT, [robot])
                )
            case _:
                raise ValueError("Invalid grid location type")

    def remove_robot(self, robot: Robot) -> None:
        grid_location = self.get_grid_location(robot.location)
        match grid_location.location_type:
            case LocationType.ROBOT:
                self.grid_locations[(robot.location.x, robot.location.y)].remove_robot(
                    robot
                )
                if not grid_location.robot_count:
                    self.remove_grid_location(grid_location)
            case _:
                raise ValueError("Invalid grid location type")

    def wrap_location(self, location: Location) -> Location:
        x = location.x % (self.max_x_location + 1)
        y = location.y % (self.max_y_location + 1)
        return Location(x, y)

    def move_robots(self) -> None:
        for x, y in set(self.grid_locations.keys()):
            location = Location(x, y)
            grid_location = self.get_grid_location(location)
            robots = grid_location.robots[:]
            for robot in robots:
                if robot.time_step != self.time_step:
                    continue
                self.remove_robot(robot)
                new_location = robot.location.offset_by(robot.offset)
                if not self.location_in_grid(new_location):
                    new_location = self.wrap_location(new_location)
                robot.location = new_location
                robot.time_step += 1
                self.add_robot(robot)
                # print(f"Moved robot {robot}")
        self.time_step += 1

    def get_grid_location(self, location: Location) -> GridLocation:
        if not self.location_in_grid(location):
            return GridLocation(location, LocationType.OUT_OF_BOUNDS)
        grid_location = self.grid_locations.get((location.x, location.y))
        if not grid_location:
            return GridLocation(location, LocationType.EMPTY)

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

    def robots_in_quadrant(self, quadrant_no: int) -> list[Robot]:
        robots: list[Robot] = []
        match quadrant_no:
            case 1:
                y_min = 0
                y_max = self.max_y_location // 2
                x_min = 0
                x_max = self.max_x_location // 2
            case 2:
                y_min = 0
                y_max = self.max_y_location // 2
                x_min = self.max_x_location // 2 + 1
                x_max = self.max_x_location + 1
            case 3:
                y_min = self.max_y_location // 2 + 1
                y_max = self.max_y_location + 1
                x_min = 0
                x_max = self.max_x_location // 2
            case 4:
                y_min = self.max_y_location // 2 + 1
                y_max = self.max_y_location + 1
                x_min = self.max_x_location // 2 + 1
                x_max = self.max_x_location + 1

        for y_index in range(y_min, y_max):
            for x_index in range(x_min, x_max):
                location = Location(x_index, y_index)
                grid_location = self.get_grid_location(location)
                if grid_location.location_type == LocationType.ROBOT:
                    robots.extend(grid_location.robots)

        return robots

    def safety_factor(self) -> int:
        quadrant_scores = []
        for quadrant_number in range(1, 5):
            robots_in_quadrant = self.robots_in_quadrant(quadrant_number)
            quadrant_scores.append(len(robots_in_quadrant))

        safety_factor = 1
        for score in quadrant_scores:
            safety_factor *= score

        return safety_factor

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


def create_robot(string: str) -> Robot:
    pos_sting, vel_string = string.split(" ")
    pos_x, pos_y = pos_sting[2:].split(",")
    vel_x, vel_y = vel_string[2:].split(",")
    return Robot(Location(int(pos_x), int(pos_y)), Location(int(vel_x), int(vel_y)))


def create_grid(data: typing.Iterator[str], width: int, height: int) -> Grid:
    grid = Grid(width - 1, height - 1)
    for line in data:
        robot = create_robot(line)
        grid.add_robot(robot)

    return grid


@enum.unique
class LocationDirection(enum.Enum):
    UP = Location(0, -1)
    RIGHT = Location(1, 0)
    DOWN = Location(0, 1)
    LEFT = Location(-1, 0)


@dataclasses.dataclass
class Region:
    grid: Grid
    grid_locations: list[GridLocation] = dataclasses.field(default_factory=list)

    @property
    def area(self) -> int:
        return len(self.grid_locations)

    def find_grid_locations(self, start_location: Location) -> None:
        grid_location = self.grid.get_grid_location(start_location)
        self.grid_locations.append(grid_location)
        queue = collections.deque([grid_location])
        while queue:
            grid_location = queue.popleft()
            location = grid_location.location
            for location_direction in LocationDirection:
                neighbour_location = location.neighbour_location(location_direction)
                neighbour_grid_location = self.grid.get_grid_location(
                    neighbour_location
                )
                if neighbour_grid_location in self.grid_locations:
                    continue
                if neighbour_grid_location.location_type == LocationType.ROBOT:
                    self.grid_locations.append(neighbour_grid_location)
                    queue.append(neighbour_grid_location)


def find_large_region(grid: Grid, size: int = 10) -> int:
    largest_region_found = 0
    for grid_location in grid.grid_locations.values():
        region = Region(grid)
        region.find_grid_locations(grid_location.location)
        largest_region_found = max(largest_region_found, region.area)

    return largest_region_found


def part_one() -> int:
    data = yield_data(FILENAME)
    grid = create_grid(data, 101, 103)
    for _ in range(100):
        grid.move_robots()
    return grid.safety_factor()


def part_two() -> int:
    data = yield_data(FILENAME)
    grid = create_grid(data, 101, 103)
    max_region_found = 0
    for index in range(10000):
        grid.move_robots()
        max_region_found = max(max_region_found, find_large_region(grid, 20))
        print(f"{index}: {max_region_found=}")
        if max_region_found > 16:
            print(f"Found Christmas Tree {index}")
            print(grid)
            return index + 1  # off by 1 for some reason
    print(grid)
    return 0


def main() -> None:
    print(f"Part one: {part_one()}")
    print(f"Part two: {part_two()}")
    return None


if __name__ == "__main__":
    main()
